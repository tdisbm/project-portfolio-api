import json
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import RequestFactory

from apps.project.decorators import queryable
from apps.project.models import Project

factory = RequestFactory()


# --- Test views ---


@queryable(
    serializer=lambda p: {"name": p.name},
    filter_by_map={
        "name__icontains": "name",
        "technologies_used__contains": ("technology", lambda v: [v]),
    },
    order_by_map={"name": "order_by_name", "date_start": "order_by_date_start"},
    default_page_size=5,
)
def _view(request: HttpRequest) -> Any:
    return Project.objects.filter(user=request.user)


@queryable(serializer=lambda p: {"name": p.name}, default_page_size=10)
def _view_no_request() -> Any:
    return Project.objects.none()


def _req(user: User, params: dict | None = None) -> HttpRequest:
    request = factory.get("/", params or {})
    request.user = user  # type: ignore[attr-defined]
    return request


def _json(response: Any) -> Any:
    return json.loads(response.content)


# --- Fixtures ---


@pytest.fixture
def quser(db: Any) -> User:
    return User.objects.create_user(username="quser", password="pass")


@pytest.fixture
def qproject(quser: User) -> Any:
    def _make(**kwargs: Any) -> Project:
        defaults: dict[str, Any] = {
            "user": quser,
            "name": "Test",
            "technologies_used": [],
            "date_start": "2024-01-01",
        }
        defaults.update(kwargs)
        return Project.objects.create(**defaults)

    return _make


# --- Pagination / response shape ---


@pytest.mark.django_db
def test_returns_paginated_response_shape(quser: User, qproject: Any) -> None:
    qproject(name="A")
    qproject(name="B")
    data = _json(_view(_req(quser)))
    assert set(data.keys()) == {"count", "total_pages", "page", "page_size", "results"}
    assert data["count"] == 2


@pytest.mark.django_db
def test_default_page_size_limits_results(quser: User, qproject: Any) -> None:
    for i in range(7):
        qproject(name=f"P{i}")
    data = _json(_view(_req(quser)))
    assert len(data["results"]) == 5  # default_page_size=5
    assert data["count"] == 7


@pytest.mark.django_db
def test_page_size_param_is_respected(quser: User, qproject: Any) -> None:
    for i in range(6):
        qproject(name=f"P{i}")
    data = _json(_view(_req(quser, {"page_size": 3})))
    assert len(data["results"]) == 3
    assert data["total_pages"] == 2


@pytest.mark.django_db
def test_page_param_returns_correct_slice(quser: User, qproject: Any) -> None:
    for i in range(8):
        qproject(name=f"P{i}")
    data = _json(_view(_req(quser, {"page": 2, "page_size": 5})))
    assert data["page"] == 2
    assert len(data["results"]) == 3


# --- Filtering ---


@pytest.mark.django_db
def test_filter_by_plain_param(quser: User, qproject: Any) -> None:
    qproject(name="Django API")
    qproject(name="React UI")
    data = _json(_view(_req(quser, {"name": "django"})))
    assert data["count"] == 1
    assert data["results"][0]["name"] == "Django API"


@pytest.mark.django_db
def test_filter_absent_param_returns_all(quser: User, qproject: Any) -> None:
    qproject(name="A")
    qproject(name="B")
    assert _json(_view(_req(quser)))["count"] == 2


@pytest.mark.django_db
def test_filter_with_transform_single_value(quser: User, qproject: Any) -> None:
    qproject(name="A", technologies_used=["Python"])
    qproject(name="B", technologies_used=["Go"])
    data = _json(_view(_req(quser, {"technology": "Python"})))
    assert data["count"] == 1


@pytest.mark.django_db
def test_filter_with_transform_multiple_values_uses_or(quser: User, qproject: Any) -> None:
    qproject(name="A", technologies_used=["Python"])
    qproject(name="B", technologies_used=["Go"])
    qproject(name="C", technologies_used=["Rust"])
    request = factory.get("/", {"technology": ["Python", "Go"]})
    request.user = quser  # type: ignore[attr-defined]
    data = _json(_view(request))
    assert data["count"] == 2
    assert {r["name"] for r in data["results"]} == {"A", "B"}


# --- Ordering ---


@pytest.mark.django_db
def test_order_by_asc(quser: User, qproject: Any) -> None:
    qproject(name="Zebra")
    qproject(name="Apple")
    names = [r["name"] for r in _json(_view(_req(quser, {"order_by_name": "asc"})))["results"]]
    assert names == ["Apple", "Zebra"]


@pytest.mark.django_db
def test_order_by_desc(quser: User, qproject: Any) -> None:
    qproject(name="Zebra")
    qproject(name="Apple")
    names = [r["name"] for r in _json(_view(_req(quser, {"order_by_name": "desc"})))["results"]]
    assert names == ["Zebra", "Apple"]


# --- View signature variants ---


@pytest.mark.django_db
def test_view_without_request_param_works(db: Any) -> None:
    request = factory.get("/")
    data = _json(_view_no_request(request))
    assert data["count"] == 0
