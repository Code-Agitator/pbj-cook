import asyncio
import json
import mimetypes
import os
import secrets
import shutil
import time
import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.responses import FileResponse

from .database import BASE_DIR, UPLOAD_DIR, db, init_db, json_load, rows
from .ingredients import aggregate_ingredients
from .security import hash_pin, verify_pin
from .seed import seed_dev_data
from .ingredients_seed import seed_ingredients

TZ = ZoneInfo(os.getenv("DACOOK_TIMEZONE", "Asia/Shanghai"))
NOW = lambda: int(time.time())
uid = lambda: str(uuid.uuid4())


def setting(conn, key, default=""):
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(conn, key, value):
    conn.execute(
        "INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )


def clean_user(row):
    data = dict(row)
    data.pop("password_hash", None)
    data["is_admin"] = bool(data.get("is_admin"))
    return data


def family_settings(conn):
    return {
        "family_name": setting(conn, "familyName", "我家"),
        "registration_open": setting(conn, "registrationOpen", "1") == "1",
        "has_join_code": bool(setting(conn, "joinCode", "")),
        "timezone": str(TZ),
    }


def make_session(conn, user_id):
    token = secrets.token_urlsafe(36)
    now = NOW()
    conn.execute("DELETE FROM sessions WHERE expires_at < ?", (now,))
    conn.execute(
        "INSERT INTO sessions(token,user_id,expires_at,created_at) VALUES(?,?,?,?)",
        (token, user_id, now + 60 * 60 * 24 * 30, now),
    )
    return token


def current_user(authorization: str | None = None):
    from fastapi import Header


async def require_user(authorization: str | None = Depends(lambda: None)):
    return authorization


async def auth_user(authorization: str | None = None):
    # FastAPI injects this through auth_dependency below.
    raise RuntimeError


from fastapi import Header


def auth_dependency(authorization: str | None = Header(default=None)):
    token = authorization.removeprefix("Bearer ").strip() if authorization else ""
    if not token:
        raise HTTPException(401, "请先登录")
    with db() as conn:
        row = conn.execute(
            "SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=? AND s.expires_at>?",
            (token, NOW()),
        ).fetchone()
        if not row:
            raise HTTPException(401, "登录已失效")
        return clean_user(row)


def admin_dependency(me=Depends(auth_dependency)):
    if not me["is_admin"]:
        raise HTTPException(403, "仅管理员可操作")
    return me


class SetupIn(BaseModel):
    family_name: str = Field(max_length=20)
    name: str = Field(min_length=1, max_length=12)
    pin: str = Field(pattern=r"^\d{6}$")


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=12)
    pin: str = Field(pattern=r"^\d{6}$")
    join_code: str = ""


class LoginIn(BaseModel):
    name: str
    pin: str


