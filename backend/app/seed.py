"""Dev-only test data seeding. Triggered when DACOOK_SEED_DEV=1."""
import json
import secrets
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from .security import hash_pin

TZ = ZoneInfo("Asia/Shanghai")

DEV_USERS = [
    {"name": "张三", "pin": "123456", "is_admin": 1},
    {"name": "李四", "pin": "123456", "is_admin": 0},
    {"name": "王五", "pin": "123456", "is_admin": 0},
]

DEV_CUISINES = [
    {"name": "川菜", "emoji": "🌶️", "ord": 0},
    {"name": "粤菜", "emoji": "🥟", "ord": 1},
    {"name": "鲁菜", "emoji": "🍜", "ord": 2},
    {"name": "苏菜", "emoji": "🦀", "ord": 3},
    {"name": "西餐", "emoji": "🍝", "ord": 4},
]

DEV_DISHES = [
    {
        "name": "宫保鸡丁",
        "description": "经典川菜，鸡肉嫩滑，花生酥脆，酸甜微辣",
        "tags": json.dumps(["辣", "经典", "下饭"], ensure_ascii=False),
        "cuisine_name": "川菜",
        "ingredients": [
            {"name": "鸡胸肉", "quantity": "300", "unit": "克"},
            {"name": "花生米", "quantity": "50", "unit": "克"},
            {"name": "干辣椒", "quantity": "10", "unit": "克"},
            {"name": "花椒", "quantity": "5", "unit": "克"},
            {"name": "葱姜蒜", "quantity": "适量", "unit": ""},
        ],
        "steps": [
            "鸡胸肉切丁，加料酒、生抽、淀粉腌制15分钟",
            "花生米炸至金黄盛出备用",
            "热锅凉油，爆香花椒干辣椒",
            "下鸡丁滑炒至变色",
            "调入宫保酱汁，翻炒均匀",
            "最后加入花生米，快速翻炒出锅",
        ],
    },
    {
        "name": "麻婆豆腐",
        "description": "四川名菜，麻辣鲜香，豆腐嫩滑入味",
        "tags": json.dumps(["辣", "麻", "豆腐"], ensure_ascii=False),
        "cuisine_name": "川菜",
        "ingredients": [
            {"name": "嫩豆腐", "quantity": "1", "unit": "块"},
            {"name": "猪肉末", "quantity": "100", "unit": "克"},
            {"name": "豆瓣酱", "quantity": "2", "unit": "勺"},
            {"name": "花椒粉", "quantity": "适量", "unit": ""},
            {"name": "葱", "quantity": "2", "unit": "根"},
        ],
        "steps": [
            "豆腐切小块，焯水去豆腥味",
            "热锅下肉末炒散",
            "加入豆瓣酱炒出红油",
            "加水烧开，放入豆腐小火煮5分钟",
            "勾芡撒花椒粉葱花出锅",
        ],
    },
    {
        "name": "红烧肉",
        "description": "肥而不腻，入口即化，色泽红亮",
        "tags": json.dumps(["甜", "经典", "硬菜"], ensure_ascii=False),
        "cuisine_name": "鲁菜",
        "ingredients": [
            {"name": "五花肉", "quantity": "500", "unit": "克"},
            {"name": "冰糖", "quantity": "30", "unit": "克"},
            {"name": "生抽", "quantity": "3", "unit": "勺"},
            {"name": "老抽", "quantity": "1", "unit": "勺"},
            {"name": "八角", "quantity": "2", "unit": "个"},
            {"name": "桂皮", "quantity": "1", "unit": "小块"},
            {"name": "葱姜", "quantity": "适量", "unit": ""},
        ],
        "steps": [
            "五花肉切方块焯水",
            "小火炒糖色至枣红色",
            "下肉块翻炒上色",
            "加生抽老抽八角桂皮葱姜",
            "加水没过肉，大火烧开转小火炖1小时",
            "大火收汁至浓稠",
        ],
    },
    {
        "name": "西红柿炒鸡蛋",
        "description": "国民家常菜，酸甜可口，营养丰富",
        "tags": json.dumps(["家常", "快手", "酸甜"], ensure_ascii=False),
        "cuisine_name": "鲁菜",
        "ingredients": [
            {"name": "鸡蛋", "quantity": "3", "unit": "个"},
            {"name": "西红柿", "quantity": "2", "unit": "个"},
            {"name": "白糖", "quantity": "1", "unit": "勺"},
            {"name": "盐", "quantity": "适量", "unit": ""},
            {"name": "葱花", "quantity": "少许", "unit": ""},
        ],
        "steps": [
            "鸡蛋打散加少许盐",
            "西红柿切块",
            "热油倒入蛋液炒成块盛出",
            "锅中留底油炒西红柿出汁",
            "加糖调味，倒回鸡蛋翻炒均匀",
        ],
    },
    {
        "name": "清蒸鲈鱼",
        "description": "粤菜经典，鱼肉鲜嫩，清淡健康",
        "tags": json.dumps(["清淡", "海鲜", "健康"], ensure_ascii=False),
        "cuisine_name": "粤菜",
        "ingredients": [
            {"name": "鲈鱼", "quantity": "1", "unit": "条"},
            {"name": "葱", "quantity": "3", "unit": "根"},
            {"name": "姜", "quantity": "1", "unit": "块"},
            {"name": "蒸鱼豉油", "quantity": "3", "unit": "勺"},
            {"name": "料酒", "quantity": "1", "unit": "勺"},
        ],
        "steps": [
            "鲈鱼处理干净，两面划刀",
            "鱼身抹料酒，放姜片腌10分钟",
            "水开后上锅蒸8分钟",
            "取出倒掉蒸出的水",
            "铺葱丝淋蒸鱼豉油",
            "浇热油激香",
        ],
    },
    {
        "name": "糖醋里脊",
        "description": "外酥里嫩，酸甜开胃，老少皆宜",
        "tags": json.dumps(["酸甜", "炸物", "下饭"], ensure_ascii=False),
        "cuisine_name": "鲁菜",
        "ingredients": [
            {"name": "猪里脊", "quantity": "300", "unit": "克"},
            {"name": "番茄酱", "quantity": "3", "unit": "勺"},
            {"name": "白醋", "quantity": "2", "unit": "勺"},
            {"name": "白糖", "quantity": "3", "unit": "勺"},
            {"name": "淀粉", "quantity": "100", "unit": "克"},
        ],
        "steps": [
            "里脊切条加盐料酒腌制",
            "裹上干淀粉",
            "油温六成热炸至金黄捞出",
            "复炸一次更酥脆",
            "锅中调糖醋汁烧开勾芡",
            "下里脊快速翻炒裹匀出锅",
        ],
    },
    {
        "name": "蛋炒饭",
        "description": "简单美味，粒粒分明，蛋香四溢",
        "tags": json.dumps(["主食", "快手", "家常"], ensure_ascii=False),
        "cuisine_name": "粤菜",
        "ingredients": [
            {"name": "隔夜米饭", "quantity": "2", "unit": "碗"},
            {"name": "鸡蛋", "quantity": "3", "unit": "个"},
            {"name": "葱花", "quantity": "适量", "unit": ""},
            {"name": "盐", "quantity": "适量", "unit": ""},
        ],
        "steps": [
            "鸡蛋打散，米饭拨散",
            "热油倒入蛋液，半凝固时加入米饭",
            "大火翻炒至粒粒分明",
            "加盐调味撒葱花出锅",
        ],
    },
    {
        "name": "意大利肉酱面",
        "description": "经典西餐，肉酱浓郁，面条劲道",
        "tags": json.dumps(["西餐", "面食", "浓郁"], ensure_ascii=False),
        "cuisine_name": "西餐",
        "ingredients": [
            {"name": "意大利面", "quantity": "200", "unit": "克"},
            {"name": "牛肉末", "quantity": "150", "unit": "克"},
            {"name": "番茄酱", "quantity": "100", "unit": "克"},
            {"name": "洋葱", "quantity": "半个", "unit": ""},
            {"name": "大蒜", "quantity": "3", "unit": "瓣"},
            {"name": "黑胡椒", "quantity": "适量", "unit": ""},
        ],
        "steps": [
            "意面按包装说明煮好捞出",
            "洋葱大蒜切碎末",
            "热锅炒香洋葱蒜末",
            "下牛肉末炒散",
            "加番茄酱炖煮10分钟",
            "拌入意面撒黑胡椒",
        ],
    },
]


