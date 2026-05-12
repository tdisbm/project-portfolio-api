import pytest
from django.contrib.auth.models import User

from apps.users.serializers import serialize_user, validate_register_data

# --- validate_register_data ---


def test_valid_data_returns_cleaned_and_no_errors() -> None:
    cleaned, errors = validate_register_data({"username": "alice", "password": "securepass"})
    assert not errors
    assert cleaned == {"username": "alice", "password": "securepass"}


def test_username_is_stripped() -> None:
    cleaned, errors = validate_register_data({"username": "  alice  ", "password": "securepass"})
    assert not errors
    assert cleaned["username"] == "alice"


def test_missing_username() -> None:
    _, errors = validate_register_data({"password": "securepass"})
    assert any("username" in e for e in errors)


def test_blank_username() -> None:
    _, errors = validate_register_data({"username": "   ", "password": "securepass"})
    assert any("username" in e for e in errors)


def test_username_at_max_length_is_valid() -> None:
    _, errors = validate_register_data({"username": "a" * 150, "password": "securepass"})
    assert not errors


def test_username_over_max_length() -> None:
    _, errors = validate_register_data({"username": "a" * 151, "password": "securepass"})
    assert any("150" in e for e in errors)


def test_missing_password() -> None:
    _, errors = validate_register_data({"username": "alice"})
    assert any("password" in e for e in errors)


def test_password_at_min_length_is_valid() -> None:
    _, errors = validate_register_data({"username": "alice", "password": "exactly8"})
    assert not errors


def test_password_too_short() -> None:
    _, errors = validate_register_data({"username": "alice", "password": "short"})
    assert any("8" in e for e in errors)


def test_empty_payload_returns_multiple_errors() -> None:
    _, errors = validate_register_data({})
    assert len(errors) >= 2


# --- serialize_user ---


@pytest.mark.django_db
def test_serialize_user() -> None:
    user = User.objects.create_user(username="bob", password="pass")
    data = serialize_user(user)
    assert data == {"id": user.pk, "username": "bob"}