class DishIn(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    description: str = Field(default="", max_length=300)
    image_path: str | None = None
    tags: list[str] = []
    cuisine_id: str | None = None
    source_url: str = ""
    ingredients: list[dict] = []
    steps: list[str] = []


class MealIn(BaseModel):
    meal_type: Literal["breakfast", "lunch", "dinner"]
    date: str
    dining_time: str
    deadline: str
    title: str = ""


class ReviewIn(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=200)


class FamilyIn(BaseModel):
    family_name: str = Field(min_length=1, max_length=20)
    registration_open: bool
    join_code: str = ""


class ScheduleIn(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    meal_type: Literal["breakfast", "lunch", "dinner"]
    enabled: bool = True
    dining_time: str
    create_lead_hours: int = Field(ge=0, le=72)
    deadline_lead_minutes: int = Field(ge=0, le=1440)
    weekdays: list[int]


def parse_local(day: str, clock: str):
    try:
        return int(datetime.strptime(f"{day} {clock}", "%Y-%m-%d %H:%M").replace(tzinfo=TZ).timestamp())
    except ValueError:
        raise HTTPException(422, "日期或时间格式不正确")


def seed_defaults(conn):
    now = NOW()
    defaults = [
        ("每日午餐", "lunch", "12:00", 16, 120),
        ("每日晚餐", "dinner", "18:30", 10, 120),
    ]
    for name, meal_type, dining, lead, deadline in defaults:
        conn.execute(
            "INSERT INTO meal_schedules VALUES(?,?,?,?,?,?,?,?,?)",
            (uid(), name, meal_type, 1, dining, lead, deadline, json.dumps(list(range(7))), now),
        )
    seed_ingredients(conn, now)


def tick_schedules():
    now_dt = datetime.now(TZ)
    now = int(now_dt.timestamp())
    result = {"created": 0, "started": 0, "finished": 0}
    with db() as conn:
        schedules = conn.execute("SELECT * FROM meal_schedules WHERE enabled=1").fetchall()
        for s in schedules:
            for offset in range(0, 4):
                target = (now_dt + timedelta(days=offset)).date()
                js_weekday = (target.weekday() + 1) % 7
                if js_weekday not in json_load(s["weekdays"], []):
                    continue
                dining = datetime.strptime(f"{target} {s['dining_time']}", "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
                create_at = dining - timedelta(hours=s["create_lead_hours"])
                if now_dt >= create_at:
                    try:
                        conn.execute(
                            "INSERT INTO meals(id,title,meal_type,date,dining_time,order_deadline,status,is_auto,schedule_id,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                            (uid(), s["name"], s["meal_type"], str(target), int(dining.timestamp()), int((dining-timedelta(minutes=s["deadline_lead_minutes"])).timestamp()), "ordering", 1, s["id"], now),
                        )
                        result["created"] += 1
                    except Exception:
                        pass
        result["started"] = conn.execute("UPDATE meals SET status='cooking' WHERE status='ordering' AND order_deadline<=?", (now,)).rowcount
        result["finished"] = conn.execute("UPDATE meals SET status='done' WHERE status='cooking' AND dining_time+7200<=?", (now,)).rowcount
    return result


async def scheduler_loop():
    while True:
        try:
            tick_schedules()
        except Exception:
            pass
        await asyncio.sleep(60)


SEED_DEV = os.getenv("DACOOK_SEED_DEV", "") == "1"


@asynccontextmanager
async def lifespan(app):
    init_db()
    if SEED_DEV:
        with db() as conn:
            summary = seed_dev_data(conn, NOW())
            print(f"[seed] Dev test data initialized: {summary}")
    # 每次启动时确保默认食材数据已就绪（跳过已存在项）
    with db() as conn:
        result = seed_ingredients(conn)
        if result["inserted"] > 0:
            print(f"[seed] Default ingredients initialized: {result}")
    task = asyncio.create_task(scheduler_loop())
    try:
        yield
    except asyncio.CancelledError:
        # 正常关闭时忽略取消信号
        pass
    finally:
        task.cancel()


app = FastAPI(title="DaCook API", version="1.0.0", lifespan=lifespan)
origins = [x.strip() for x in os.getenv("DACOOK_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
FRONTEND_DIR = Path(os.getenv("DACOOK_FRONTEND_DIR", str(BASE_DIR.parent / "frontend" / "dist" / "build" / "h5")))


@app.get("/api/health")
def health():
    return {"ok": True, "time": NOW()}


@app.get("/api/bootstrap")
def bootstrap():
    with db() as conn:
        members = conn.execute("SELECT id,name,avatar_path,is_admin FROM users ORDER BY created_at").fetchall()
        return {"setup_needed": not members, "settings": family_settings(conn), "members": [clean_user(x) for x in members]}


@app.post("/api/auth/setup")
def setup(payload: SetupIn):
    with db() as conn:
        if conn.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            raise HTTPException(409, "家庭已创建")
        user_id = uid()
        conn.execute("INSERT INTO users VALUES(?,?,?,?,?,?)", (user_id, payload.name.strip(), hash_pin(payload.pin), None, 1, NOW()))
        set_setting(conn, "familyName", payload.family_name.strip() or "我家")
        set_setting(conn, "registrationOpen", "1")
        seed_defaults(conn)
        return {"token": make_session(conn, user_id), "user": clean_user(conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone())}


@app.post("/api/auth/register")
def register(payload: RegisterIn):
    with db() as conn:
        if setting(conn, "registrationOpen", "1") != "1":
            raise HTTPException(403, "家庭已关闭注册")
        if setting(conn, "joinCode", "") and payload.join_code.strip() != setting(conn, "joinCode"):
            raise HTTPException(403, "注册口令不正确")
        if conn.execute("SELECT 1 FROM users WHERE name=?", (payload.name.strip(),)).fetchone():
            raise HTTPException(409, "昵称已存在")
        user_id = uid()
        conn.execute("INSERT INTO users VALUES(?,?,?,?,?,?)", (user_id, payload.name.strip(), hash_pin(payload.pin), None, 0, NOW()))
        return {"token": make_session(conn, user_id), "user": clean_user(conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone())}


@app.post("/api/auth/login")
def login(payload: LoginIn):
    with db() as conn:
        row = conn.execute("SELECT * FROM users WHERE name=?", (payload.name.strip(),)).fetchone()
        if not row or not verify_pin(payload.pin, row["password_hash"]):
            raise HTTPException(401, "昵称或密码不正确")
        return {"token": make_session(conn, row["id"]), "user": clean_user(row)}


@app.post("/api/auth/logout")
def logout(authorization: str | None = Header(default=None)):
    token = authorization.removeprefix("Bearer ").strip() if authorization else ""
    with db() as conn:
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))
    return {"ok": True}


@app.get("/api/me")
def me(user=Depends(auth_dependency)):
    return user


@app.put("/api/me/profile")
def update_profile(payload: dict, me=Depends(auth_dependency)):
    name = str(payload.get("name", "")).strip()
    if not name or len(name) > 12:
        raise HTTPException(422, "昵称需为 1-12 个字符")
    with db() as conn:
        conflict = conn.execute("SELECT id FROM users WHERE name=? AND id<>?", (name, me["id"])).fetchone()
        if conflict:
            raise HTTPException(409, "昵称已存在")
        conn.execute("UPDATE users SET name=?,avatar_path=COALESCE(?,avatar_path) WHERE id=?", (name, payload.get("avatar_path"), me["id"]))
    return {"ok": True}


@app.put("/api/me/pin")
def change_pin(payload: dict, me=Depends(auth_dependency)):
    old_pin, new_pin = str(payload.get("old_pin", "")), str(payload.get("new_pin", ""))
    if len(new_pin) != 6 or not new_pin.isdigit():
        raise HTTPException(422, "新密码必须是 6 位数字")
    with db() as conn:
        row = conn.execute("SELECT password_hash FROM users WHERE id=?", (me["id"],)).fetchone()
        if not verify_pin(old_pin, row["password_hash"]):
            raise HTTPException(403, "原密码不正确")
        conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_pin(new_pin), me["id"]))
    return {"ok": True}


@app.post("/api/uploads")
def upload(file: UploadFile = File(...), me=Depends(auth_dependency)):
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(415, "只能上传图片")
    suffix = mimetypes.guess_extension(file.content_type or "") or ".jpg"
    name = f"{uid()}{suffix}"
    target = UPLOAD_DIR / name
    with target.open("wb") as output:
        shutil.copyfileobj(file.file, output)
    if target.stat().st_size > 5 * 1024 * 1024:
        target.unlink(missing_ok=True)
        raise HTTPException(413, "图片不能超过 5MB")
    return {"path": name, "url": f"/uploads/{name}"}


def dish_detail(conn, dish_id):
    row = conn.execute("SELECT d.*,c.name cuisine_name,c.emoji cuisine_emoji FROM dishes d LEFT JOIN dish_cuisines c ON c.id=d.cuisine_id WHERE d.id=?", (dish_id,)).fetchone()
    if not row:
        raise HTTPException(404, "菜品不存在")
    data = dict(row)
    data["tags"] = json_load(data["tags"], [])
    data["ingredients"] = rows(conn.execute("SELECT * FROM dish_ingredients WHERE dish_id=? ORDER BY ord", (dish_id,)).fetchall())
    data["steps"] = rows(conn.execute("SELECT * FROM dish_steps WHERE dish_id=? ORDER BY ord", (dish_id,)).fetchall())
    return data


@app.get("/api/cuisines")
def cuisines(me=Depends(auth_dependency)):
    with db() as conn:
        return rows(conn.execute("SELECT * FROM dish_cuisines ORDER BY ord,name").fetchall())


@app.post("/api/cuisines")
def create_cuisine(payload: dict, me=Depends(admin_dependency)):
    name = str(payload.get("name", "")).strip()
    if not name:
        raise HTTPException(422, "请填写菜系名称")
    with db() as conn:
        cuisine_id = uid()
        try:
            conn.execute("INSERT INTO dish_cuisines VALUES(?,?,?,?,?)", (cuisine_id, name[:12], str(payload.get("emoji", ""))[:4], 0, NOW()))
        except Exception:
            raise HTTPException(409, "菜系名称已存在")
        return {"id": cuisine_id}


@app.delete("/api/cuisines/{cuisine_id}")
def delete_cuisine(cuisine_id: str, me=Depends(admin_dependency)):
    with db() as conn:
        if conn.execute("SELECT 1 FROM dishes WHERE cuisine_id=?", (cuisine_id,)).fetchone():
            raise HTTPException(409, "该菜系仍有菜品，不能删除")
        conn.execute("DELETE FROM dish_cuisines WHERE id=?", (cuisine_id,))
    return {"ok": True}


@app.get("/api/dishes")
def list_dishes(status: str = "active", q: str = "", cuisine_id: str | None = None, me=Depends(auth_dependency)):
    sql = "SELECT d.*,c.name cuisine_name,c.emoji cuisine_emoji FROM dishes d LEFT JOIN dish_cuisines c ON c.id=d.cuisine_id WHERE d.status=?"
    params = [status]
    if q:
        sql += " AND (d.name LIKE ? OR d.description LIKE ? OR d.tags LIKE ?)"
        params += [f"%{q}%"] * 3
    if cuisine_id:
        sql += " AND d.cuisine_id=?"
        params.append(cuisine_id)
    sql += " ORDER BY d.created_at DESC"
    with db() as conn:
        data = rows(conn.execute(sql, params).fetchall())
        for item in data:
            item["tags"] = json_load(item["tags"], [])
        return data


@app.get("/api/dishes/{dish_id}")
def get_dish(dish_id: str, me=Depends(auth_dependency)):
    with db() as conn:
        return dish_detail(conn, dish_id)


def save_dish_children(conn, dish_id, payload):
    conn.execute("DELETE FROM dish_ingredients WHERE dish_id=?", (dish_id,))
    conn.execute("DELETE FROM dish_steps WHERE dish_id=?", (dish_id,))
    for index, item in enumerate(payload.ingredients[:30]):
        name = str(item.get("name", "")).strip()
        if name:
            conn.execute("INSERT INTO dish_ingredients VALUES(?,?,?,?,?,?)", (uid(), dish_id, name[:30], str(item.get("quantity", ""))[:20], str(item.get("unit", ""))[:12], index))
    for index, body in enumerate(payload.steps[:20]):
        if body.strip():
            conn.execute("INSERT INTO dish_steps VALUES(?,?,?,?)", (uid(), dish_id, index, body.strip()[:500]))


@app.post("/api/dishes")
def create_dish(payload: DishIn, me=Depends(auth_dependency)):
    dish_id = uid()
    with db() as conn:
        conn.execute("INSERT INTO dishes VALUES(?,?,?,?,?,?,?,?,?,?)", (dish_id, payload.name.strip(), payload.description.strip(), payload.image_path, json.dumps(payload.tags, ensure_ascii=False), payload.cuisine_id, payload.source_url.strip(), "active", me["id"], NOW()))
        save_dish_children(conn, dish_id, payload)
        return dish_detail(conn, dish_id)


@app.put("/api/dishes/{dish_id}")
def update_dish(dish_id: str, payload: DishIn, me=Depends(auth_dependency)):
    with db() as conn:
        old = conn.execute("SELECT * FROM dishes WHERE id=?", (dish_id,)).fetchone()
        if not old:
            raise HTTPException(404, "菜品不存在")
        if old["created_by"] != me["id"] and not me["is_admin"]:
            raise HTTPException(403, "只能编辑自己创建的菜品")
        conn.execute("UPDATE dishes SET name=?,description=?,image_path=?,tags=?,cuisine_id=?,source_url=? WHERE id=?", (payload.name.strip(), payload.description.strip(), payload.image_path, json.dumps(payload.tags, ensure_ascii=False), payload.cuisine_id, payload.source_url.strip(), dish_id))
        save_dish_children(conn, dish_id, payload)
        return dish_detail(conn, dish_id)


@app.patch("/api/dishes/{dish_id}/status")
def dish_status(dish_id: str, payload: dict, me=Depends(auth_dependency)):
    status = payload.get("status")
    if status not in ("active", "archived"):
        raise HTTPException(422, "状态不正确")
    with db() as conn:
        dish = conn.execute("SELECT * FROM dishes WHERE id=?", (dish_id,)).fetchone()
        if not dish:
            raise HTTPException(404, "菜品不存在")
        if dish["created_by"] != me["id"] and not me["is_admin"]:
            raise HTTPException(403, "无权操作")
        conn.execute("UPDATE dishes SET status=? WHERE id=?", (status, dish_id))
    return {"ok": True}


@app.delete("/api/dishes/{dish_id}")
def delete_dish(dish_id: str, me=Depends(auth_dependency)):
    with db() as conn:
        dish = conn.execute("SELECT * FROM dishes WHERE id=?", (dish_id,)).fetchone()
        if not dish:
            raise HTTPException(404, "菜品不存在")
        if dish["created_by"] != me["id"] and not me["is_admin"]:
            raise HTTPException(403, "无权操作")
        conn.execute("DELETE FROM dishes WHERE id=?", (dish_id,))
    return {"ok": True}


# ============================================================
# 食材统一管理
# ============================================================

def _ingredient_with_aliases(conn, row):
    """将 ingredient_canonical 行与它的别名合并输出。"""
    data = dict(row)
    data["aliases"] = [
        dict(a) for a in conn.execute(
            "SELECT id, alias FROM ingredient_aliases WHERE canonical_id=? ORDER BY created_at",
            (row["id"],)
        ).fetchall()
    ]
    data["alias_names"] = [a["alias"] for a in data["aliases"]]
    return data


def _search_ingredients(conn, keyword, offset=0, limit=None):
    """按标准名或别名搜索食材。"""
    kw = f"%{keyword}%"
    limit_clause = ""
    params = [kw, kw]
    if limit is not None:
        limit_clause = " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    rows = conn.execute(
        f"""
        SELECT DISTINCT c.* FROM ingredient_canonical c
        LEFT JOIN ingredient_aliases a ON a.canonical_id = c.id
        WHERE c.name LIKE ? OR a.alias LIKE ?
        ORDER BY c.name{limit_clause}
        """,
        params,
    ).fetchall()
    return [_ingredient_with_aliases(conn, r) for r in rows]


