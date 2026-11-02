from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/eddy/Codes/design-platform/thesis-analysis/figures/diagrams")
ROOT.mkdir(parents=True, exist_ok=True)
FONT = "/Users/eddy/Codes/design-platform/thesis-analysis/fonts/ArialUnicode.ttf"

GREEN = "#2F6B4F"
GREEN_DARK = "#174A34"
GREEN_LIGHT = "#EAF3EC"
BLUE = "#5478A7"
BLUE_LIGHT = "#EAF0F8"
ORANGE = "#C97A52"
ORANGE_LIGHT = "#FBEEE7"
RED = "#B94B4B"
RED_LIGHT = "#FDECEC"
GRAY = "#667085"
GRAY_LIGHT = "#F4F6F8"
INK = "#20242A"
LINE = "#8793A1"
WHITE = "#FFFFFF"


def f(size: int):
    return ImageFont.truetype(FONT, size)


def canvas(width=1800, height=1050):
    image = Image.new("RGB", (width, height), WHITE)
    return image, ImageDraw.Draw(image)


def title(draw, text, subtitle=""):
    draw.text((70, 54), text, font=f(44), fill=GREEN_DARK)
    if subtitle:
        draw.text((74, 112), subtitle, font=f(24), fill=GRAY)
    draw.line((70, 155, 1730, 155), fill="#DDE4E0", width=2)


def rounded_box(draw, box, text, fill=GRAY_LIGHT, outline=LINE, font_size=27, bold=False, radius=18, text_fill=INK):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=3)
    x1, y1, x2, y2 = box
    lines = text.split("\n")
    font = f(font_size + (2 if bold else 0))
    line_height = font_size * 1.42
    total = line_height * len(lines)
    for i, line in enumerate(lines):
        bounds = draw.textbbox((0, 0), line, font=font)
        width = bounds[2] - bounds[0]
        draw.text(((x1 + x2 - width) / 2, (y1 + y2 - total) / 2 + i * line_height), line, font=font, fill=text_fill)


def arrow(draw, start, end, fill=LINE, width=4, label="", label_offset=(0, -30)):
    sx, sy = start
    ex, ey = end
    draw.line((sx, sy, ex, ey), fill=fill, width=width)
    angle = math.atan2(ey - sy, ex - sx)
    length = 16
    spread = math.pi / 7
    pts = [
        (ex, ey),
        (ex - length * math.cos(angle - spread), ey - length * math.sin(angle - spread)),
        (ex - length * math.cos(angle + spread), ey - length * math.sin(angle + spread)),
    ]
    draw.polygon(pts, fill=fill)
    if label:
        font = f(21)
        bbox = draw.textbbox((0, 0), label, font=font)
        tx = (sx + ex) / 2 - (bbox[2] - bbox[0]) / 2 + label_offset[0]
        ty = (sy + ey) / 2 + label_offset[1]
        draw.rectangle((tx - 5, ty - 3, tx + bbox[2] - bbox[0] + 5, ty + bbox[3] - bbox[1] + 4), fill=WHITE)
        draw.text((tx, ty), label, font=font, fill=GRAY)


def save(image, name):
    image.save(ROOT / name, quality=95)


def process_flow():
    image, draw = canvas(1800, 920)
    title(draw, "校园二手交易核心业务流程", "从商品发布到交易评价的端到端业务闭环")
    labels = ["用户登录", "发布商品", "后台审核", "检索沟通", "创建订单", "付款/面交", "完成评价"]
    xs = [55, 305, 555, 805, 1055, 1305, 1555]
    for i, (x, label) in enumerate(zip(xs, labels)):
        fill = BLUE_LIGHT if i == 2 else ORANGE_LIGHT if i in (4, 5) else GREEN_LIGHT
        edge = BLUE if i == 2 else ORANGE if i in (4, 5) else GREEN
        rounded_box(draw, (x, 300, x + 190, 420), f"{i + 1}\n{label}", fill, edge, 25, True)
        if i < 6:
            arrow(draw, (x + 190, 360), (xs[i + 1], 360), GREEN, 4)
    rounded_box(draw, (555, 535, 745, 625), "审核驳回", "#FFF4E6", "#D9902F", 24, True)
    arrow(draw, (650, 420), (650, 535), "#D9902F", label="不通过", label_offset=(55, -5))
    arrow(draw, (555, 580), (400, 420), "#D9902F", label="修改后重审", label_offset=(-30, 10))
    rounded_box(draw, (1300, 535, 1530, 625), "取消/退款/争议", RED_LIGHT, RED, 24, True)
    arrow(draw, (1400, 420), (1400, 535), RED, label="异常分支", label_offset=(65, -5))
    rounded_box(draw, (1515, 690, 1735, 780), "举报与平台介入", BLUE_LIGHT, BLUE, 23, True)
    arrow(draw, (1510, 625), (1600, 690), BLUE, label="处理", label_offset=(30, -15))
    draw.text((70, 810), "业务闭环强调：身份可识别、商品可审核、沟通有上下文、订单有状态、异常可追溯。", font=f(25), fill=GRAY)
    save(image, "fig-3-1-business-flow.png")