def seed_dev_data(conn, now: int):
    """Insert test users, cuisines, dishes, and a few sample meals.

    Idempotent: checks existing data before inserting.
    Returns a summary dict of what was created.
    """
    summary = {"users": 0, "cuisines": 0, "dishes": 0, "meals": 0}

    # --- Users ---
    existing_users = {row["name"] for row in conn.execute("SELECT name FROM users").fetchall()}
    user_id_map = {}
    for u in DEV_USERS:
        if u["name"] not in existing_users:
            uid = secrets.token_urlsafe(12)
            conn.execute(
                "INSERT INTO users VALUES(?,?,?,?,?,?)",
                (uid, u["name"], hash_pin(u["pin"]), None, u["is_admin"], now),
            )
            user_id_map[u["name"]] = uid
            summary["users"] += 1
        else:
            row = conn.execute("SELECT id FROM users WHERE name=?", (u["name"],)).fetchone()
            user_id_map[u["name"]] = row["id"]

    # --- Family settings (only if not already configured) ---
    existing_settings = {row["key"] for row in conn.execute("SELECT key FROM settings").fetchall()}
    if "familyName" not in existing_settings:
        conn.execute(
            "INSERT INTO settings(key,value) VALUES(?,?)",
            ("familyName", "测试家庭"),
        )
    if "registrationOpen" not in existing_settings:
        conn.execute(
            "INSERT INTO settings(key,value) VALUES(?,?)",
            ("registrationOpen", "1"),
        )

    # --- Cuisines ---
    cuisine_id_map = {}
    for c in DEV_CUISINES:
        row = conn.execute("SELECT id FROM dish_cuisines WHERE name=?", (c["name"],)).fetchone()
        if not row:
            cid = secrets.token_urlsafe(12)
            conn.execute(
                "INSERT INTO dish_cuisines VALUES(?,?,?,?,?)",
                (cid, c["name"], c["emoji"], c["ord"], now),
            )
            cuisine_id_map[c["name"]] = cid
            summary["cuisines"] += 1
        else:
            cuisine_id_map[c["name"]] = row["id"]

    # --- Dishes ---
    admin_uid = user_id_map.get("张三")
    existing_dishes = {row["name"] for row in conn.execute("SELECT name FROM dishes").fetchall()}
    dish_id_map = {}
    for d in DEV_DISHES:
        if d["name"] not in existing_dishes:
            did = secrets.token_urlsafe(12)
            cuisine_id = cuisine_id_map.get(d["cuisine_name"])
            conn.execute(
                "INSERT INTO dishes VALUES(?,?,?,?,?,?,?,?,?,?)",
                (did, d["name"], d["description"], None, d["tags"], cuisine_id, "", "active", admin_uid, now),
            )
            # ingredients
            for i, ing in enumerate(d["ingredients"]):
                conn.execute(
                    "INSERT INTO dish_ingredients VALUES(?,?,?,?,?,?)",
                    (secrets.token_urlsafe(12), did, ing["name"], ing["quantity"], ing["unit"], i),
                )
            # steps
            for i, step in enumerate(d["steps"]):
                conn.execute(
                    "INSERT INTO dish_steps VALUES(?,?,?,?)",
                    (secrets.token_urlsafe(12), did, i, step),
                )
            dish_id_map[d["name"]] = did
            summary["dishes"] += 1
        else:
            row = conn.execute("SELECT id FROM dishes WHERE name=?", (d["name"],)).fetchone()
            dish_id_map[d["name"]] = row["id"]

    # --- Sample meals (today lunch + tomorrow dinner) ---
    today = date.today()
    meal_plans = [
        {
            "title": "今日午餐",
            "meal_type": "lunch",
            "date": str(today),
            "dining_time": "12:00",
            "order_deadline": "10:00",
            "status": "ordering",
        },
        {
            "title": "今日晚餐",
            "meal_type": "dinner",
            "date": str(today),
            "dining_time": "18:30",
            "order_deadline": "16:00",
            "status": "ordering",
        },
        {
            "title": "明日午餐",
            "meal_type": "lunch",
            "date": str(today + timedelta(days=1)),
            "dining_time": "12:00",
            "order_deadline": "10:00",
            "status": "ordering",
        },
    ]

    existing_meal_titles = {row["title"] for row in conn.execute("SELECT title FROM meals WHERE title IS NOT NULL").fetchall()}
    for mp in meal_plans:
        if mp["title"] not in existing_meal_titles:
            mid = secrets.token_urlsafe(12)
            dining_ts = int(datetime.strptime(f"{mp['date']} {mp['dining_time']}", "%Y-%m-%d %H:%M").replace(tzinfo=TZ).timestamp())
            deadline_ts = int(datetime.strptime(f"{mp['date']} {mp['order_deadline']}", "%Y-%m-%d %H:%M").replace(tzinfo=TZ).timestamp())
            conn.execute(
                "INSERT INTO meals(id,title,meal_type,date,dining_time,order_deadline,status,is_auto,created_by,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (mid, mp["title"], mp["meal_type"], mp["date"], dining_ts, deadline_ts, mp["status"], 0, admin_uid, now),
            )
            summary["meals"] += 1

    # --- Sample orders on the first meal ---
    if summary["meals"] > 0 or "今日午餐" not in existing_meal_titles:
        lunch_row = conn.execute("SELECT id FROM meals WHERE title=?", ("今日午餐",)).fetchone()
        if lunch_row:
            lunch_id = lunch_row["id"]
            existing_orders = {(r["meal_id"], r["dish_id"], r["user_id"]) for r in conn.execute("SELECT meal_id,dish_id,user_id FROM orders").fetchall()}
            dish_names = list(dish_id_map.keys())
            order_pairs = [
                ("李四", dish_names[0]),
                ("李四", dish_names[1]),
                ("王五", dish_names[0]),
                ("王五", dish_names[3]),
            ]
            for uname, dname in order_pairs:
                uid = user_id_map.get(uname)
                did = dish_id_map.get(dname)
                if uid and did and (lunch_id, did, uid) not in existing_orders:
                    conn.execute(
                        "INSERT INTO orders VALUES(?,?,?,?,?,?)",
                        (secrets.token_urlsafe(12), lunch_id, did, uid, None, now),
                    )

    return summary