def _count_ingredients(conn, keyword=None):
    """统计食材总数或搜索结果数。"""
    if keyword:
        kw = f"%{keyword}%"
        return conn.execute(
            """
            SELECT COUNT(DISTINCT c.id) FROM ingredient_canonical c
            LEFT JOIN ingredient_aliases a ON a.canonical_id = c.id
            WHERE c.name LIKE ? OR a.alias LIKE ?
            """,
            (kw, kw),
        ).fetchone()[0]
    return conn.execute("SELECT COUNT(*) FROM ingredient_canonical").fetchone()[0]


@app.get("/api/ingredients")
def ingredient_list(
    q: str = "",
    page: int = 1,
    page_size: int = 50,
    me=Depends(admin_dependency),
):
    """获取食材列表，支持分页和搜索。

    返回格式: { items: [...], total: N, page: N, page_size: N }
    """
    with db() as conn:
        page = max(1, page)
        page_size = min(max(1, page_size), 200)
        offset = (page - 1) * page_size
        keyword = q.strip()

        if keyword:
            total = _count_ingredients(conn, keyword)
            items = _search_ingredients(conn, keyword, offset, page_size)
        else:
            total = _count_ingredients(conn)
            rows = conn.execute(
                "SELECT * FROM ingredient_canonical ORDER BY name LIMIT ? OFFSET ?",
                (page_size, offset),
            ).fetchall()
            items = [_ingredient_with_aliases(conn, r) for r in rows]

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }


