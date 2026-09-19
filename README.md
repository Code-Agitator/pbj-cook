# PBJCook uni-app

这是 `RendaHuang/DaCook` 的 uni-app + FastAPI 复刻版，主要面向微信小程序，同时保留 H5 调试能力。

## 目录

- `frontend/`：Vue 3 + uni-app，包含微信小程序与 H5 构建
- `backend/`：Python + FastAPI + SQLite，数据和上传文件默认位于 `backend/data/`

## 启动后端

```powershell
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

接口文档：`http://127.0.0.1:8000/docs`

## 启动前端

```powershell
cd frontend
npm install
npm run dev:h5
```

微信小程序构建：

```powershell
npm run build:mp-weixin
```

构建产物位于 `frontend/dist/build/mp-weixin`，使用微信开发者工具导入。真机访问时，在"我的 → 服务器设置"填写局域网或 HTTPS 后端地址；正式发布要求在小程序后台配置合法 HTTPS 域名。

## 开发模式自动初始化测试数据

设置环境变量 `DACOOK_SEED_DEV=1` 后启动后端，会自动填充测试数据用于调试：

```powershell
$env:DACOOK_SEED_DEV="1"; .venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

填充的数据包括：

- **测试用户**：张三（管理员，PIN:123456）、李四、王五（普通用户，PIN:123456）
- **菜系**：川菜🌶️、粤菜🥟、鲁菜🍜、苏菜🦀、西餐🍝
- **菜品**：8 道示例菜品，均含食材清单和烹饪步骤
- **饭局**：今日午餐、今日晚餐、明日午餐
- **点餐记录**：李四和王五在今日午餐中各有若干点餐

> 数据填充是幂等的，重复启动不会重复插入。正常生产模式请勿设置该变量。

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DACOOK_DATABASE` | SQLite 数据库文件路径 | `backend/data/dacook.db` |
| `DACOOK_UPLOADS` | 上传文件存储目录 | `backend/data/uploads` |
| `DACOOK_TIMEZONE` | 时区 | `Asia/Shanghai` |
| `DACOOK_CORS_ORIGINS` | 允许的 CORS 来源，逗号分隔 | `http://localhost:5173,http://127.0.0.1:5173` |
| `DACOOK_SEED_DEV` | 设为 `1` 时启动自动填充测试数据 | 不设置 |

## 功能范围

首位成员创建家庭并成为管理员；支持头像成员选择登录、注册口令、菜品与菜系、食材和步骤、饭局点菜、掌勺认领、菜品跳过、状态流转、饭后评价、贡献热力图、成员管理和自动饭局规则。
