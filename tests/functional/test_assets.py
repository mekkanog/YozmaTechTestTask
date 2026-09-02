import pytest


pytestmark = pytest.mark.functional


def test_create_and_get_asset(user1_client, integration_factory, asset_factory, settings):
    integration = integration_factory(user1_client)
    created = asset_factory(user1_client, integration["id"], description="original")
    response = user1_client.get(f"assets/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created
    assert created["tenant_id"] == settings.user_1
    assert created["integration_id"] == integration["id"]


def test_patch_asset_persists(user1_client, integration_factory, asset_factory):
    integration = integration_factory(user1_client)
    created = asset_factory(user1_client, integration["id"])
    response = user1_client.patch(
        "assets",
        json={"id": created["id"], "name": "updated-asset", "description": "updated"},
    )
    persisted = user1_client.get(f"assets/{created['id']}")

    assert response.status_code == 200
    assert persisted.status_code == 200
    assert persisted.json()["name"] == "updated-asset"
    assert persisted.json()["description"] == "updated"


def test_list_assets_by_integration(user1_client, integration_factory, asset_factory):
    integration = integration_factory(user1_client)
    created = asset_factory(user1_client, integration["id"])
    response = user1_client.get("assets", params={"integrationId": integration["id"]})

    assert response.status_code == 200
    assert created["id"] in {item["id"] for item in response.json()}
    assert all(item["integration_id"] == integration["id"] for item in response.json())


def test_delete_asset(user1_client, integration_factory, asset_factory):
    integration = integration_factory(user1_client)
    created = asset_factory(user1_client, integration["id"])
    response = user1_client.delete(f"assets/{created['id']}")
    after_delete = user1_client.get(f"assets/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert after_delete.status_code == 404