@app.get("/api/ingredients/{ingredient_id}")
def ingredient_get(ingredient_id: str, me=Depends(admin_dependency)):
    with db() as conn:
        row = conn.execute("SELECT * FROM ingredient_canonical WHERE id=?", (ingredient_id,)).fetchone()
        if not row:
            raise HTTPException(404, "食材不存在")
        return _ingredient_with_aliases(conn, row)


@app.post("/api/ingredients")
def ingredient_create(payload: dict, me=Depends(admin_dependency)):
    name = str(payload.get("name", "")).strip()
    if not name:
        raise HTTPException(422, "请填写食材名称")
    aliases = payload.get("aliases") or []
    if not isinstance(aliases, list):
        raise HTTPException(422, "别名格式不正确")
    clean_aliases = [a.strip() for a in aliases if isinstance(a, str) and a.strip() and a.strip() != name]
    clean_aliases = list(dict.fromkeys(clean_aliases))[:20]  # 去重并限制数量
    with db() as conn:
        # 检查名称是否已存在（标准名或别名）
        existing = conn.execute(
            "SELECT c.id, c.name FROM ingredient_canonical c WHERE c.name = ? UNION ALL SELECT c.id, c.name FROM ingredient_aliases a JOIN ingredient_canonical c ON c.id = a.canonical_id WHERE a.alias = ?",
            (name, name),
        ).fetchone()
        if existing:
            raise HTTPException(409, f"食材名称已存在（{existing['name']}）")
        ingredient_id = uid()
        conn.execute(
            "INSERT INTO ingredient_canonical(id, name, created_at) VALUES(?, ?, ?)",
            (ingredient_id, name, NOW()),
        )
        for a in clean_aliases:
            conn.execute(
                "INSERT INTO ingredient_aliases(id, canonical_id, alias, created_at) VALUES(?, ?, ?, ?)",
                (uid(), ingredient_id, a, NOW()),
            )
        return _ingredient_with_aliases(conn, conn.execute("SELECT * FROM ingredient_canonical WHERE id=?", (ingredient_id,)).fetchone())


