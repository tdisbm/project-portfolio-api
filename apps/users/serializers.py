from __future__ import annotations

from typing import Any

from django.contrib.auth.models import User


def serialize_user(user: User) -> dict[str, Any]:
    return {
        "id": user.pk,
        "username": user.username,
    }


def validate_register_data(data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    cleaned: dict[str, Any] = {}

    username = (data.get("username") or "").strip()
    if not username:
        errors.append("username is required")
    elif len(username) > 150:
        errors.append("username must be at most 150 characters")
    else:
        cleaned["username"] = username

    password = data.get("password") or ""
    if not password:
        errors.append("password is required")
    elif len(password) < 8:
        errors.append("password must be at least 8 characters")
    else:
        cleaned["password"] = password

    return cleaned, errors
