from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from . import models


def iso(value: datetime | None) -> str | None:
    return value.isoformat(timespec="seconds") if value else None


def parse_images(value: str | None) -> list[str]:
    try:
        return json.loads(value or "[]")
    except json.JSONDecodeError:
        return []


def user_public(user: models.User | None) -> dict[str, Any] | None:
    if not user:
        return None
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "campus": user.campus,
        "verified": user.verified,
        "credit_score": user.credit_score,
        "bio": user.bio,
        "created_at": iso(user.created_at),
    }


def user_private(user: models.User) -> dict[str, Any]:
    return {
        **user_public(user),
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "student_no": user.student_no,
        "status": user.status,
        "last_login_at": iso(user.last_login_at),
    }


def category(category: models.Category) -> dict[str, Any]:
    return {
        "id": category.id,
        "name": category.name,
        "icon": category.icon,
        "color": category.color,
        "sort_order": category.sort_order,
        "enabled": category.enabled,
    }


def product(item: models.Product, is_favorite: bool = False) -> dict[str, Any]:
    return {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "price": item.price,
        "original_price": item.original_price,
        "condition": item.condition,
        "category_id": item.category_id,
        "category": category(item.category) if item.category else None,
        "seller_id": item.seller_id,
        "seller": user_public(item.seller),
        "campus": item.campus,
        "pickup_location": item.pickup_location,
        "transaction_method": item.transaction_method,
        "images": parse_images(item.images),
        "status": item.status,
        "audit_note": item.audit_note,
        "view_count": item.view_count,
        "favorite_count": item.favorite_count,
        "featured": item.featured,
        "is_favorite": is_favorite,
        "created_at": iso(item.created_at),
        "updated_at": iso(item.updated_at),
    }


def order(item: models.Order, current_user_id: int | None = None) -> dict[str, Any]:
    return {
        "id": item.id,
        "order_no": item.order_no,
        "product_id": item.product_id,
        "product": product(item.product) if item.product else None,
        "buyer": user_public(item.buyer),
        "seller": user_public(item.seller),
        "amount": item.amount,
        "status": item.status,
        "pickup_code": item.pickup_code if current_user_id in {item.buyer_id, item.seller_id} else "",
        "meetup_place": item.meetup_place,
        "buyer_note": item.buyer_note,
        "cancel_reason": item.cancel_reason,
        "created_at": iso(item.created_at),
        "paid_at": iso(item.paid_at),
        "completed_at": iso(item.completed_at),
        "perspective": "buyer" if current_user_id == item.buyer_id else "seller",
    }


def conversation(item: models.Conversation, current_user_id: int) -> dict[str, Any]:
    other = item.seller if current_user_id == item.buyer_id else item.buyer
    return {
        "id": item.id,
        "product": product(item.product) if item.product else None,
        "buyer_id": item.buyer_id,
        "seller_id": item.seller_id,
        "other_user": user_public(other),
        "last_message": item.last_message,
        "last_message_at": iso(item.last_message_at),
        "created_at": iso(item.created_at),
    }


def message(item: models.Message) -> dict[str, Any]:
    return {
        "id": item.id,
        "conversation_id": item.conversation_id,
        "sender_id": item.sender_id,
        "sender": user_public(item.sender),
        "content": item.content,
        "message_type": item.message_type,
        "is_read": item.is_read,
        "created_at": iso(item.created_at),
    }

