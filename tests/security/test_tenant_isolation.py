from uuid import uuid4

import pytest


pytestmark = pytest.mark.security


@pytest.mark.tenant
@pytest.mark.xfail(reason="BUG-001: integration collection leaks all tenants", strict=True)
def test_integration_collections_are_tenant_scoped(
    user1_client, user2_client, integration_factory
):
    user1 = integration_factory(user1_client)
    user2 = integration_factory(user2_client)

    user1_items = user1_client.get("integrations").json()
    user2_items = user2_client.get("integrations").json()
    user1_ids = {item["id"] for item in user1_items}
    user2_ids = {item["id"] for item in user2_items}

    assert user1["id"] in user1_ids and user2["id"] not in user1_ids
    assert user2["id"] in user2_ids and user1["id"] not in user2_ids


@pytest.mark.tenant
@pytest.mark.xfail(reason="BUG-002: cross-tenant integration GET is allowed", strict=True)
def test_other_tenant_cannot_get_integration(
    user1_client, user2_client, integration_factory
):
    owned = integration_factory(user1_client)
    response = user2_client.get(f"integrations/{owned['id']}")
    assert response.status_code in {403, 404}


@pytest.mark.tenant
@pytest.mark.xfail(reason="BUG-003: cross-tenant integration update is accepted", strict=True)
def test_other_tenant_cannot_update_integration(
    user1_client, user2_client, integration_factory
):
    owned = integration_factory(user1_client)
    response = user2_client.put(
        f"integrations/{owned['id']}",
        json={"id": owned["id"], "name": "cross-tenant-change"},
    )
    owner_state = user1_client.get(f"integrations/{owned['id']}")

    unchanged = owner_state.status_code == 200 and owner_state.json()["name"] == owned["name"]
    assert response.status_code in {403, 404} and unchanged


@pytest.mark.tenant
@pytest.mark.xfail(reason="BUG-004: cross-tenant integration DELETE succeeds", strict=True)
def test_other_tenant_cannot_delete_integration(
    user1_client, user2_client, integration_factory
):
    owned = integration_factory(user1_client)
    response = user2_client.delete(f"integrations/{owned['id']}")
    owner_state = user1_client.get(f"integrations/{owned['id']}")

    assert response.status_code in {403, 404} and owner_state.status_code == 200


@pytest.mark.tenant
@pytest.mark.xfail(reason="BUG-005: cross-tenant asset GET is allowed", strict=True)
def test_other_tenant_cannot_get_asset(
    user1_client, user2_client, integration_factory, asset_factory
):
    integration = integration_factory(user1_client)
    asset = asset_factory(user1_client, integration["id"])
    response = user2_client.get(f"assets/{asset['id']}")
    assert response.status_code in {403, 404}


@pytest.mark.tenant
@pytest.mark.xfail(reason="BUG-006: cross-tenant asset PATCH succeeds", strict=True)
def test_other_tenant_cannot_patch_asset(
    user1_client, user2_client, integration_factory, asset_factory
):
    integration = integration_factory(user1_client)
    asset = asset_factory(user1_client, integration["id"])
    response = user2_client.patch(
        "assets",
        json={"id": asset["id"], "name": "cross-tenant-change", "description": "changed"},
    )
    owner_state = user1_client.get(f"assets/{asset['id']}")

    unchanged = owner_state.status_code == 200 and owner_state.json()["name"] == asset["name"]
    assert response.status_code in {403, 404} and unchanged


@pytest.mark.tenant
@pytest.mark.xfail(reason="BUG-007: cross-tenant asset DELETE succeeds", strict=True)
def test_other_tenant_cannot_delete_asset(
    user1_client, user2_client, integration_factory, asset_factory
):
    integration = integration_factory(user1_client)
    asset = asset_factory(user1_client, integration["id"])
    response = user2_client.delete(f"assets/{asset['id']}")
    owner_state = user1_client.get(f"assets/{asset['id']}")

    assert response.status_code in {403, 404} and owner_state.status_code == 200


@pytest.mark.tenant
@pytest.mark.xfail(
    reason="BUG-008: asset may reference another tenant's integration", strict=True
)
def test_asset_cannot_reference_other_tenant_integration(
    user1_client, user2_client, integration_factory, asset_factory
):
    integration = integration_factory(user1_client)
    response = user2_client.post(
        "assets",
        json={
            "name": f"cross-tenant-reference-{uuid4().hex[:10]}",
            "description": "must be rejected",
            "integration_id": integration["id"],
        },
    )
    if response.status_code in {200, 201}:
        asset_factory_created = response.json()
        user2_client.delete(f"assets/{asset_factory_created['id']}")

    assert response.status_code in {403, 404}
