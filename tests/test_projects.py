from collections.abc import Callable

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from apps.project.models import Project

# --- List ---


@pytest.mark.django_db
def test_list_requires_auth(client: Client) -> None:
    response = client.get(reverse("project:project-list"))
    assert response.status_code == 401


@pytest.mark.django_db
def test_list_returns_empty_for_new_user(auth_client: Client) -> None:
    response = auth_client.get(reverse("project:project-list"))
    assert response.status_code == 200
    assert response.json()["count"] == 0


@pytest.mark.django_db
def test_list_returns_only_own_projects(
    auth_client: Client, make_project: Callable, other_user: User
) -> None:
    make_project(name="Mine")
    make_project(owner=other_user, name="Theirs")
    data = auth_client.get(reverse("project:project-list")).json()
    assert data["count"] == 1
    assert data["results"][0]["name"] == "Mine"


@pytest.mark.django_db
def test_list_pagination(auth_client: Client, make_project: Callable) -> None:
    for i in range(12):
        make_project(name=f"Project {i}")
    response = auth_client.get(reverse("project:project-list"), {"page": 1, "page_size": 10})
    data = response.json()
    assert data["count"] == 12
    assert data["total_pages"] == 2
    assert len(data["results"]) == 10
    page2 = auth_client.get(reverse("project:project-list"), {"page": 2, "page_size": 10}).json()
    assert len(page2["results"]) == 2


@pytest.mark.django_db
def test_filter_by_name(auth_client: Client, make_project: Callable) -> None:
    make_project(name="Django App")
    make_project(name="React UI")
    data = auth_client.get(reverse("project:project-list"), {"name": "django"}).json()
    assert data["count"] == 1
    assert data["results"][0]["name"] == "Django App"


@pytest.mark.django_db
def test_filter_by_description(auth_client: Client, make_project: Callable) -> None:
    make_project(name="A", description="backend service")
    make_project(name="B", description="frontend app")
    data = auth_client.get(reverse("project:project-list"), {"description": "backend"}).json()
    assert data["count"] == 1
    assert data["results"][0]["name"] == "A"


@pytest.mark.django_db
def test_filter_by_single_technology(auth_client: Client, make_project: Callable) -> None:
    make_project(name="A", technologies_used=["Python", "Django"])
    make_project(name="B", technologies_used=["JavaScript"])
    data = auth_client.get(reverse("project:project-list"), {"technology": "Django"}).json()
    assert data["count"] == 1
    assert data["results"][0]["name"] == "A"


@pytest.mark.django_db
def test_filter_by_multiple_technologies_uses_or_logic(
    auth_client: Client, make_project: Callable
) -> None:
    make_project(name="A", technologies_used=["Python"])
    make_project(name="B", technologies_used=["JavaScript"])
    make_project(name="C", technologies_used=["Go"])
    data = auth_client.get(
        reverse("project:project-list"), {"technology": ["Python", "JavaScript"]}
    ).json()
    assert data["count"] == 2
    assert {r["name"] for r in data["results"]} == {"A", "B"}


@pytest.mark.django_db
def test_filter_by_date_start_after(auth_client: Client, make_project: Callable) -> None:
    make_project(name="Old", date_start="2022-01-01")
    make_project(name="New", date_start="2024-06-01")
    data = auth_client.get(
        reverse("project:project-list"), {"date_start_after": "2024-01-01"}
    ).json()
    assert data["count"] == 1
    assert data["results"][0]["name"] == "New"


@pytest.mark.django_db
def test_filter_by_date_end_before(auth_client: Client, make_project: Callable) -> None:
    make_project(name="A", date_start="2023-01-01", date_end="2023-06-01")
    make_project(name="B", date_start="2023-01-01", date_end="2025-01-01")
    make_project(name="C", date_start="2023-01-01")  # no end date
    data = auth_client.get(
        reverse("project:project-list"), {"date_end_before": "2024-01-01"}
    ).json()
    assert data["count"] == 1
    assert data["results"][0]["name"] == "A"


@pytest.mark.django_db
def test_sort_by_name_asc(auth_client: Client, make_project: Callable) -> None:
    make_project(name="Zebra")
    make_project(name="Apple")
    data = auth_client.get(reverse("project:project-list"), {"order_by_name": "asc"}).json()
    names = [r["name"] for r in data["results"]]
    assert names == ["Apple", "Zebra"]


@pytest.mark.django_db
def test_sort_by_name_desc(auth_client: Client, make_project: Callable) -> None:
    make_project(name="Zebra")
    make_project(name="Apple")
    data = auth_client.get(reverse("project:project-list"), {"order_by_name": "desc"}).json()
    names = [r["name"] for r in data["results"]]
    assert names == ["Zebra", "Apple"]


