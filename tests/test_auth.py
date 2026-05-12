import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from apps.users.models import AuthToken

# --- Register ---


@pytest.mark.django_db
def test_register_creates_user_and_returns_token(client: Client) -> None:
    response = client.post(
        reverse("users:register"),
        data={"username": "newuser", "password": "securepass"},
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert data["user"]["username"] == "newuser"
    assert User.objects.filter(username="newuser").exists()
    assert AuthToken.objects.filter(user__username="newuser").exists()


@pytest.mark.django_db
def test_register_auto_logs_in(client: Client) -> None:
    response = client.post(
        reverse("users:register"),
        data={"username": "newuser", "password": "securepass"},
        content_type="application/json",
    )
    token = response.json()["token"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    me_response = client.get(reverse("users:me"))
    assert me_response.status_code == 200


@pytest.mark.django_db
def test_register_duplicate_username_returns_422(client: Client, user: User) -> None:
    response = client.post(
        reverse("users:register"),
        data={"username": "testuser", "password": "securepass"},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert any("already taken" in e for e in response.json()["errors"])


@pytest.mark.django_db
def test_register_short_password_returns_422(client: Client) -> None:
    response = client.post(
        reverse("users:register"),
        data={"username": "someone", "password": "short"},
        content_type="application/json",
    )
    assert response.status_code == 422


@pytest.mark.django_db
def test_register_missing_username_returns_422(client: Client) -> None:
    response = client.post(
        reverse("users:register"),
        data={"password": "securepass"},
        content_type="application/json",
    )
    assert response.status_code == 422


@pytest.mark.django_db
def test_register_invalid_json_returns_400(client: Client) -> None:
    response = client.post(
        reverse("users:register"),
        data="not json",
        content_type="application/json",
    )
    assert response.status_code == 400


# --- Login ---


@pytest.mark.django_db
def test_login_valid_credentials_returns_token(client: Client, user: User) -> None:
    response = client.post(
        reverse("users:login"),
        data={"username": "testuser", "password": "testpass123"},
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["username"] == "testuser"
    assert AuthToken.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_login_wrong_password_returns_401(client: Client, user: User) -> None:
    response = client.post(
        reverse("users:login"),
        data={"username": "testuser", "password": "wrongpass"},
        content_type="application/json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_login_unknown_user_returns_401(client: Client) -> None:
    response = client.post(
        reverse("users:login"),
        data={"username": "nobody", "password": "pass"},
        content_type="application/json",
    )
    assert response.status_code == 401


# --- Logout ---


@pytest.mark.django_db
def test_logout_revokes_token(auth_client: Client, token: AuthToken) -> None:
    response = auth_client.post(reverse("users:logout"), content_type="application/json")
    assert response.status_code == 204
    assert not AuthToken.objects.filter(pk=token.pk).exists()


@pytest.mark.django_db
def test_logout_requires_auth(client: Client) -> None:
    response = client.post(reverse("users:logout"), content_type="application/json")
    assert response.status_code == 401


# --- Me ---


@pytest.mark.django_db
def test_me_returns_current_user(auth_client: Client, user: User) -> None:
    response = auth_client.get(reverse("users:me"))
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.pk
    assert data["username"] == user.username


@pytest.mark.django_db
def test_me_requires_auth(client: Client) -> None:
    response = client.get(reverse("users:me"))
    assert response.status_code == 401