def use_case():
    image, draw = canvas(1800, 1080)
    title(draw, "系统总体用例图", "游客、校园用户和管理员三类角色的核心能力边界")
    rounded_box(draw, (50, 285, 260, 385), "游客", GREEN_LIGHT, GREEN, 30, True)
    rounded_box(draw, (50, 590, 260, 690), "校园用户", GREEN_LIGHT, GREEN, 30, True)
    rounded_box(draw, (1540, 450, 1750, 550), "管理员", BLUE_LIGHT, BLUE, 30, True)
    cases = [("浏览与检索商品", 390, 250), ("注册与登录", 710, 250), ("发布/编辑商品", 390, 460), ("收藏与商品沟通", 710, 460), ("创建与处理订单", 390, 670), ("评价/通知/举报", 710, 670)]
    for label, x, y in cases:
        rounded_box(draw, (x, y, x + 240, y + 90), label, WHITE, GREEN, 23)
    arrow(draw, (260, 335), (390, 295), GREEN)
    for _, x, y in cases:
        arrow(draw, (260, 640), (x, y + 45), GREEN, 3)
    admin_cases = [("数据概览", 1100, 210), ("用户状态管理", 1100, 330), ("商品审核", 1100, 450), ("订单查询", 1100, 570), ("举报与风控", 1100, 690), ("运营/配置/审计", 1100, 810)]
    for label, x, y in admin_cases:
        rounded_box(draw, (x, y, x + 260, y + 82), label, WHITE, BLUE, 23)
        arrow(draw, (1540, 500), (1360, y + 41), BLUE, 3)
    draw.text((65, 965), "校园用户同时具备游客的公开浏览能力；管理端路由与接口均受角色权限约束。", font=f(25), fill=GRAY)
    save(image, "fig-3-2-use-case.png")


def architecture():
    image, draw = canvas(1800, 1120)
    title(draw, "系统总体架构图", "Vue 单页应用、FastAPI 服务、SQLAlchemy 数据层与文件资源的分层协作")
    rows = [
        (220, "客户端表现层", GREEN_LIGHT, GREEN, ["C 端页面", "管理后台", "响应式布局"]),
        (425, "前端应用层", GREEN_LIGHT, GREEN, ["Vue 3 / Router", "Pinia / Axios", "Element Plus / ECharts"]),
        (630, "接口与业务层", BLUE_LIGHT, BLUE, ["FastAPI 路由", "Pydantic 校验", "依赖注入与权限"]),
        (835, "数据与资源层", ORANGE_LIGHT, ORANGE, ["SQLAlchemy ORM", "SQLite 数据库", "uploads 静态资源"]),
    ]
    for row_idx, (y, label, fill, edge, items) in enumerate(rows):
        rounded_box(draw, (60, y, 340, y + 125), label, fill, edge, 28, True)
        for i, item in enumerate(items):
            x = 430 + i * 425
            rounded_box(draw, (x, y + 13, x + 340, y + 112), item, WHITE, edge, 25)
        if row_idx < len(rows) - 1:
            arrow(draw, (900, y + 125), (900, y + 205), LINE, 4, "调用/HTTP JSON", (110, -4))
    draw.text((65, 1030), "部署边界：浏览器经 /api 调用后端；图片由 /uploads 提供；数据层可在生产环境替换为服务器型数据库。", font=f(24), fill=GRAY)
    save(image, "fig-4-1-architecture.png")