# --- Create ---


@pytest.mark.django_db
def test_create_requires_auth(client: Client) -> None:
    response = client.post(
        reverse("project:project-create"), data={}, content_type="application/json"
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_happy_path(auth_client: Client, user: User) -> None:
    payload = {
        "name": "New Project",
        "description": "Desc",
        "technologies_used": ["Python"],
        "date_start": "2024-01-01",
    }
    response = auth_client.post(
        reverse("project:project-create"), data=payload, content_type="application/json"
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Project"
    project = Project.objects.get(pk=data["id"])
    assert project.user == user


@pytest.mark.django_db
def test_create_validation_error_returns_422(auth_client: Client) -> None:
    response = auth_client.post(
        reverse("project:project-create"),
        data={"description": "missing name and date"},
        content_type="application/json",
    )
    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("name" in e for e in errors)
    assert any("date_start" in e for e in errors)


@pytest.mark.django_db
def test_create_date_end_before_date_start_returns_422(auth_client: Client) -> None:
    response = auth_client.post(
        reverse("project:project-create"),
        data={"name": "X", "date_start": "2024-06-01", "date_end": "2024-01-01"},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert any("date_end" in e for e in response.json()["errors"])


@pytest.mark.django_db
def test_create_invalid_json_returns_400(auth_client: Client) -> None:
    response = auth_client.post(
        reverse("project:project-create"), data="not json", content_type="application/json"
    )
    assert response.status_code == 400


# --- Retrieve ---


@pytest.mark.django_db
def test_retrieve_own_project(auth_client: Client, make_project: Callable) -> None:
    project = make_project(name="Mine")
    response = auth_client.get(reverse("project:project-retrieve", args=[project.pk]))
    assert response.status_code == 200
    assert response.json()["name"] == "Mine"


@pytest.mark.django_db
def test_retrieve_other_users_project_returns_404(
    auth_client: Client, make_project: Callable, other_user: User
) -> None:
    project = make_project(owner=other_user, name="Theirs")
    response = auth_client.get(reverse("project:project-retrieve", args=[project.pk]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_retrieve_nonexistent_project_returns_404(auth_client: Client) -> None:
    response = auth_client.get(reverse("project:project-retrieve", args=[99999]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_retrieve_requires_auth(client: Client, make_project: Callable) -> None:
    project = make_project()
    response = client.get(reverse("project:project-retrieve", args=[project.pk]))
    assert response.status_code == 401


# --- Update (PATCH) ---


@pytest.mark.django_db
def test_patch_own_project(auth_client: Client, make_project: Callable) -> None:
    project = make_project(name="Original")
    response = auth_client.patch(
        reverse("project:project-update", args=[project.pk]),
        data={"name": "Updated"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"
    project.refresh_from_db()
    assert project.name == "Updated"


@pytest.mark.django_db
def test_patch_does_not_change_untouched_fields(
    auth_client: Client, make_project: Callable
) -> None:
    project = make_project(name="Original", description="Keep this")
    auth_client.patch(
        reverse("project:project-update", args=[project.pk]),
        data={"name": "Updated"},
        content_type="application/json",
    )
    project.refresh_from_db()
    assert project.description == "Keep this"


@pytest.mark.django_db
def test_patch_other_users_project_returns_404(
    auth_client: Client, make_project: Callable, other_user: User
) -> None:
    project = make_project(owner=other_user)
    response = auth_client.patch(
        reverse("project:project-update", args=[project.pk]),
        data={"name": "Hacked"},
        content_type="application/json",
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_patch_requires_auth(client: Client, make_project: Callable) -> None:
    project = make_project()
    response = client.patch(
        reverse("project:project-update", args=[project.pk]),
        data={"name": "X"},
        content_type="application/json",
    )
    assert response.status_code == 401


# --- Delete ---


@pytest.mark.django_db
def test_delete_own_project(auth_client: Client, make_project: Callable) -> None:
    project = make_project()
    response = auth_client.delete(reverse("project:project-delete", args=[project.pk]))
    assert response.status_code == 204
    assert not Project.objects.filter(pk=project.pk).exists()


@pytest.mark.django_db
def test_delete_other_users_project_returns_404(
    auth_client: Client, make_project: Callable, other_user: User
) -> None:
    project = make_project(owner=other_user)
    response = auth_client.delete(reverse("project:project-delete", args=[project.pk]))
    assert response.status_code == 404
    assert Project.objects.filter(pk=project.pk).exists()


@pytest.mark.django_db
def test_delete_requires_auth(client: Client, make_project: Callable) -> None:
    project = make_project()
    response = client.delete(reverse("project:project-delete", args=[project.pk]))
    assert response.status_code == 401
