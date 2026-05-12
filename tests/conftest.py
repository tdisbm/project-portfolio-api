import pytest
from django.contrib.auth.models import User
from django.test import Client

from apps.project.models import Project
from apps.users.models import AuthToken


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def other_user(db) -> User:
    return User.objects.create_user(username="otheruser", password="testpass123")


@pytest.fixture
def token(user) -> AuthToken:
    return AuthToken.objects.create(user=user, token=AuthToken.generate_token())


@pytest.fixture
def other_token(other_user) -> AuthToken:
    return AuthToken.objects.create(user=other_user, token=AuthToken.generate_token())


@pytest.fixture
def auth_client(client: Client, token: AuthToken) -> Client:
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token.token}"
    return client


@pytest.fixture
def other_auth_client(other_token: AuthToken) -> Client:
    c = Client()
    c.defaults["HTTP_AUTHORIZATION"] = f"Bearer {other_token.token}"
    return c


@pytest.fixture
def make_project(user: User):
    def _make(owner: User | None = None, **kwargs: object) -> Project:
        defaults: dict[str, object] = {
            "user": owner if owner is not None else user,
            "name": "Test Project",
            "description": "A test description",
            "technologies_used": ["Python"],
            "date_start": "2024-01-01",
        }
        defaults.update(kwargs)
        return Project.objects.create(**defaults)

    return _make