@app.put("/api/ingredients/{ingredient_id}")
def ingredient_update(ingredient_id: str, payload: dict, me=Depends(admin_dependency)):
    name = str(payload.get("name", "")).strip()
    if not name:
        raise HTTPException(422, "请填写食材名称")
    aliases = payload.get("aliases") or []
    if not isinstance(aliases, list):
        raise HTTPException(422, "别名格式不正确")
    clean_aliases = [a.strip() for a in aliases if isinstance(a, str) and a.strip() and a.strip() != name]
    clean_aliases = list(dict.fromkeys(clean_aliases))[:20]
    with db() as conn:
        row = conn.execute("SELECT * FROM ingredient_canonical WHERE id=?", (ingredient_id,)).fetchone()
        if not row:
            raise HTTPException(404, "食材不存在")
        if name != row["name"]:
            existing = conn.execute(
                "SELECT c.id FROM ingredient_canonical c WHERE c.name = ? AND c.id != ? UNION ALL SELECT c.id FROM ingredient_aliases a JOIN ingredient_canonical c ON c.id = a.canonical_id WHERE a.alias = ? AND c.id != ?",
                (name, ingredient_id, name, ingredient_id),
            ).fetchone()
            if existing:
                raise HTTPException(409, "食材名称已存在")
        conn.execute("UPDATE ingredient_canonical SET name=? WHERE id=?", (name, ingredient_id))
        # 重新设置别名：删旧增新
        conn.execute("DELETE FROM ingredient_aliases WHERE canonical_id=?", (ingredient_id,))
        for a in clean_aliases:
            conn.execute(
                "INSERT INTO ingredient_aliases(id, canonical_id, alias, created_at) VALUES(?, ?, ?, ?)",
                (uid(), ingredient_id, a, NOW()),
            )
        return _ingredient_with_aliases(conn, conn.execute("SELECT * FROM ingredient_canonical WHERE id=?", (ingredient_id,)).fetchone())


@app.delete("/api/ingredients/{ingredient_id}")
def ingredient_delete(ingredient_id: str, me=Depends(admin_dependency)):
    with db() as conn:
        row = conn.execute("SELECT * FROM ingredient_canonical WHERE id=?", (ingredient_id,)).fetchone()
        if not row:
            raise HTTPException(404, "食材不存在")
        conn.execute("DELETE FROM ingredient_canonical WHERE id=?", (ingredient_id,))
    return {"ok": True}


