from __future__ import annotations

import json
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    Announcement,
    Banner,
    Category,
    Conversation,
    Favorite,
    Message,
    Notification,
    Order,
    Product,
    Report,
    Review,
    SystemConfig,
    User,
)
from .security import hash_password


def seed_database(db: Session) -> None:
    if db.scalar(select(User.id).limit(1)):
        return

    categories = [
        Category(name="教材教辅", icon="Reading", color="#4f7b4f", sort_order=1),
        Category(name="数码电子", icon="Monitor", color="#3f6ea8", sort_order=2),
        Category(name="运动户外", icon="Bicycle", color="#5d8b3d", sort_order=3),
        Category(name="生活家居", icon="House", color="#d88945", sort_order=4),
        Category(name="美妆个护", icon="MagicStick", color="#c46b82", sort_order=5),
        Category(name="乐器文娱", icon="Headset", color="#8a64a8", sort_order=6),
        Category(name="食品饮料", icon="CoffeeCup", color="#c79036", sort_order=7),
        Category(name="其他闲置", icon="MoreFilled", color="#667085", sort_order=8),
    ]
    db.add_all(categories)
    db.flush()

    users = [
        User(username="admin", email="admin@campus.local", password_hash=hash_password("admin123"), nickname="平台管理员", avatar="/assets/avatars/user-1.png", role="admin", campus="同济大学", student_no="A00001", verified=True, bio="校园集市运营团队"),
        User(username="20230001", email="demo@campus.local", phone="13800000001", password_hash=hash_password("demo123"), nickname="学长很靠谱", avatar="/assets/avatars/user-1.png", campus="同济大学", student_no="20230001", verified=True, bio="数码爱好者，所有闲置均可当面验货。"),
        User(username="20230002", email="latte@campus.local", phone="13800000002", password_hash=hash_password("demo123"), nickname="Latte加糖", avatar="/assets/avatars/user-2.png", campus="同济大学", student_no="20230002", verified=True, credit_score=98, bio="搬宿舍清闲置～"),
        User(username="20220018", email="orange@campus.local", phone="13800000003", password_hash=hash_password("demo123"), nickname="胶片日记", avatar="/assets/avatars/user-5.png", campus="同济大学", student_no="20220018", verified=True, credit_score=99),
        User(username="20240086", email="joker@campus.local", phone="13800000004", password_hash=hash_password("demo123"), nickname="Joker同学", avatar="/assets/avatars/user-3.png", campus="同济大学", student_no="20240086", verified=True, credit_score=96),
        User(username="20210006", email="green@campus.local", phone="13800000005", password_hash=hash_password("demo123"), nickname="生活家小H", avatar="/assets/avatars/user-6.png", campus="同济大学", student_no="20210006", verified=True, credit_score=97),
    ]
    db.add_all(users)
    db.flush()

    product_specs = [
        ("iPad Air 5 64G 深空灰", "自用 iPad Air 5，屏幕无划痕，电池健康，含原装充电器和保护壳。支持四平路校区当面验机。", 1850, 4399, "9成新", 2, 2, "/assets/products/ipad.png", "四平路校区", True),
        ("高等数学 第七版 上下册", "同济版高数上下册，考研复习用过，重点章节有少量铅笔笔记。", 40, 96, "95新", 1, 3, "/assets/products/books.png", "嘉定校区", True),
        ("米家台灯 Lite", "宿舍自用半年，三档色温、亮度可调，功能完好。", 60, 129, "9成新", 4, 5, "/assets/products/lamp.png", "四平路校区", True),
        ("捷安特 Escape 1 公路车", "21 速通勤车，刚做过保养，车架 M 码，适合 165-180cm。", 450, 1898, "8成新", 3, 2, "/assets/products/bicycle.png", "嘉定校区", True),
        ("富士 instax mini 11", "薰衣草紫，成色很好，送相机包和两盒彩纸。", 280, 599, "9成新", 6, 4, "/assets/products/camera.png", "四平路校区", True),
        ("复古小冰箱 45L", "宿舍搬空，制冷正常、安静省电，可约时间自提。", 220, 499, "9成新", 4, 6, "/assets/products/fridge.png", "嘉定校区", True),
        ("Keychron K2 机械键盘", "茶轴蓝牙双模，键帽已清洁，带原装线。", 280, 598, "8成新", 2, 5, "/assets/products/keyboard.png", "彰武路校区", False),
        ("YAMAHA F310 民谣吉他", "入门练习首选，琴颈顺直，弦距合适，送琴包。", 320, 899, "8成新", 6, 3, "/assets/products/guitar.png", "学生服务中心", False),
        ("宿舍人体工学椅", "可升降、腰托可调，毕业搬家低价出。", 160, 499, "8成新", 4, 4, "/assets/products/chair.png", "西南十楼", False),
        ("罗技 MX Master 3S", "白色静音办公鼠标，使用三个月，配件齐全。", 380, 699, "95新", 2, 2, "/assets/products/mouse.png", "四平路校区", False),
        ("羽毛球拍 ASTROX 77", "4U5，已穿线，拍框无磕碰，适合进阶。", 520, 1099, "9成新", 3, 5, "/assets/products/badminton.png", "体育馆", False),
        ("20 寸登机行李箱", "九成新，只用过两次，万向轮顺滑。", 90, 299, "9成新", 8, 6, "/assets/products/suitcase.png", "嘉定校区", False),
    ]
    products: list[Product] = []
    for index, spec in enumerate(product_specs):
        title, desc, price, original, condition, category_id, seller_id, image, location, featured = spec
        products.append(
            Product(
                title=title,
                description=desc,
                price=price,
                original_price=original,
                condition=condition,
                category_id=category_id,
                seller_id=seller_id,
                pickup_location=location,
                transaction_method="当面交易 / 校内自提",
                images=json.dumps([image], ensure_ascii=False),
                status="published" if index != 10 else "pending",
                view_count=980 - index * 63,
                favorite_count=max(8, 126 - index * 9),
                featured=featured,
                created_at=datetime.now() - timedelta(hours=index * 3 + 1),
            )
        )
    db.add_all(products)
    db.flush()

    db.add_all([Favorite(user_id=2, product_id=3), Favorite(user_id=2, product_id=5), Favorite(user_id=3, product_id=1)])

    orders = [
        Order(order_no="CM202608110001", product_id=3, buyer_id=2, seller_id=5, amount=60, status="paid", pickup_code="482731", meetup_place="四平路校区图书馆门口", buyer_note="今晚七点可以吗", paid_at=datetime.now() - timedelta(hours=2)),
        Order(order_no="CM202608090018", product_id=2, buyer_id=2, seller_id=3, amount=40, status="completed", pickup_code="158204", meetup_place="嘉定校区食堂", completed_at=datetime.now() - timedelta(days=1)),
        Order(order_no="CM202608080012", product_id=5, buyer_id=5, seller_id=4, amount=280, status="meeting", pickup_code="637922", meetup_place="四平路校区南门"),
        Order(order_no="CM202608070006", product_id=4, buyer_id=4, seller_id=2, amount=450, status="cancelled", cancel_reason="买家行程变更"),
    ]
    db.add_all(orders)
    db.flush()

    conversations = [
        Conversation(product_id=3, buyer_id=2, seller_id=5, last_message="好的，今晚七点图书馆门口见～", last_message_at=datetime.now() - timedelta(minutes=12)),
        Conversation(product_id=1, buyer_id=3, seller_id=2, last_message="可以当面验机吗？", last_message_at=datetime.now() - timedelta(minutes=28)),
        Conversation(product_id=4, buyer_id=4, seller_id=2, last_message="车架适合 170cm 吗？", last_message_at=datetime.now() - timedelta(hours=2)),
    ]
    db.add_all(conversations)
    db.flush()
    db.add_all([
        Message(conversation_id=1, sender_id=2, content="你好，台灯还在吗？", created_at=datetime.now() - timedelta(minutes=35), is_read=True),
        Message(conversation_id=1, sender_id=5, content="还在的，灯光和按键都正常。", created_at=datetime.now() - timedelta(minutes=25), is_read=True),
        Message(conversation_id=1, sender_id=2, content="好的，今晚七点图书馆门口见～", created_at=datetime.now() - timedelta(minutes=12)),
        Message(conversation_id=2, sender_id=3, content="可以当面验机吗？", created_at=datetime.now() - timedelta(minutes=28)),
        Message(conversation_id=3, sender_id=4, content="车架适合 170cm 吗？", created_at=datetime.now() - timedelta(hours=2)),
    ])

    db.add_all([
        Notification(user_id=2, title="订单已付款", content="你购买的米家台灯 Lite 已付款，请与卖家确认见面地点。", notification_type="order"),
        Notification(user_id=2, title="商品审核通过", content="你发布的捷安特 Escape 1 公路车已通过审核。", notification_type="product", created_at=datetime.now() - timedelta(days=1)),
        Notification(user_id=2, title="开学季安全提醒", content="请优先校内当面交易，贵重物品务必现场验货。", notification_type="system", created_at=datetime.now() - timedelta(days=2)),
    ])
    db.add_all([
        Report(reporter_id=3, target_type="product", target_id=12, reason="疑似信息不实", description="商品图片与描述不一致，请核实。"),
        Report(reporter_id=5, target_type="user", target_id=4, reason="爽约", description="约好时间后对方未出现。", status="processing"),
    ])
    db.add(Review(order_id=2, reviewer_id=2, reviewee_id=3, score=5, content="书保存得很好，交易准时。"))
    db.add_all([
        Banner(title="开学季，让好物继续发光", subtitle="同校交易更省心，发布闲置赢校园积分", image="/assets/hero-campus.png", link="/market", sort_order=1),
        Announcement(title="校园集市交易安全指南", content="优先选择校内公共场所当面交易，贵重物品请现场验货，切勿脱离平台沟通或提前转账。", announcement_type="safety", pinned=True),
        Announcement(title="开学季闲置循环计划启动", content="8 月 11 日至 9 月 15 日发布教材和宿舍好物，可获得双倍校园积分。", announcement_type="campaign"),
    ])
    db.add_all([
        SystemConfig(config_key="site_name", config_value="校园集市", description="平台名称"),
        SystemConfig(config_key="audit_required", config_value="true", description="新商品是否需要审核"),
        SystemConfig(config_key="max_product_images", config_value="9", description="商品最大图片数"),
        SystemConfig(config_key="service_fee_rate", config_value="0", description="平台服务费比例"),
    ])
    db.commit()
