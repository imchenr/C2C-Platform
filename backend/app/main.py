from __future__ import annotations

import json
import secrets
import shutil
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.orm import Session, joinedload

from .database import Base, SessionLocal, engine, get_db
from .models import (
    Announcement,
    AuditLog,
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
from .security import create_access_token, decode_access_token, hash_password, verify_password
from .seed import seed_database
from .serializers import category as serialize_category
from .serializers import conversation as serialize_conversation
from .serializers import iso, message as serialize_message, order as serialize_order
from .serializers import product as serialize_product
from .serializers import user_private, user_public


UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_database(db)
    yield


app = FastAPI(
    title="校园集市 API",
    description="校园二手商品交易平台后端服务",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


class RegisterPayload(BaseModel):
    username: str = Field(min_length=4, max_length=64)
    email: str = Field(min_length=5, max_length=128)
    password: str = Field(min_length=6, max_length=64)
    nickname: str = Field(min_length=2, max_length=64)
    campus: str = "同济大学"
    student_no: str = ""


class LoginPayload(BaseModel):
    account: str
    password: str


class ProfilePayload(BaseModel):
    nickname: str | None = None
    phone: str | None = None
    campus: str | None = None
    student_no: str | None = None
    bio: str | None = None
    avatar: str | None = None


class ProductPayload(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=10, max_length=5000)
    price: float = Field(gt=0)
    original_price: float = Field(default=0, ge=0)
    condition: str = "9成新"
    category_id: int
    campus: str = "同济大学"
    pickup_location: str
    transaction_method: str = "当面交易 / 校内自提"
    images: list[str] = Field(default_factory=list, max_length=9)


class OrderCreatePayload(BaseModel):
    product_id: int
    meetup_place: str = ""
    buyer_note: str = ""


class OrderActionPayload(BaseModel):
    action: Literal["pay", "confirm_meetup", "complete", "cancel", "refund", "dispute"]
    reason: str = ""
    meetup_place: str = ""


class ConversationPayload(BaseModel):
    product_id: int


class MessagePayload(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    message_type: str = "text"


class ReviewPayload(BaseModel):
    score: int = Field(ge=1, le=5)
    content: str = Field(default="", max_length=512)


class ReportPayload(BaseModel):
    target_type: Literal["product", "user", "order"]
    target_id: int
    reason: str
    description: str = ""


class AuditProductPayload(BaseModel):
    action: Literal["approve", "reject", "off_shelf", "restore", "feature", "unfeature"]
    note: str = ""


class UserStatusPayload(BaseModel):
    status: Literal["active", "suspended", "banned"]
    reason: str = ""


class ReportHandlePayload(BaseModel):
    status: Literal["processing", "resolved", "rejected"]
    result: str


class CategoryPayload(BaseModel):
    name: str
    icon: str = "Box"
    color: str = "#2f7d32"
    sort_order: int = 0
    enabled: bool = True


class BannerPayload(BaseModel):
    title: str
    subtitle: str = ""
    image: str = ""
    link: str = ""
    sort_order: int = 0
    enabled: bool = True


class AnnouncementPayload(BaseModel):
    title: str
    content: str
    announcement_type: str = "notice"
    pinned: bool = False
    enabled: bool = True


class SettingPayload(BaseModel):
    values: dict[str, str]


def auth_error(detail: str = "请先登录") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def get_optional_user(
    authorization: str | None = Header(default=None), db: Session = Depends(get_db)
) -> User | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    payload = decode_access_token(authorization.split(" ", 1)[1])
    if not payload:
        return None
    user = db.get(User, int(payload["sub"]))
    if not user or user.status != "active":
        return None
    return user


def get_current_user(user: User | None = Depends(get_optional_user)) -> User:
    if not user:
        raise auth_error()
    return user


def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if user.role not in {"admin", "moderator"}:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


def add_audit_log(db: Session, admin: User, action: str, target_type: str, target_id: int, detail: str = "") -> None:
    db.add(AuditLog(operator_id=admin.id, action=action, target_type=target_type, target_id=target_id, detail=detail))


def get_product_or_404(db: Session, product_id: int) -> Product:
    item = db.scalar(
        select(Product)
        .where(Product.id == product_id)
        .options(joinedload(Product.seller), joinedload(Product.category))
    )
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    return item


def get_order_or_404(db: Session, order_id: int) -> Order:
    item = db.scalar(
        select(Order)
        .where(Order.id == order_id)
        .options(joinedload(Order.product).joinedload(Product.category), joinedload(Order.product).joinedload(Product.seller), joinedload(Order.buyer), joinedload(Order.seller))
    )
    if not item:
        raise HTTPException(status_code=404, detail="订单不存在")
    return item


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "campus-market-api", "time": iso(datetime.now())}


@app.post("/api/auth/register", status_code=201)
def register(payload: RegisterPayload, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(or_(User.username == payload.username, User.email == payload.email)))
    if exists:
        raise HTTPException(status_code=409, detail="用户名或邮箱已被使用")
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        nickname=payload.nickname,
        campus=payload.campus,
        student_no=payload.student_no,
        verified=bool(payload.student_no),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": create_access_token(user.id, user.role), "user": user_private(user)}


@app.post("/api/auth/login")
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(or_(User.username == payload.account, User.email == payload.account, User.phone == payload.account)))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="账号或密码错误")
    if user.status != "active":
        raise HTTPException(status_code=403, detail="账号已被停用，请联系管理员")
    user.last_login_at = datetime.now()
    db.commit()
    return {"token": create_access_token(user.id, user.role), "user": user_private(user)}


