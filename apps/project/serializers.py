from __future__ import annotations

from datetime import date
from typing import Any

from apps.project.models import Project


def serialize_project(project: Project) -> dict[str, Any]:
    return {
        "id": project.pk,
        "name": project.name,
        "description": project.description,
        "technologies_used": project.technologies_used,
        "date_start": project.date_start.isoformat(),
        "date_end": project.date_end.isoformat() if project.date_end else None,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
    }


def validate_project_data(
    data: dict[str, Any], *, partial: bool = False
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    cleaned: dict[str, Any] = {}

    if not partial or "name" in data:
        name = data.get("name")
        if name is None:
            errors.append("name is required")
        elif not isinstance(name, str) or not name.strip():
            errors.append("name must be a non-empty string")
        elif len(name) > 200:
            errors.append("name must be at most 200 characters")
        else:
            cleaned["name"] = name.strip()

    if "description" in data:
        description = data["description"]
        if not isinstance(description, str):
            errors.append("description must be a string")
        else:
            cleaned["description"] = description

    if "technologies_used" in data:
        technologies = data["technologies_used"]
        if not isinstance(technologies, list):
            errors.append("technologies_used must be a list")
        elif not all(isinstance(t, str) for t in technologies):
            errors.append("technologies_used must be a list of strings")
        else:
            cleaned["technologies_used"] = technologies

    if not partial or "date_start" in data:
        date_start_raw = data.get("date_start")
        if date_start_raw is None:
            errors.append("date_start is required")
        else:
            try:
                cleaned["date_start"] = date.fromisoformat(str(date_start_raw))
            except ValueError:
                errors.append("date_start must be a valid date (YYYY-MM-DD)")

    if "date_end" in data:
        date_end_raw = data["date_end"]
        if date_end_raw is None:
            cleaned["date_end"] = None
        else:
            try:
                cleaned["date_end"] = date.fromisoformat(str(date_end_raw))
            except ValueError:
                errors.append("date_end must be a valid date (YYYY-MM-DD) or null")

    if (
        not errors
        and "date_start" in cleaned
        and "date_end" in cleaned
        and cleaned["date_end"] is not None
        and cleaned["date_end"] < cleaned["date_start"]
    ):
        errors.append("date_end must be on or after date_start")

    return cleaned, errors
