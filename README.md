# DaCook uni-app

这是 `D:\Work\DaCook` 的 uni-app + FastAPI 复刻版，主要面向微信小程序，同时保留 H5 调试能力。

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

构建产物位于 `frontend/dist/build/mp-weixin`，使用微信开发者工具导入。真机访问时，在“我的 → 服务器设置”填写局域网或 HTTPS 后端地址；正式发布要求在小程序后台配置合法 HTTPS 域名。

## 功能范围

首位成员创建家庭并成为管理员；支持头像成员选择登录、注册口令、菜品与菜系、食材和步骤、饭局点菜、掌勺认领、菜品跳过、状态流转、饭后评价、贡献热力图、成员管理和自动饭局规则。