@app.get("/api/auth/me")
def me(user: User = Depends(get_current_user)):
    return user_private(user)


@app.put("/api/profile")
def update_profile(payload: ProfilePayload, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(user, key, value)
    if payload.student_no:
        user.verified = True
    db.commit()
    return user_private(user)


@app.get("/api/users/{user_id}")
def user_detail(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    product_count = db.scalar(select(func.count()).select_from(Product).where(Product.seller_id == user_id, Product.status.in_(["published", "sold"]))) or 0
    review_stats = db.execute(select(func.count(Review.id), func.avg(Review.score)).where(Review.reviewee_id == user_id)).one()
    return {**user_public(user), "product_count": product_count, "review_count": review_stats[0], "rating": round(review_stats[1] or 5, 1)}


@app.post("/api/upload")
def upload_image(file: UploadFile = File(...), _: User = Depends(get_current_user)):
    suffix = Path(file.filename or "image.jpg").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        raise HTTPException(status_code=400, detail="仅支持 JPG、PNG、WEBP、GIF 图片")
    filename = f"{datetime.now():%Y%m%d%H%M%S}-{secrets.token_hex(5)}{suffix}"
    target = UPLOAD_DIR / filename
    with target.open("wb") as stream:
        shutil.copyfileobj(file.file, stream)
    return {"url": f"/uploads/{filename}"}


@app.get("/api/categories")
def categories(include_disabled: bool = False, db: Session = Depends(get_db)):
    query = select(Category).order_by(Category.sort_order, Category.id)
    if not include_disabled:
        query = query.where(Category.enabled.is_(True))
    return [serialize_category(item) for item in db.scalars(query).all()]


@app.get("/api/home")
def home(user: User | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    favorite_ids: set[int] = set()
    if user:
        favorite_ids = set(db.scalars(select(Favorite.product_id).where(Favorite.user_id == user.id)).all())
    product_query = (
        select(Product)
        .where(Product.status == "published")
        .options(joinedload(Product.seller), joinedload(Product.category))
        .order_by(desc(Product.featured), desc(Product.created_at))
        .limit(12)
    )
    products = db.scalars(product_query).unique().all()
    banners = db.scalars(select(Banner).where(Banner.enabled.is_(True)).order_by(Banner.sort_order)).all()
    announcements = db.scalars(select(Announcement).where(Announcement.enabled.is_(True)).order_by(desc(Announcement.pinned), desc(Announcement.published_at)).limit(5)).all()
    return {
        "banners": [{"id": item.id, "title": item.title, "subtitle": item.subtitle, "image": item.image, "link": item.link} for item in banners],
        "announcements": [{"id": item.id, "title": item.title, "content": item.content, "type": item.announcement_type, "pinned": item.pinned, "published_at": iso(item.published_at)} for item in announcements],
        "categories": [serialize_category(item) for item in db.scalars(select(Category).where(Category.enabled.is_(True)).order_by(Category.sort_order)).all()],
        "products": [serialize_product(item, item.id in favorite_ids) for item in products],
    }


@app.get("/api/products")
def product_list(
    keyword: str = "",
    category_id: int | None = None,
    condition: str = "",
    campus: str = "",
    min_price: float | None = None,
    max_price: float | None = None,
    sort: Literal["latest", "price_asc", "price_desc", "popular", "recommended"] = "recommended",
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    filters = [Product.status == "published"]
    if keyword:
        filters.append(or_(Product.title.ilike(f"%{keyword}%"), Product.description.ilike(f"%{keyword}%")))
    if category_id:
        filters.append(Product.category_id == category_id)
    if condition:
        filters.append(Product.condition == condition)
    if campus:
        filters.append(Product.campus == campus)
    if min_price is not None:
        filters.append(Product.price >= min_price)
    if max_price is not None:
        filters.append(Product.price <= max_price)
    order_map = {
        "latest": [desc(Product.created_at)],
        "price_asc": [Product.price.asc()],
        "price_desc": [Product.price.desc()],
        "popular": [desc(Product.favorite_count), desc(Product.view_count)],
        "recommended": [desc(Product.featured), desc(Product.created_at)],
    }
    total = db.scalar(select(func.count()).select_from(Product).where(*filters)) or 0
    items = db.scalars(
        select(Product)
        .where(*filters)
        .options(joinedload(Product.seller), joinedload(Product.category))
        .order_by(*order_map[sort])
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).unique().all()
    favorite_ids: set[int] = set()
    if user:
        favorite_ids = set(db.scalars(select(Favorite.product_id).where(Favorite.user_id == user.id)).all())
    return {"items": [serialize_product(item, item.id in favorite_ids) for item in items], "total": total, "page": page, "page_size": page_size}


@app.get("/api/products/{product_id}")
def product_detail(product_id: int, user: User | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    item = get_product_or_404(db, product_id)
    if item.status != "published" and (not user or (user.id != item.seller_id and user.role not in {"admin", "moderator"})):
        raise HTTPException(status_code=404, detail="商品不存在或已下架")
    item.view_count += 1
    is_favorite = bool(user and db.scalar(select(Favorite).where(Favorite.user_id == user.id, Favorite.product_id == item.id)))
    similar = db.scalars(
        select(Product)
        .where(Product.category_id == item.category_id, Product.id != item.id, Product.status == "published")
        .options(joinedload(Product.seller), joinedload(Product.category))
        .order_by(desc(Product.created_at))
        .limit(4)
    ).unique().all()
    db.commit()
    return {"product": serialize_product(item, is_favorite), "similar": [serialize_product(product) for product in similar]}


@app.post("/api/products", status_code=201)
def create_product(payload: ProductPayload, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.get(Category, payload.category_id):
        raise HTTPException(status_code=400, detail="分类不存在")
    audit_required = db.scalar(select(SystemConfig.config_value).where(SystemConfig.config_key == "audit_required")) != "false"
    item = Product(
        **payload.model_dump(exclude={"images"}),
        images=json.dumps(payload.images, ensure_ascii=False),
        seller_id=user.id,
        status="pending" if audit_required and user.role == "user" else "published",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    get_product_or_404(db, item.id)
    return serialize_product(item)


@app.put("/api/products/{product_id}")
def update_product(product_id: int, payload: ProductPayload, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = get_product_or_404(db, product_id)
    if item.seller_id != user.id and user.role not in {"admin", "moderator"}:
        raise HTTPException(status_code=403, detail="无权修改该商品")
    for key, value in payload.model_dump(exclude={"images"}).items():
        setattr(item, key, value)
    item.images = json.dumps(payload.images, ensure_ascii=False)
    if user.role == "user":
        item.status = "pending"
    db.commit()
    return serialize_product(item)


@app.delete("/api/products/{product_id}")
def off_shelf_product(product_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = get_product_or_404(db, product_id)
    if item.seller_id != user.id and user.role not in {"admin", "moderator"}:
        raise HTTPException(status_code=403, detail="无权下架该商品")
    item.status = "off_shelf"
    db.commit()
    return {"message": "商品已下架"}


@app.post("/api/products/{product_id}/favorite")
def toggle_favorite(product_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = get_product_or_404(db, product_id)
    favorite = db.scalar(select(Favorite).where(Favorite.user_id == user.id, Favorite.product_id == product_id))
    if favorite:
        db.delete(favorite)
        item.favorite_count = max(0, item.favorite_count - 1)
        favorited = False
    else:
        db.add(Favorite(user_id=user.id, product_id=product_id))
        item.favorite_count += 1
        favorited = True
    db.commit()
    return {"favorited": favorited, "favorite_count": item.favorite_count}


@app.get("/api/favorites")
def favorites(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.scalars(
        select(Product)
        .join(Favorite, Favorite.product_id == Product.id)
        .where(Favorite.user_id == user.id)
        .options(joinedload(Product.seller), joinedload(Product.category))
        .order_by(desc(Favorite.created_at))
    ).unique().all()
    return [serialize_product(item, True) for item in items]


@app.get("/api/my/products")
def my_products(status_filter: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = select(Product).where(Product.seller_id == user.id).options(joinedload(Product.seller), joinedload(Product.category)).order_by(desc(Product.created_at))
    if status_filter:
        query = query.where(Product.status == status_filter)
    return [serialize_product(item) for item in db.scalars(query).unique().all()]


@app.post("/api/orders", status_code=201)
def create_order(payload: OrderCreatePayload, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = get_product_or_404(db, payload.product_id)
    if item.status != "published":
        raise HTTPException(status_code=400, detail="商品当前不可购买")
    if item.seller_id == user.id:
        raise HTTPException(status_code=400, detail="不能购买自己发布的商品")
    existing = db.scalar(select(Order).where(Order.product_id == item.id, Order.buyer_id == user.id, Order.status.in_(["pending", "paid", "meeting"])))
    if existing:
        raise HTTPException(status_code=409, detail="该商品已有进行中的订单")
    order_no = f"CM{datetime.now():%Y%m%d%H%M%S}{secrets.randbelow(100):02d}"
    order = Order(order_no=order_no, product_id=item.id, buyer_id=user.id, seller_id=item.seller_id, amount=item.price, meetup_place=payload.meetup_place or item.pickup_location, buyer_note=payload.buyer_note, pickup_code=f"{secrets.randbelow(900000) + 100000}")
    db.add(order)
    db.add(Notification(user_id=item.seller_id, title="收到新订单", content=f"{user.nickname} 想购买「{item.title}」，请及时处理。", notification_type="order"))
    db.commit()
    db.refresh(order)
    return serialize_order(get_order_or_404(db, order.id), user.id)


@app.get("/api/orders")
def order_list(role: Literal["all", "buyer", "seller"] = "all", status_filter: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conditions = []
    if role == "buyer":
        conditions.append(Order.buyer_id == user.id)
    elif role == "seller":
        conditions.append(Order.seller_id == user.id)
    else:
        conditions.append(or_(Order.buyer_id == user.id, Order.seller_id == user.id))
    if status_filter:
        conditions.append(Order.status == status_filter)
    query = select(Order).where(*conditions).options(joinedload(Order.product).joinedload(Product.category), joinedload(Order.product).joinedload(Product.seller), joinedload(Order.buyer), joinedload(Order.seller)).order_by(desc(Order.created_at))
    return [serialize_order(item, user.id) for item in db.scalars(query).unique().all()]


@app.get("/api/orders/{order_id}")
def order_detail(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = get_order_or_404(db, order_id)
    if user.id not in {item.buyer_id, item.seller_id} and user.role not in {"admin", "moderator"}:
        raise HTTPException(status_code=403, detail="无权查看该订单")
    return serialize_order(item, user.id)


@app.patch("/api/orders/{order_id}/status")
def update_order_status(order_id: int, payload: OrderActionPayload, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = get_order_or_404(db, order_id)
    if user.id not in {item.buyer_id, item.seller_id} and user.role not in {"admin", "moderator"}:
        raise HTTPException(status_code=403, detail="无权操作该订单")
    transitions = {
        "pay": ("pending", "paid"),
        "confirm_meetup": ("paid", "meeting"),
        "complete": ("meeting", "completed"),
        "cancel": (("pending", "paid"), "cancelled"),
        "refund": (("paid", "meeting"), "refunding"),
        "dispute": (("paid", "meeting", "refunding"), "disputed"),
    }
    allowed_from, target = transitions[payload.action]
    allowed_values = {allowed_from} if isinstance(allowed_from, str) else set(allowed_from)
    if item.status not in allowed_values:
        raise HTTPException(status_code=400, detail="当前订单状态不支持该操作")
    if payload.action == "pay" and user.id != item.buyer_id:
        raise HTTPException(status_code=403, detail="仅买家可付款")
    if payload.action == "complete" and user.id != item.buyer_id:
        raise HTTPException(status_code=403, detail="仅买家可确认完成")
    item.status = target
    if payload.meetup_place:
        item.meetup_place = payload.meetup_place
    if payload.action == "pay":
        item.paid_at = datetime.now()
    if payload.action == "complete":
        item.completed_at = datetime.now()
        item.product.status = "sold"
    if payload.action in {"cancel", "refund", "dispute"}:
        item.cancel_reason = payload.reason
    notify_user_id = item.seller_id if user.id == item.buyer_id else item.buyer_id
    db.add(Notification(user_id=notify_user_id, title="订单状态已更新", content=f"订单 {item.order_no} 已更新为 {target}。", notification_type="order"))
    db.commit()
    return serialize_order(item, user.id)


@app.post("/api/orders/{order_id}/reviews", status_code=201)
def create_review(order_id: int, payload: ReviewPayload, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = get_order_or_404(db, order_id)
    if item.status != "completed" or user.id not in {item.buyer_id, item.seller_id}:
        raise HTTPException(status_code=400, detail="仅已完成订单的交易双方可评价")
    if db.scalar(select(Review).where(Review.order_id == order_id, Review.reviewer_id == user.id)):
        raise HTTPException(status_code=409, detail="你已经评价过该订单")
    reviewee_id = item.seller_id if user.id == item.buyer_id else item.buyer_id
    review = Review(order_id=order_id, reviewer_id=user.id, reviewee_id=reviewee_id, score=payload.score, content=payload.content)
    db.add(review)
    db.commit()
    return {"id": review.id, "score": review.score, "content": review.content}


@app.post("/api/conversations")
def start_conversation(payload: ConversationPayload, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = get_product_or_404(db, payload.product_id)
    if product.seller_id == user.id:
        raise HTTPException(status_code=400, detail="不能与自己发起会话")
    item = db.scalar(select(Conversation).where(Conversation.product_id == product.id, Conversation.buyer_id == user.id, Conversation.seller_id == product.seller_id).options(joinedload(Conversation.product).joinedload(Product.category), joinedload(Conversation.product).joinedload(Product.seller), joinedload(Conversation.buyer), joinedload(Conversation.seller)))
    if not item:
        item = Conversation(product_id=product.id, buyer_id=user.id, seller_id=product.seller_id)
        db.add(item)
        db.commit()
        db.refresh(item)
        item = db.scalar(select(Conversation).where(Conversation.id == item.id).options(joinedload(Conversation.product).joinedload(Product.category), joinedload(Conversation.product).joinedload(Product.seller), joinedload(Conversation.buyer), joinedload(Conversation.seller)))
    return serialize_conversation(item, user.id)


@app.get("/api/conversations")
def conversation_list(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.scalars(select(Conversation).where(or_(Conversation.buyer_id == user.id, Conversation.seller_id == user.id)).options(joinedload(Conversation.product).joinedload(Product.category), joinedload(Conversation.product).joinedload(Product.seller), joinedload(Conversation.buyer), joinedload(Conversation.seller)).order_by(desc(Conversation.last_message_at))).unique().all()
    unread_counts = dict(db.execute(select(Message.conversation_id, func.count(Message.id)).join(Conversation, Conversation.id == Message.conversation_id).where(or_(Conversation.buyer_id == user.id, Conversation.seller_id == user.id), Message.sender_id != user.id, Message.is_read.is_(False)).group_by(Message.conversation_id)).all())
    return [{**serialize_conversation(item, user.id), "unread_count": unread_counts.get(item.id, 0)} for item in items]


@app.get("/api/conversations/{conversation_id}/messages")
def message_list(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.get(Conversation, conversation_id)
    if not conversation or user.id not in {conversation.buyer_id, conversation.seller_id}:
        raise HTTPException(status_code=404, detail="会话不存在")
    items = db.scalars(select(Message).where(Message.conversation_id == conversation_id).options(joinedload(Message.sender)).order_by(Message.created_at)).all()
    db.query(Message).filter(Message.conversation_id == conversation_id, Message.sender_id != user.id, Message.is_read.is_(False)).update({Message.is_read: True})
    db.commit()
    return [serialize_message(item) for item in items]


@app.post("/api/conversations/{conversation_id}/messages", status_code=201)
def send_message(conversation_id: int, payload: MessagePayload, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.get(Conversation, conversation_id)
    if not conversation or user.id not in {conversation.buyer_id, conversation.seller_id}:
        raise HTTPException(status_code=404, detail="会话不存在")
    item = Message(conversation_id=conversation_id, sender_id=user.id, content=payload.content, message_type=payload.message_type)
    conversation.last_message = payload.content[:256]
    conversation.last_message_at = datetime.now()
    db.add(item)
    db.commit()
    db.refresh(item)
    item = db.scalar(select(Message).where(Message.id == item.id).options(joinedload(Message.sender)))
    return serialize_message(item)


@app.get("/api/notifications")
def notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.scalars(select(Notification).where(Notification.user_id == user.id).order_by(desc(Notification.created_at)).limit(50)).all()
    return [{"id": item.id, "title": item.title, "content": item.content, "type": item.notification_type, "is_read": item.is_read, "created_at": iso(item.created_at)} for item in items]


@app.patch("/api/notifications/read-all")
def read_all_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read.is_(False)).update({Notification.is_read: True})
    db.commit()
    return {"message": "已全部标记为已读"}


@app.patch("/api/notifications/{notification_id}/read")
def read_notification(notification_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(Notification, notification_id)
    if not item or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="通知不存在")
    item.is_read = True
    db.commit()
    return {"message": "已读"}


@app.post("/api/reports", status_code=201)
def create_report(payload: ReportPayload, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = Report(reporter_id=user.id, **payload.model_dump())
    db.add(item)
    db.commit()
    return {"id": item.id, "status": item.status, "message": "举报已提交，平台将在 24 小时内处理"}


@app.get("/api/admin/dashboard")
def admin_dashboard(_: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    stats = {
        "users": db.scalar(select(func.count()).select_from(User)) or 0,
        "new_users_today": db.scalar(select(func.count()).select_from(User).where(User.created_at >= today)) or 0,
        "products": db.scalar(select(func.count()).select_from(Product)) or 0,
        "pending_products": db.scalar(select(func.count()).select_from(Product).where(Product.status == "pending")) or 0,
        "orders": db.scalar(select(func.count()).select_from(Order)) or 0,
        "trading_orders": db.scalar(select(func.count()).select_from(Order).where(Order.status.in_(["paid", "meeting"]))) or 0,
        "gmv": round(db.scalar(select(func.coalesce(func.sum(Order.amount), 0)).where(Order.status.in_(["paid", "meeting", "completed"]))) or 0, 2),
        "pending_reports": db.scalar(select(func.count()).select_from(Report).where(Report.status.in_(["pending", "processing"]))) or 0,
    }
    start = today - timedelta(days=6)
    rows = db.execute(select(func.date(Order.created_at), func.count(Order.id), func.coalesce(func.sum(Order.amount), 0)).where(Order.created_at >= start).group_by(func.date(Order.created_at))).all()
    order_map = {str(row[0]): {"orders": row[1], "gmv": float(row[2])} for row in rows}
    trend = []
    for offset in range(7):
        day = (start + timedelta(days=offset)).date().isoformat()
        trend.append({"date": day, **order_map.get(day, {"orders": 0, "gmv": 0})})
    categories = db.execute(select(Category.name, func.count(Product.id)).outerjoin(Product, Product.category_id == Category.id).group_by(Category.id).order_by(desc(func.count(Product.id)))).all()
    recent_orders = db.scalars(select(Order).options(joinedload(Order.product).joinedload(Product.category), joinedload(Order.product).joinedload(Product.seller), joinedload(Order.buyer), joinedload(Order.seller)).order_by(desc(Order.created_at)).limit(6)).unique().all()
    return {"stats": stats, "trend": trend, "categories": [{"name": row[0], "value": row[1]} for row in categories], "recent_orders": [serialize_order(item) for item in recent_orders]}


@app.get("/api/admin/users")
def admin_users(keyword: str = "", status_filter: str = "", role: str = "", page: int = 1, page_size: int = 20, _: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    filters = []
    if keyword:
        filters.append(or_(User.username.ilike(f"%{keyword}%"), User.nickname.ilike(f"%{keyword}%"), User.email.ilike(f"%{keyword}%"), User.student_no.ilike(f"%{keyword}%")))
    if status_filter:
        filters.append(User.status == status_filter)
    if role:
        filters.append(User.role == role)
    total = db.scalar(select(func.count()).select_from(User).where(*filters)) or 0
    users = db.scalars(select(User).where(*filters).order_by(desc(User.created_at)).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [user_private(item) for item in users], "total": total}


@app.patch("/api/admin/users/{user_id}/status")
def admin_user_status(user_id: int, payload: UserStatusPayload, request: Request, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    item = db.get(User, user_id)
    if not item:
        raise HTTPException(status_code=404, detail="用户不存在")
    if item.id == admin.id:
        raise HTTPException(status_code=400, detail="不能停用当前管理员账号")
    item.status = payload.status
    add_audit_log(db, admin, "更新用户状态", "user", item.id, f"{payload.status}: {payload.reason}")
    db.commit()
    return user_private(item)


@app.get("/api/admin/products")
def admin_products(keyword: str = "", status_filter: str = "", category_id: int | None = None, page: int = 1, page_size: int = 20, _: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    filters = []
    if keyword:
        filters.append(Product.title.ilike(f"%{keyword}%"))
    if status_filter:
        filters.append(Product.status == status_filter)
    if category_id:
        filters.append(Product.category_id == category_id)
    total = db.scalar(select(func.count()).select_from(Product).where(*filters)) or 0
    items = db.scalars(select(Product).where(*filters).options(joinedload(Product.seller), joinedload(Product.category)).order_by(desc(Product.created_at)).offset((page - 1) * page_size).limit(page_size)).unique().all()
    return {"items": [serialize_product(item) for item in items], "total": total}


@app.patch("/api/admin/products/{product_id}/audit")
def admin_product_audit(product_id: int, payload: AuditProductPayload, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    item = get_product_or_404(db, product_id)
    mapping = {"approve": "published", "reject": "rejected", "off_shelf": "off_shelf", "restore": "published"}
    if payload.action in mapping:
        item.status = mapping[payload.action]
        item.audit_note = payload.note
    elif payload.action == "feature":
        item.featured = True
    elif payload.action == "unfeature":
        item.featured = False
    db.add(Notification(user_id=item.seller_id, title="商品审核结果", content=f"「{item.title}」状态已更新为 {item.status}。{payload.note}", notification_type="product"))
    add_audit_log(db, admin, f"商品{payload.action}", "product", item.id, payload.note)
    db.commit()
    return serialize_product(item)


@app.get("/api/admin/orders")
def admin_orders(keyword: str = "", status_filter: str = "", page: int = 1, page_size: int = 20, _: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    filters = []
    if keyword:
        filters.append(Order.order_no.ilike(f"%{keyword}%"))
    if status_filter:
        filters.append(Order.status == status_filter)
    total = db.scalar(select(func.count()).select_from(Order).where(*filters)) or 0
    items = db.scalars(select(Order).where(*filters).options(joinedload(Order.product).joinedload(Product.category), joinedload(Order.product).joinedload(Product.seller), joinedload(Order.buyer), joinedload(Order.seller)).order_by(desc(Order.created_at)).offset((page - 1) * page_size).limit(page_size)).unique().all()
    return {"items": [serialize_order(item) for item in items], "total": total}


@app.get("/api/admin/reports")
def admin_reports(status_filter: str = "", target_type: str = "", page: int = 1, page_size: int = 20, _: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    filters = []
    if status_filter:
        filters.append(Report.status == status_filter)
    if target_type:
        filters.append(Report.target_type == target_type)
    total = db.scalar(select(func.count()).select_from(Report).where(*filters)) or 0
    items = db.scalars(select(Report).where(*filters).options(joinedload(Report.reporter), joinedload(Report.handler)).order_by(desc(Report.created_at)).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"id": item.id, "reporter": user_public(item.reporter), "target_type": item.target_type, "target_id": item.target_id, "reason": item.reason, "description": item.description, "status": item.status, "handler": user_public(item.handler), "result": item.result, "created_at": iso(item.created_at), "handled_at": iso(item.handled_at)} for item in items], "total": total}


@app.patch("/api/admin/reports/{report_id}")
def handle_report(report_id: int, payload: ReportHandlePayload, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    item = db.get(Report, report_id)
    if not item:
        raise HTTPException(status_code=404, detail="举报不存在")
    item.status = payload.status
    item.result = payload.result
    item.handler_id = admin.id
    item.handled_at = datetime.now() if payload.status in {"resolved", "rejected"} else None
    db.add(Notification(user_id=item.reporter_id, title="举报处理进展", content=f"你的举报已更新为 {payload.status}：{payload.result}", notification_type="report"))
    add_audit_log(db, admin, "处理举报", "report", item.id, payload.result)
    db.commit()
    return {"id": item.id, "status": item.status, "result": item.result}


@app.get("/api/admin/categories")
def admin_categories(_: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    rows = db.execute(select(Category, func.count(Product.id)).outerjoin(Product, Product.category_id == Category.id).group_by(Category.id).order_by(Category.sort_order)).all()
    return [{**serialize_category(item), "product_count": count} for item, count in rows]


@app.post("/api/admin/categories", status_code=201)
def create_category(payload: CategoryPayload, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    item = Category(**payload.model_dump())
    db.add(item)
    db.flush()
    add_audit_log(db, admin, "创建分类", "category", item.id, item.name)
    db.commit()
    return serialize_category(item)


@app.put("/api/admin/categories/{category_id}")
def update_category(category_id: int, payload: CategoryPayload, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    item = db.get(Category, category_id)
    if not item:
        raise HTTPException(status_code=404, detail="分类不存在")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    add_audit_log(db, admin, "更新分类", "category", item.id, item.name)
    db.commit()
    return serialize_category(item)


@app.get("/api/admin/banners")
def admin_banners(_: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    items = db.scalars(select(Banner).order_by(Banner.sort_order)).all()
    return [{"id": item.id, "title": item.title, "subtitle": item.subtitle, "image": item.image, "link": item.link, "sort_order": item.sort_order, "enabled": item.enabled, "created_at": iso(item.created_at)} for item in items]


@app.post("/api/admin/banners", status_code=201)
def create_banner(payload: BannerPayload, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    item = Banner(**payload.model_dump())
    db.add(item)
    db.flush()
    add_audit_log(db, admin, "创建轮播", "banner", item.id, item.title)
    db.commit()
    return {"id": item.id, **payload.model_dump()}


@app.put("/api/admin/banners/{banner_id}")
def update_banner(banner_id: int, payload: BannerPayload, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    item = db.get(Banner, banner_id)
    if not item:
        raise HTTPException(status_code=404, detail="轮播不存在")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    add_audit_log(db, admin, "更新轮播", "banner", item.id, item.title)
    db.commit()
    return {"id": item.id, **payload.model_dump()}


@app.get("/api/admin/announcements")
def admin_announcements(_: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    items = db.scalars(select(Announcement).order_by(desc(Announcement.published_at))).all()
    return [{"id": item.id, "title": item.title, "content": item.content, "announcement_type": item.announcement_type, "pinned": item.pinned, "enabled": item.enabled, "published_at": iso(item.published_at)} for item in items]


@app.post("/api/admin/announcements", status_code=201)
def create_announcement(payload: AnnouncementPayload, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    item = Announcement(**payload.model_dump())
    db.add(item)
    db.flush()
    add_audit_log(db, admin, "发布公告", "announcement", item.id, item.title)
    db.commit()
    return {"id": item.id, **payload.model_dump(), "published_at": iso(item.published_at)}


@app.get("/api/admin/settings")
def admin_settings(_: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    return {item.config_key: {"value": item.config_value, "description": item.description, "updated_at": iso(item.updated_at)} for item in db.scalars(select(SystemConfig).order_by(SystemConfig.config_key)).all()}


@app.put("/api/admin/settings")
def update_settings(payload: SettingPayload, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    for key, value in payload.values.items():
        item = db.scalar(select(SystemConfig).where(SystemConfig.config_key == key))
        if item:
            item.config_value = value
        else:
            db.add(SystemConfig(config_key=key, config_value=value))
    add_audit_log(db, admin, "更新系统设置", "system", 0, json.dumps(payload.values, ensure_ascii=False))
    db.commit()
    return {"message": "设置已保存"}


@app.get("/api/admin/audit-logs")
def audit_logs(page: int = 1, page_size: int = 30, _: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(AuditLog)) or 0
    items = db.scalars(select(AuditLog).options(joinedload(AuditLog.operator)).order_by(desc(AuditLog.created_at)).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"id": item.id, "operator": user_public(item.operator), "action": item.action, "target_type": item.target_type, "target_id": item.target_id, "detail": item.detail, "ip_address": item.ip_address, "created_at": iso(item.created_at)} for item in items], "total": total}