def modules():
    image, draw = canvas(1800, 1080)
    title(draw, "系统功能模块图", "C 端交易闭环与管理后台运营治理的双端协同")
    rounded_box(draw, (610, 190, 1190, 295), "校园二手商品交易平台", GREEN_DARK, GREEN_DARK, 31, True, text_fill=WHITE)
    rounded_box(draw, (90, 375, 790, 465), "C 端", GREEN_LIGHT, GREEN, 31, True)
    rounded_box(draw, (1010, 375, 1710, 465), "管理后台", BLUE_LIGHT, BLUE, 31, True)
    arrow(draw, (735, 295), (440, 375), GREEN)
    arrow(draw, (1065, 295), (1360, 375), BLUE)
    c_items = ["账户与个人中心", "首页与商品检索", "发布与商品管理", "收藏与消息", "订单与评价", "通知与举报"]
    a_items = ["数据概览", "用户管理", "商品审核", "订单管理", "举报与风控", "运营内容", "系统配置与审计"]
    for i, item in enumerate(c_items):
        col, row = i % 2, i // 2
        x, y = 110 + col * 345, 535 + row * 130
        rounded_box(draw, (x, y, x + 305, y + 85), item, WHITE, GREEN, 23)
    for i, item in enumerate(a_items):
        col, row = i % 2, i // 2
        x, y = 1030 + col * 345, 515 + row * 112
        rounded_box(draw, (x, y, x + 305, y + 78), item, WHITE, BLUE, 22)
    draw.text((430, 965), "共享实体：用户、商品、订单、会话、消息、评价、举报与通知", font=f(24), fill=GRAY)
    save(image, "fig-4-2-modules.png")


def auth_sequence():
    image, draw = canvas(1800, 1120)
    title(draw, "登录认证时序图", "浏览器、Vue、FastAPI、SQLAlchemy 与 SQLite 的交互")
    participants = [(145, "用户", GREEN_LIGHT, GREEN), (490, "Vue 登录页", GREEN_LIGHT, GREEN), (840, "FastAPI", BLUE_LIGHT, BLUE), (1190, "SQLAlchemy", ORANGE_LIGHT, ORANGE), (1540, "SQLite", ORANGE_LIGHT, ORANGE)]
    for x, label, fill, edge in participants:
        rounded_box(draw, (x - 110, 210, x + 110, 290), label, fill, edge, 23, True)
        draw.line((x, 290, x, 1010), fill="#C6CCD3", width=3)
    messages = [(145, 490, 350, "输入账号与密码"), (490, 840, 440, "POST /api/auth/login"), (840, 1190, 530, "查询用户"), (1190, 1540, 620, "SELECT users"), (1540, 1190, 710, "用户记录"), (1190, 840, 800, "映射 User"), (840, 490, 890, "PBKDF2 校验并签发令牌"), (490, 145, 980, "保存状态并跳转")]
    for sx, ex, y, label in messages:
        arrow(draw, (sx, y), (ex, y), GREEN if ex > sx else BLUE, 4, label)
    save(image, "fig-4-3-auth-sequence.png")


