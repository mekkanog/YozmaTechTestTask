import base64

import pytest

from tests.api_client import ApiClient


pytestmark = pytest.mark.security


@pytest.mark.parametrize("client_fixture", ["user1_client", "user2_client"])
def test_supplied_users_authenticate(request, client_fixture):
    response = request.getfixturevalue(client_fixture).get("integrations")
    assert response.status_code == 200


@pytest.mark.parametrize("path", ["integrations", "assets?integrationId=unknown"])
def test_missing_credentials_are_rejected(anonymous_client, path):
    response = anonymous_client.get(path)
    assert response.status_code == 401
    assert response.text == ""
    assert response.headers["WWW-Authenticate"].startswith("Basic")


@pytest.mark.parametrize("case", ["wrong_password", "unknown_user", "empty", "empty_password"])
def test_invalid_credentials_are_rejected(settings, case):
    credentials = {
        "wrong_password": (settings.user_1, "wrong-password"),
        "unknown_user": ("unknown-user", settings.password_1),
        "empty": ("", ""),
        "empty_password": (settings.user_1, ""),
    }
    username, password = credentials[case]
    client = ApiClient(settings.base_url, (username, password), settings.timeout)
    response = client.get("integrations")
    assert response.status_code == 401
    assert response.text == ""


@pytest.mark.parametrize("authorization", ["Basic !!!not-base64!!!", "Bearer token"])
def test_malformed_authorization_is_rejected(anonymous_client, authorization):
    response = anonymous_client.get(
        "integrations", headers={"Authorization": authorization}
    )
    assert response.status_code == 401
    assert response.text == ""


def test_basic_credentials_without_password_are_rejected(anonymous_client, settings):
    incomplete = base64.b64encode(settings.user_1.encode()).decode()
    response = anonymous_client.get(
        "integrations", headers={"Authorization": f"Basic {incomplete}"}
    )
    assert response.status_code == 401
    assert response.text == ""