@app.post("/api/ingredients/{ingredient_id}/merge")
def ingredient_merge(ingredient_id: str, payload: dict, me=Depends(admin_dependency)):
    """将其他食材的别名合并到目标食材中，然后删除源食材。"""
    source_id = str(payload.get("source_id", "")).strip()
    if not source_id:
        raise HTTPException(422, "请选择要合并的源食材")
    if source_id == ingredient_id:
        raise HTTPException(422, "不能合并自身")
    with db() as conn:
        target = conn.execute("SELECT * FROM ingredient_canonical WHERE id=?", (ingredient_id,)).fetchone()
        if not target:
            raise HTTPException(404, "目标食材不存在")
        source = conn.execute("SELECT * FROM ingredient_canonical WHERE id=?", (source_id,)).fetchone()
        if not source:
            raise HTTPException(404, "源食材不存在")
        # 把源的所有别名转移到目标
        source_aliases = conn.execute("SELECT alias FROM ingredient_aliases WHERE canonical_id=?", (source_id,)).fetchall()
        for a in source_aliases:
            existing = conn.execute("SELECT id FROM ingredient_aliases WHERE canonical_id=? AND alias=?", (ingredient_id, a["alias"])).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO ingredient_aliases(id, canonical_id, alias, created_at) VALUES(?, ?, ?, ?)",
                    (uid(), ingredient_id, a["alias"], NOW()),
                )
        # 把源的标准名也作为目标的别名
        existing = conn.execute("SELECT id FROM ingredient_aliases WHERE canonical_id=? AND alias=?", (ingredient_id, source["name"])).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO ingredient_aliases(id, canonical_id, alias, created_at) VALUES(?, ?, ?, ?)",
                (uid(), ingredient_id, source["name"], NOW()),
            )
        # 删除源
        conn.execute("DELETE FROM ingredient_canonical WHERE id=?", (source_id,))
        return _ingredient_with_aliases(conn, target)


def meal_summary(conn, row):
    data = dict(row)
    cook = conn.execute("SELECT id,name,avatar_path FROM users WHERE id=?", (data.get("cook_id"),)).fetchone() if data.get("cook_id") else None
    data["cook"] = dict(cook) if cook else None
    data["participant_count"] = conn.execute("SELECT COUNT(DISTINCT user_id) n FROM orders WHERE meal_id=?", (data["id"],)).fetchone()["n"]
    data["is_auto"] = bool(data["is_auto"])
    return data


@app.get("/api/meals")
def list_meals(scope: str = "all", me=Depends(auth_dependency)):
    with db() as conn:
        result = []
        for row in conn.execute("SELECT * FROM meals ORDER BY dining_time DESC").fetchall():
            result.append(meal_summary(conn, row))
        return result


@app.post("/api/meals")
def create_meal(payload: MealIn, me=Depends(auth_dependency)):
    meal_id = uid()
    dining = parse_local(payload.date, payload.dining_time)
    deadline = parse_local(payload.date, payload.deadline)
    with db() as conn:
        conn.execute("INSERT INTO meals(id,title,meal_type,date,dining_time,order_deadline,status,is_auto,created_by,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)", (meal_id, payload.title.strip()[:30] or None, payload.meal_type, payload.date, dining, deadline, "ordering", 0, me["id"], NOW()))
        return {"id": meal_id}


@app.get("/api/meals/{meal_id}")
def get_meal(meal_id: str, me=Depends(auth_dependency)):
    with db() as conn:
        meal = conn.execute("SELECT * FROM meals WHERE id=?", (meal_id,)).fetchone()
        if not meal:
            raise HTTPException(404, "饭局不存在")
        data = meal_summary(conn, meal)
        data["orders"] = rows(conn.execute("SELECT o.*,u.name user_name,u.avatar_path user_avatar,d.name dish_name,d.image_path dish_image FROM orders o JOIN users u ON u.id=o.user_id JOIN dishes d ON d.id=o.dish_id WHERE o.meal_id=? ORDER BY o.created_at", (meal_id,)).fetchall())
        data["reviews"] = rows(conn.execute("SELECT r.*,u.name user_name,u.avatar_path user_avatar FROM reviews r JOIN users u ON u.id=r.user_id WHERE r.meal_id=? ORDER BY r.created_at", (meal_id,)).fetchall())
        data["skipped_dish_ids"] = [x["dish_id"] for x in conn.execute("SELECT dish_id FROM meal_dish_skips WHERE meal_id=?", (meal_id,)).fetchall()]
        data["my_ordered_dish_ids"] = [x["dish_id"] for x in conn.execute("SELECT dish_id FROM orders WHERE meal_id=? AND user_id=?", (meal_id, me["id"])).fetchall()]
        return data


@app.get("/api/meals/{meal_id}/ingredient-list")
def meal_ingredient_list(meal_id: str):
    with db() as conn:
        meal = conn.execute("SELECT id FROM meals WHERE id=?", (meal_id,)).fetchone()
        if not meal:
            raise HTTPException(404, "饭局不存在")
        ingredient_rows = rows(conn.execute(
            """
            SELECT i.name,i.quantity,i.unit
            FROM dish_ingredients i
            JOIN (
              SELECT DISTINCT o.dish_id FROM orders o
              WHERE o.meal_id=? AND NOT EXISTS (
                SELECT 1 FROM meal_dish_skips s
                WHERE s.meal_id=o.meal_id AND s.dish_id=o.dish_id
              )
            ) picked ON picked.dish_id=i.dish_id
            ORDER BY i.name,i.unit,i.ord
            """,
            (meal_id,),
        ).fetchall())
        return {"meal_id": meal_id, "items": aggregate_ingredients(ingredient_rows)}


