import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_index_returns_200(client: Client) -> None:
    response = client.get(reverse("core:index"))
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db
def test_health_endpoint(client: Client) -> None:
    response = client.get(reverse("core:health"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