def state_diagram():
    image, draw = canvas(1800, 1080)
    title(draw, "商品与订单状态机", "状态迁移由后端动作、用户角色和业务条件共同约束")
    draw.text((70, 205), "商品状态", font=f(30), fill=GREEN_DARK)
    products = [(70, "pending", "#FFF4E6", "#D9902F"), (370, "published", GREEN_LIGHT, GREEN), (700, "off_shelf", GRAY_LIGHT, GRAY), (1030, "rejected", RED_LIGHT, RED), (1390, "sold", BLUE_LIGHT, BLUE)]
    for x, label, fill, edge in products:
        rounded_box(draw, (x, 270, x + 240, 360), label, fill, edge, 24, True)
    arrow(draw, (310, 315), (370, 315), GREEN, label="审核通过")
    arrow(draw, (610, 315), (700, 315), GRAY, label="下架")
    arrow(draw, (700, 350), (610, 350), GREEN, label="恢复", label_offset=(0, 8))
    arrow(draw, (190, 360), (1030, 360), RED, label="审核驳回", label_offset=(0, 10))
    arrow(draw, (610, 270), (1390, 270), BLUE, label="订单完成", label_offset=(0, -28))

    draw.text((70, 500), "订单状态", font=f(30), fill=GREEN_DARK)
    orders = [(70, "pending", GREEN_LIGHT, GREEN), (345, "paid", GREEN_LIGHT, GREEN), (620, "meeting", GREEN_LIGHT, GREEN), (895, "completed", GREEN_LIGHT, GREEN), (1190, "cancelled", GRAY_LIGHT, GRAY), (1480, "refunding /\ndisputed", ORANGE_LIGHT, ORANGE)]
    widths = [210, 210, 210, 230, 220, 260]
    for (x, label, fill, edge), w in zip(orders, widths):
        rounded_box(draw, (x, 580, x + w, 680), label, fill, edge, 23, True)
    arrow(draw, (280, 630), (345, 630), GREEN, label="付款")
    arrow(draw, (555, 630), (620, 630), GREEN, label="确认面交")
    arrow(draw, (830, 630), (895, 630), GREEN, label="完成")
    arrow(draw, (175, 680), (1190, 680), GRAY, label="取消", label_offset=(0, 15))
    arrow(draw, (450, 580), (1480, 580), ORANGE, label="退款 / 争议", label_offset=(0, -30))
    draw.text((70, 880), "说明：当前付款为业务状态模拟；取货码已生成，但尚未形成强制核销闭环。", font=f(25), fill=GRAY)
    save(image, "fig-4-4-state-machine.png")


def er_diagram():
    image, draw = canvas(1800, 1300)
    title(draw, "核心数据实体关系图", "为保证可读性，运营内容与系统配置实体以分组形式呈现")
    entities = {
        "User": (70, 250, GREEN_LIGHT, GREEN), "Category": (570, 190, BLUE_LIGHT, BLUE), "Product": (570, 390, GREEN_LIGHT, GREEN),
        "Favorite": (240, 580, GRAY_LIGHT, GRAY), "Order": (570, 650, ORANGE_LIGHT, ORANGE), "Conversation": (1010, 390, BLUE_LIGHT, BLUE),
        "Message": (1430, 390, BLUE_LIGHT, BLUE), "Review": (130, 850, GREEN_LIGHT, GREEN), "Report": (1010, 650, ORANGE_LIGHT, ORANGE),
        "Notification": (1430, 650, GREEN_LIGHT, GREEN), "AuditLog": (570, 950, GRAY_LIGHT, GRAY), "运营与配置": (1050, 950, GRAY_LIGHT, GRAY),
    }
    sizes = {name: (260 if name not in ("Conversation", "Notification", "运营与配置") else 310, 86) for name in entities}
    centers = {}
    for name, (x, y, fill, edge) in entities.items():
        w, h = sizes[name]
        rounded_box(draw, (x, y, x + w, y + h), name, fill, edge, 23, True)
        centers[name] = (x + w / 2, y + h / 2)
    relations = [("User", "Product", "1:N 发布"), ("Category", "Product", "1:N 分类"), ("User", "Favorite", "1:N"), ("Product", "Favorite", "1:N"), ("User", "Order", "买家/卖家"), ("Product", "Order", "1:N"), ("Product", "Conversation", "1:N"), ("Conversation", "Message", "1:N"), ("User", "Review", "评价双方"), ("Order", "Review", "1:N"), ("User", "Report", "举报/处理"), ("User", "Notification", "1:N"), ("User", "AuditLog", "管理员"), ("User", "运营与配置", "维护")]
    for left, right, label in relations:
        arrow(draw, centers[left], centers[right], "#A1AAB4", 3, label, (0, -24))
    draw.text((70, 1190), "运营与配置组包含 Banner、Announcement、SystemConfig；图中省略字段，仅呈现实体级关系。", font=f(24), fill=GRAY)
    save(image, "fig-4-5-er.png")