@app.post("/api/meals/{meal_id}/cook")
def toggle_cook(meal_id: str, me=Depends(auth_dependency)):
    with db() as conn:
        meal = conn.execute("SELECT * FROM meals WHERE id=?", (meal_id,)).fetchone()
        if not meal:
            raise HTTPException(404, "饭局不存在")
        if meal["status"] not in ("ordering", "cooking"):
            raise HTTPException(409, "当前状态不能认领掌勺")
        if meal["cook_id"] == me["id"]:
            conn.execute("UPDATE meals SET cook_id=? WHERE id=?", (None, meal_id))
        elif meal["cook_id"] is None:
            conn.execute("UPDATE meals SET cook_id=? WHERE id=?", (me["id"], meal_id))
        else:
            raise HTTPException(409, "已有主厨，需等当前主厨退出后才能认领")
    return {"ok": True}


@app.post("/api/meals/{meal_id}/orders/{dish_id}")
def toggle_order(meal_id: str, dish_id: str, me=Depends(auth_dependency)):
    with db() as conn:
        meal = conn.execute("SELECT * FROM meals WHERE id=?", (meal_id,)).fetchone()
        if not meal or meal["status"] != "ordering" or NOW() >= meal["order_deadline"]:
            raise HTTPException(409, "点菜已结束")
        old = conn.execute("SELECT id FROM orders WHERE meal_id=? AND dish_id=? AND user_id=?", (meal_id, dish_id, me["id"])).fetchone()
        if old:
            conn.execute("DELETE FROM orders WHERE id=?", (old["id"],))
            selected = False
        else:
            conn.execute("INSERT INTO orders VALUES(?,?,?,?,?,?)", (uid(), meal_id, dish_id, me["id"], None, NOW()))
            selected = True
    return {"selected": selected}


@app.post("/api/meals/{meal_id}/skips/{dish_id}")
def toggle_skip(meal_id: str, dish_id: str, me=Depends(auth_dependency)):
    with db() as conn:
        meal = conn.execute("SELECT cook_id FROM meals WHERE id=?", (meal_id,)).fetchone()
        if not meal or meal["cook_id"] != me["id"]:
            raise HTTPException(403, "仅掌勺人可标记不做")
        old = conn.execute("SELECT 1 FROM meal_dish_skips WHERE meal_id=? AND dish_id=?", (meal_id, dish_id)).fetchone()
        if old:
            conn.execute("DELETE FROM meal_dish_skips WHERE meal_id=? AND dish_id=?", (meal_id, dish_id))
        else:
            conn.execute("INSERT INTO meal_dish_skips VALUES(?,?,?,?)", (meal_id, dish_id, me["id"], NOW()))
    return {"skipped": not bool(old)}


@app.patch("/api/meals/{meal_id}/status")
def update_meal_status(meal_id: str, payload: dict, me=Depends(auth_dependency)):
    status = payload.get("status")
    if status not in ("ordering", "cooking", "done", "cancelled"):
        raise HTTPException(422, "状态不正确")
    with db() as conn:
        meal = conn.execute("SELECT * FROM meals WHERE id=?", (meal_id,)).fetchone()
        if not meal:
            raise HTTPException(404, "饭局不存在")
        if status == "cancelled":
            if not me["is_admin"]:
                raise HTTPException(403, "仅管理员可取消饭局")
        elif not me["is_admin"] and me["id"] not in (meal["created_by"], meal["cook_id"]):
            raise HTTPException(403, "仅创建者、掌勺人或管理员可操作")
        allowed = {
            "ordering": {"cooking", "cancelled"},
            "cooking": {"done", "cancelled"},
            "done": set(),
            "cancelled": set(),
        }
        if status not in allowed[meal["status"]]:
            raise HTTPException(409, "当前状态不能执行该操作")
        conn.execute("UPDATE meals SET status=? WHERE id=?", (status, meal_id))
    return {"ok": True}


@app.delete("/api/meals/{meal_id}")
def delete_meal(meal_id: str, me=Depends(auth_dependency)):
    with db() as conn:
        meal = conn.execute("SELECT * FROM meals WHERE id=?", (meal_id,)).fetchone()
        if meal and not me["is_admin"] and meal["created_by"] != me["id"]:
            raise HTTPException(403, "仅创建者或管理员可删除")
        conn.execute("DELETE FROM meals WHERE id=?", (meal_id,))
    return {"ok": True}


