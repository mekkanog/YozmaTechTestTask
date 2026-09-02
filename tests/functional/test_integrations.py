import pytest


pytestmark = pytest.mark.functional


def test_create_and_get_integration(user1_client, integration_factory, settings):
    created = integration_factory(user1_client, type_="github")
    response = user1_client.get(f"integrations/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created
    assert created["tenant_id"] == settings.user_1


@pytest.mark.xfail(reason="BUG-009: integration PUT is a successful no-op", strict=True)
def test_update_integration_persists(user1_client, integration_factory):
    created = integration_factory(user1_client)
    response = user1_client.put(
        f"integrations/{created['id']}",
        json={"id": created["id"], "name": "persisted-update"},
    )
    persisted = user1_client.get(f"integrations/{created['id']}")

    assert response.status_code == 200
    assert persisted.status_code == 200
    assert response.json()["name"] == "persisted-update"
    assert persisted.json()["name"] == "persisted-update"


def test_delete_integration(user1_client, integration_factory):
    created = integration_factory(user1_client)
    response = user1_client.delete(f"integrations/{created['id']}")
    after_delete = user1_client.get(f"integrations/{created['id']}")

    assert response.status_code == 200
    assert response.json() == {"message": "integration deleted"}
    assert after_delete.status_code == 404


def test_integration_pagination(user1_client, integration_factory):
    created = [integration_factory(user1_client) for _ in range(4)]
    page_one = user1_client.get("integrations", params={"page": 1, "limit": 2})
    page_two = user1_client.get("integrations", params={"page": 2, "limit": 2})
    full_list = user1_client.get("integrations")

    assert page_one.status_code == page_two.status_code == 200
    assert len(page_one.json()) == len(page_two.json()) == 2
    page_one_ids = {item["id"] for item in page_one.json()}
    page_two_ids = {item["id"] for item in page_two.json()}
    assert page_one_ids.isdisjoint(page_two_ids)
    assert {item["id"] for item in created}.issubset(
        {item["id"] for item in full_list.json()}
    )


def test_delete_integration_with_asset_has_consistent_result(
    user1_client, integration_factory, asset_factory
):
    integration = integration_factory(user1_client)
    asset = asset_factory(user1_client, integration["id"])
    deleted = user1_client.delete(f"integrations/{integration['id']}")
    parent = user1_client.get(f"integrations/{integration['id']}")
    child = user1_client.get(f"assets/{asset['id']}")

    assert deleted.status_code == 200
    assert parent.status_code == 404
    # Cascade versus retained child is not specified. Both are accepted here,
    # while a server error or corrupt representation is not.
    assert child.status_code in {200, 404}
    if child.status_code == 200:
        assert child.json()["integration_id"] == integration["id"]
