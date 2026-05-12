from unittest.mock import MagicMock, patch

from django.http import JsonResponse
from django.test import RequestFactory

from apps.users.decorators import require_auth

factory = RequestFactory()


def _dummy_view(request: object) -> JsonResponse:
    return JsonResponse({"ok": True})


def test_missing_authorization_header_returns_401() -> None:
    request = factory.get("/")
    response = require_auth(_dummy_view)(request)
    assert response.status_code == 401


def test_non_bearer_scheme_returns_401() -> None:
    request = factory.get("/", HTTP_AUTHORIZATION="Basic dXNlcjpwYXNz")
    response = require_auth(_dummy_view)(request)
    assert response.status_code == 401


def test_bearer_prefix_only_no_token_returns_401() -> None:
    request = factory.get("/", HTTP_AUTHORIZATION="Bearer ")
    with patch("apps.users.repository.token.get_token_with_user", return_value=None):
        response = require_auth(_dummy_view)(request)
    assert response.status_code == 401


def test_unknown_token_returns_401() -> None:
    request = factory.get("/", HTTP_AUTHORIZATION="Bearer unknown-token")
    with patch("apps.users.repository.token.get_token_with_user", return_value=None):
        response = require_auth(_dummy_view)(request)
    assert response.status_code == 401


def test_valid_token_calls_view() -> None:
    mock_user = MagicMock()
    mock_auth_token = MagicMock()
    mock_auth_token.user = mock_user

    request = factory.get("/", HTTP_AUTHORIZATION="Bearer valid-token")
    with patch("apps.users.repository.token.get_token_with_user", return_value=mock_auth_token):
        response = require_auth(_dummy_view)(request)

    assert response.status_code == 200


def test_valid_token_sets_request_user() -> None:
    mock_user = MagicMock()
    mock_auth_token = MagicMock()
    mock_auth_token.user = mock_user

    request = factory.get("/", HTTP_AUTHORIZATION="Bearer valid-token")
    with patch("apps.users.repository.token.get_token_with_user", return_value=mock_auth_token):
        require_auth(_dummy_view)(request)

    assert request.user is mock_user


def test_decorated_view_preserves_name() -> None:
    decorated = require_auth(_dummy_view)
    assert decorated.__name__ == "_dummy_view"
