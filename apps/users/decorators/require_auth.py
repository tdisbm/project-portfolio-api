from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from django.http import HttpRequest, JsonResponse

from apps.users.repository import token as token_repo


def require_auth(view_func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Authentication required"}, status=401)

        token_value = auth_header[len("Bearer ") :]
        auth_token = token_repo.get_token_with_user(token_value)
        if auth_token is None:
            return JsonResponse({"error": "Invalid or expired token"}, status=401)

        request.user = auth_token.user
        return view_func(request, *args, **kwargs)

    return wrapper
