from uuid import uuid4
import warnings

import pytest
import requests

from tests.api_client import ApiClient
from tests.config import Settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="session")
def anonymous_client(settings: Settings) -> ApiClient:
    return ApiClient(settings.base_url, None, settings.timeout)


@pytest.fixture(scope="session")
def user1_client(settings: Settings) -> ApiClient:
    return ApiClient(
        settings.base_url, (settings.user_1, settings.password_1), settings.timeout
    )


@pytest.fixture(scope="session")
def user2_client(settings: Settings) -> ApiClient:
    return ApiClient(
        settings.base_url, (settings.user_2, settings.password_2), settings.timeout
    )


@pytest.fixture(scope="session")
def swagger(settings: Settings) -> dict:
    response = requests.get(
        f"{settings.base_url}/swagger/doc.json", timeout=settings.timeout
    )
    response.raise_for_status()
    return response.json()


def unique_name(prefix: str) -> str:
    return f"qa-{prefix}-{uuid4().hex[:10]}"


def cleanup_resource(
    client: ApiClient, path: str, expected_statuses: set[int]
) -> None:
    try:
        response = client.delete(path)
        if response.status_code not in expected_statuses:
            warnings.warn(
                f"Cleanup DELETE {path} returned {response.status_code}: {response.text}",
                stacklevel=2,
            )
    except requests.RequestException as exc:
        warnings.warn(f"Cleanup DELETE {path} failed: {exc}", stacklevel=2)


@pytest.fixture
def integration_factory():
    created: list[tuple[ApiClient, str]] = []

    def create(client: ApiClient, *, name: str | None = None, type_: str = "github") -> dict:
        response = client.post(
            "integrations",
            json={"name": name or unique_name("integration"), "type": type_},
        )
        assert response.status_code in {200, 201}, response.text
        resource = response.json()
        created.append((client, resource["id"]))
        return resource

    yield create

    for client, resource_id in reversed(created):
        cleanup_resource(client, f"integrations/{resource_id}", {200, 404})


@pytest.fixture
def asset_factory():
    created: list[tuple[ApiClient, str]] = []

    def create(
        client: ApiClient,
        integration_id: str,
        *,
        name: str | None = None,
        description: str = "automation asset",
    ) -> dict:
        response = client.post(
            "assets",
            json={
                "name": name or unique_name("asset"),
                "description": description,
                "integration_id": integration_id,
            },
        )
        assert response.status_code in {200, 201}, response.text
        resource = response.json()
        created.append((client, resource["id"]))
        return resource

    yield create

    for client, resource_id in reversed(created):
        cleanup_resource(client, f"assets/{resource_id}", {204, 404})