def request_flow():
    image, draw = canvas(1800, 900)
    title(draw, "后端请求处理流程", "统一认证依赖、业务校验、ORM 会话与结构化响应")
    labels = ["Axios 请求", "CORS/路由", "令牌与角色校验", "Pydantic 校验", "业务规则处理", "SQLAlchemy", "JSON 响应"]
    widths = [190, 200, 230, 210, 220, 200, 180]
    xs = [55]
    for w in widths[:-1]:
        xs.append(xs[-1] + w + 55)
    for i, (x, w, label) in enumerate(zip(xs, widths, labels)):
        fill = BLUE_LIGHT if i in (1, 2, 3) else ORANGE_LIGHT if i == 5 else GREEN_LIGHT
        edge = BLUE if i in (1, 2, 3) else ORANGE if i == 5 else GREEN
        rounded_box(draw, (x, 280, x + w, 385), label, fill, edge, 22, True)
        if i < 6:
            arrow(draw, (x + w, 332), (xs[i + 1], 332), LINE, 4)
    errors = [(520, "401 / 403", RED_LIGHT, RED, "权限失败"), (805, "400 / 409", "#FFF4E6", "#D9902F", "参数/冲突"), (1120, "404 / 业务异常", GRAY_LIGHT, GRAY, "资源异常")]
    for x, label, fill, edge, reason in errors:
        rounded_box(draw, (x, 555, x + 230, 650), label, fill, edge, 23, True)
        arrow(draw, (x + 115, 385), (x + 115, 555), edge, label=reason, label_offset=(70, -5))
    draw.text((65, 770), "前端响应拦截器统一提取 detail，并在 401 时清理本地令牌与用户信息。", font=f(25), fill=GRAY)
    save(image, "fig-5-1-request-flow.png")


def benchmark_chart():
    data_path = Path("/Users/eddy/Codes/design-platform/thesis-analysis/test-results/api-readonly-benchmark.json")
    data = json.loads(data_path.read_text(encoding="utf-8"))["results"]
    image, draw = canvas(1600, 900)
    title(draw, "本地只读 API 小规模并发测试", "每个接口 30 次请求，并发数 5；单位：毫秒")
    plot = (140, 240, 1500, 700)
    draw.line((plot[0], plot[1], plot[0], plot[3]), fill=LINE, width=3)
    draw.line((plot[0], plot[3], plot[2], plot[3]), fill=LINE, width=3)
    max_value = max(max(item["mean_ms"], item["p95_ms"]) for item in data) * 1.18
    for tick in range(0, 31, 5):
        y = plot[3] - tick / max_value * (plot[3] - plot[1])
        draw.line((plot[0], y, plot[2], y), fill="#E7EAED", width=2)
        draw.text((75, y - 12), str(tick), font=f(20), fill=GRAY)
    group_w = (plot[2] - plot[0]) / len(data)
    for i, item in enumerate(data):
        cx = plot[0] + group_w * (i + 0.5)
        for j, (key, color) in enumerate((("mean_ms", "#6FA37E"), ("p95_ms", "#C88963"))):
            value = item[key]
            bh = value / max_value * (plot[3] - plot[1])
            x1 = cx - 70 + j * 75
            draw.rectangle((x1, plot[3] - bh, x1 + 58, plot[3]), fill=color)
            txt = f"{value:.2f}"
            tw = draw.textbbox((0, 0), txt, font=f(20))[2]
            draw.text((x1 + 29 - tw / 2, plot[3] - bh - 30), txt, font=f(20), fill=INK)
        label = item["path"].replace("?page=1&page_size=12", "")
        tw = draw.textbbox((0, 0), label, font=f(19))[2]
        draw.text((cx - tw / 2, 725), label, font=f(19), fill=INK)
    draw.rectangle((1050, 175, 1080, 195), fill="#6FA37E")
    draw.text((1090, 170), "平均响应时间", font=f(21), fill=INK)
    draw.rectangle((1300, 175, 1330, 195), fill="#C88963")
    draw.text((1340, 170), "P95 响应时间", font=f(21), fill=INK)
    draw.text((140, 820), "说明：localhost、小样本、只读接口测试，仅用于验证演示环境的基本响应，不代表生产容量。", font=f(23), fill=GRAY)
    save(image, "fig-6-1-benchmark.png")


def main():
    process_flow(); use_case(); architecture(); modules(); auth_sequence(); state_diagram(); er_diagram(); request_flow(); benchmark_chart()
    print(f"generated diagrams in {ROOT}")


if __name__ == "__main__":
    main()
