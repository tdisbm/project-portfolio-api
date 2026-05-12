from __future__ import annotations

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from apps.users.models import AuthToken
from apps.users.serializers import validate_register_data


def register(data: dict) -> tuple[User, AuthToken]:
    cleaned, errors = validate_register_data(data)
    if errors:
        raise ValidationError(errors)
    if User.objects.filter(username=cleaned["username"]).exists():
        raise ValidationError(["username already taken"])
    user = User.objects.create_user(username=cleaned["username"], password=cleaned["password"])
    return user, _create_token(user)


def get_by_credentials(username: str, password: str) -> User | None:
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None
    return user if user.check_password(password) else None


def create_token(user: User) -> AuthToken:
    return _create_token(user)


def get_token_with_user(token_value: str) -> AuthToken | None:
    try:
        return AuthToken.objects.select_related("user").get(token=token_value)
    except AuthToken.DoesNotExist:
        return None


def delete_token(token_value: str) -> None:
    AuthToken.objects.filter(token=token_value).delete()


def _create_token(user: User) -> AuthToken:
    return AuthToken.objects.create(user=user, token=AuthToken.generate_token())