@app.put("/api/meals/{meal_id}/review")
def review(meal_id: str, payload: ReviewIn, me=Depends(auth_dependency)):
    with db() as conn:
        meal = conn.execute("SELECT status FROM meals WHERE id=?", (meal_id,)).fetchone()
        if not meal or meal["status"] != "done":
            raise HTTPException(409, "饭局完成后才能评价")
        conn.execute("INSERT INTO reviews VALUES(?,?,?,?,?,?) ON CONFLICT(meal_id,user_id) DO UPDATE SET rating=excluded.rating,comment=excluded.comment", (uid(), meal_id, me["id"], payload.rating, payload.comment.strip(), NOW()))
    return {"ok": True}


@app.get("/api/contributions")
def contributions(me=Depends(auth_dependency)):
    start = date.today() - timedelta(days=111)
    with db() as conn:
        members = []
        for u in conn.execute("SELECT id,name,avatar_path FROM users ORDER BY created_at").fetchall():
            cooks = conn.execute("SELECT date,COUNT(*) n FROM meals WHERE cook_id=? AND status='done' AND date>=? GROUP BY date", (u["id"], str(start))).fetchall()
            orders_by_day = conn.execute("SELECT m.date,COUNT(*) n FROM orders o JOIN meals m ON m.id=o.meal_id WHERE o.user_id=? AND m.date>=? GROUP BY m.date", (u["id"], str(start))).fetchall()
            cook_map, order_map = {x["date"]: x["n"] for x in cooks}, {x["date"]: x["n"] for x in orders_by_day}
            streak, cursor = 0, date.today()
            while cook_map.get(str(cursor), 0) > 0:
                streak += 1
                cursor -= timedelta(days=1)
            members.append({**dict(u), "cook_total": sum(cook_map.values()), "order_total": sum(order_map.values()), "streak": streak, "cook_by_date": cook_map, "order_by_date": order_map})
        return {"today": str(date.today()), "start": str(start), "members": members}


@app.get("/api/admin")
def admin(me=Depends(admin_dependency)):
    with db() as conn:
        schedules = rows(conn.execute("SELECT * FROM meal_schedules ORDER BY created_at").fetchall())
        for item in schedules:
            item["enabled"] = bool(item["enabled"])
            item["weekdays"] = json_load(item["weekdays"], [])
        members = [clean_user(x) for x in conn.execute("SELECT * FROM users ORDER BY created_at").fetchall()]
        result = family_settings(conn)
        result["join_code"] = setting(conn, "joinCode", "")
        return {"settings": result, "schedules": schedules, "members": members}


@app.put("/api/admin/settings")
def update_family(payload: FamilyIn, me=Depends(admin_dependency)):
    with db() as conn:
        set_setting(conn, "familyName", payload.family_name.strip())
        set_setting(conn, "registrationOpen", "1" if payload.registration_open else "0")
        set_setting(conn, "joinCode", payload.join_code.strip())
    return {"ok": True}


@app.post("/api/admin/schedules")
def create_schedule(payload: ScheduleIn, me=Depends(admin_dependency)):
    schedule_id = uid()
    with db() as conn:
        conn.execute("INSERT INTO meal_schedules VALUES(?,?,?,?,?,?,?,?,?)", (schedule_id, payload.name, payload.meal_type, int(payload.enabled), payload.dining_time, payload.create_lead_hours, payload.deadline_lead_minutes, json.dumps(payload.weekdays), NOW()))
    return {"id": schedule_id}


@app.put("/api/admin/schedules/{schedule_id}")
def update_schedule(schedule_id: str, payload: ScheduleIn, me=Depends(admin_dependency)):
    with db() as conn:
        result = conn.execute("UPDATE meal_schedules SET name=?,meal_type=?,enabled=?,dining_time=?,create_lead_hours=?,deadline_lead_minutes=?,weekdays=? WHERE id=?", (payload.name, payload.meal_type, int(payload.enabled), payload.dining_time, payload.create_lead_hours, payload.deadline_lead_minutes, json.dumps(payload.weekdays), schedule_id))
        if result.rowcount == 0:
            raise HTTPException(404, "自动饭局规则不存在")
    return {"ok": True}


@app.delete("/api/admin/schedules/{schedule_id}")
def remove_schedule(schedule_id: str, me=Depends(admin_dependency)):
    with db() as conn:
        result = conn.execute("DELETE FROM meal_schedules WHERE id=?", (schedule_id,))
        if result.rowcount == 0:
            raise HTTPException(404, "自动饭局规则不存在")
    return {"ok": True}


@app.post("/api/admin/tick")
def run_tick(me=Depends(admin_dependency)):
    return tick_schedules()


@app.patch("/api/admin/members/{user_id}")
def member_admin(user_id: str, payload: dict, me=Depends(admin_dependency)):
    if user_id == me["id"] and not payload.get("is_admin"):
        raise HTTPException(409, "不能取消自己的管理员权限")
    with db() as conn:
        conn.execute("UPDATE users SET is_admin=? WHERE id=?", (int(bool(payload.get("is_admin"))), user_id))
    return {"ok": True}


@app.delete("/api/admin/members/{user_id}")
def remove_member(user_id: str, me=Depends(admin_dependency)):
    if user_id == me["id"]:
        raise HTTPException(409, "不能删除自己")
    with db() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    return {"ok": True}


if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="frontend-assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
