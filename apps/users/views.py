from __future__ import annotations

import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.users.decorators import require_auth
from apps.users.repository import token as token_repo
from apps.users.serializers import serialize_user


@csrf_exempt
@require_http_methods(["POST"])
def register(request: HttpRequest) -> HttpResponse:
    body = json.loads(request.body)
    user, token = token_repo.register(body)
    return JsonResponse({"token": token.token, "user": serialize_user(user)}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def login(request: HttpRequest) -> HttpResponse:
    body = json.loads(request.body)
    user = token_repo.get_by_credentials(body.get("username", ""), body.get("password", ""))
    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    token = token_repo.create_token(user)
    return JsonResponse({"token": token.token, "user": serialize_user(user)})


@csrf_exempt
@require_auth
@require_http_methods(["POST"])
def logout(request: HttpRequest) -> HttpResponse:
    token_value = request.META.get("HTTP_AUTHORIZATION", "")[len("Bearer ") :]
    token_repo.delete_token(token_value)
    return HttpResponse(status=204)


@require_auth
@require_http_methods(["GET"])
def me(request: HttpRequest) -> HttpResponse:
    return JsonResponse(serialize_user(request.user))
