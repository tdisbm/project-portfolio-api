from datetime import date

import pytest
from django.contrib.auth.models import User

from apps.project.models import Project
from apps.project.serializers import serialize_project, validate_project_data

# --- validate_project_data ---


def test_valid_full_payload() -> None:
    data = {
        "name": "My Project",
        "description": "Desc",
        "technologies_used": ["Python", "Django"],
        "date_start": "2024-01-01",
        "date_end": "2024-06-01",
    }
    cleaned, errors = validate_project_data(data)
    assert not errors
    assert cleaned["name"] == "My Project"


def test_missing_name() -> None:
    _, errors = validate_project_data({"date_start": "2024-01-01"})
    assert any("name" in e for e in errors)


def test_blank_name() -> None:
    _, errors = validate_project_data({"name": "   ", "date_start": "2024-01-01"})
    assert any("name" in e for e in errors)


def test_name_over_max_length() -> None:
    _, errors = validate_project_data({"name": "x" * 201, "date_start": "2024-01-01"})
    assert any("200" in e for e in errors)


def test_missing_date_start() -> None:
    _, errors = validate_project_data({"name": "X"})
    assert any("date_start" in e for e in errors)


def test_invalid_date_start_format() -> None:
    _, errors = validate_project_data({"name": "X", "date_start": "not-a-date"})
    assert any("date_start" in e for e in errors)


def test_date_end_before_date_start() -> None:
    _, errors = validate_project_data(
        {"name": "X", "date_start": "2024-06-01", "date_end": "2024-01-01"}
    )
    assert any("date_end" in e for e in errors)


def test_date_end_equal_to_date_start_is_valid() -> None:
    _, errors = validate_project_data(
        {"name": "X", "date_start": "2024-06-01", "date_end": "2024-06-01"}
    )
    assert not errors


def test_null_date_end_is_accepted() -> None:
    cleaned, errors = validate_project_data(
        {"name": "X", "date_start": "2024-01-01", "date_end": None}
    )
    assert not errors
    assert cleaned["date_end"] is None


def test_technologies_must_be_a_list() -> None:
    _, errors = validate_project_data(
        {"name": "X", "date_start": "2024-01-01", "technologies_used": "Python"}
    )
    assert any("technologies_used" in e for e in errors)


def test_technologies_must_be_strings() -> None:
    _, errors = validate_project_data(
        {"name": "X", "date_start": "2024-01-01", "technologies_used": [1, 2]}
    )
    assert any("technologies_used" in e for e in errors)


def test_partial_skips_missing_required_fields() -> None:
    cleaned, errors = validate_project_data({"name": "Updated"}, partial=True)
    assert not errors
    assert cleaned == {"name": "Updated"}


def test_partial_still_validates_fields_that_are_present() -> None:
    _, errors = validate_project_data(
        {"date_start": "2024-06-01", "date_end": "2024-01-01"}, partial=True
    )
    assert any("date_end" in e for e in errors)


# --- serialize_project ---


@pytest.mark.django_db
def test_serialize_project_fields() -> None:
    user = User.objects.create_user(username="owner", password="pass")
    project = Project.objects.create(
        user=user,
        name="Test",
        description="Desc",
        technologies_used=["Python"],
        date_start=date(2024, 1, 1),
    )
    data = serialize_project(project)
    assert data["id"] == project.pk
    assert data["name"] == "Test"
    assert data["description"] == "Desc"
    assert data["technologies_used"] == ["Python"]
    assert data["date_start"] == "2024-01-01"
    assert data["date_end"] is None
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.django_db
def test_serialize_project_with_date_end() -> None:
    user = User.objects.create_user(username="owner2", password="pass")
    project = Project.objects.create(
        user=user,
        name="Finished",
        technologies_used=[],
        date_start=date(2024, 1, 1),
        date_end=date(2024, 12, 31),
    )
    data = serialize_project(project)
    assert data["date_end"] == "2024-12-31"
