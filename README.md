# 校园集市

一个可直接运行的 Python + Vue 校园二手商品交易平台，包含完整 C 端和管理后台。项目默认使用 SQLite，首次启动会自动建表并生成演示数据，适合课程设计、毕业设计、原型验证和后续二次开发。

## 技术栈

- 后端：Python 3.12、FastAPI、SQLAlchemy 2、SQLite、PBKDF2 密码哈希、HMAC 签名访问令牌
- 前端：Vue 3、Vite、Vue Router、Pinia、Axios、Element Plus、ECharts
- 设计：校园绿 + 象牙白视觉系统，桌面端与移动端响应式适配，本地图片资源不依赖外部图床

## 已实现功能

### C 端

- 注册、登录、校园身份信息、实名认证状态、个人资料与信用分
- 首页推荐、校园切换入口、商品分类、关键词搜索、价格/成色/分类筛选与多种排序
- 商品详情、卖家资料、同类推荐、浏览量、收藏与举报
- 闲置发布、图片上传、编辑、重新审核与下架
- 收藏夹、我的发布、审核状态、消息通知
- 商品会话、未读消息、历史聊天、围绕商品快速沟通
- 买入/卖出订单、付款、确认面交、完成、取消、退款与争议状态流转
- 交易评价、信用展示、安全交易提示
- 适配手机宽度，无横向页面溢出

### 管理后台

- 数据概览：用户、商品、订单、GMV、待审与举报指标
- 近 7 日订单/交易额趋势、商品分类分布、最新订单
- 用户搜索、角色筛选、账号暂停/恢复/封禁
- 商品审核、驳回、下架、恢复、推荐位管理
- 全平台订单检索与详情查看
- 举报受理、跟进、解决与处理结果通知
- 商品分类、首页轮播、平台公告运营管理
- 审核策略、交易参数、基础配置和管理员审计日志

## 快速启动

在项目根目录运行：

```bash
./scripts/dev.sh
```

也可以分别启动：

```bash
cd backend
python3 -m venv .venv
PIP_CERT=/etc/ssl/cert.pem .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

- C 端：http://localhost:5173/
- 管理后台：http://localhost:5173/admin
- API 文档：http://localhost:8000/docs

## 演示账号

| 用途 | 账号 | 密码 |
| --- | --- | --- |
| C 端用户 | `20230001` | `demo123` |
| 管理员 | `admin` | `admin123` |

登录页也提供“C 端账号”和“管理员账号”快速填充按钮。

## 目录结构

```text
design-platform/
├── backend/
│   ├── app/
│   │   ├── main.py          # API 路由与业务逻辑
│   │   ├── models.py        # 数据模型
│   │   ├── security.py      # 密码与令牌
│   │   ├── serializers.py   # 响应序列化
│   │   └── seed.py          # 演示数据
│   └── requirements.txt
├── frontend/
│   ├── public/assets/       # 校园、商品和头像资源
│   └── src/
│       ├── api/             # Axios 请求封装
│       ├── components/      # 公共组件
│       ├── layouts/         # C 端 / 管理后台布局
│       ├── router/          # 页面路由与权限守卫
│       ├── stores/          # Pinia 状态
│       └── views/           # C 端与后台页面
└── scripts/dev.sh           # 一键启动脚本
```

## 数据与安全说明

- SQLite 数据库位于 `backend/campus_market.db`，首次启动自动创建。
- 上传文件存放于 `backend/uploads/`。
- 生产环境必须设置新的 `APP_SECRET`，并建议改用 PostgreSQL、对象存储和 HTTPS。
- 当前付款为校园面交业务状态模拟，不接入真实支付渠道；接入支付前应增加回调验签、幂等、账务流水和退款审核。

## 验证

```bash
cd frontend && npm run build
cd backend && .venv/bin/python -m py_compile app/*.py
```

项目已完成首页、搜索筛选、登录、消息、订单、发布页，以及管理后台数据、商品审核、举报和运营页面的浏览器验证。

