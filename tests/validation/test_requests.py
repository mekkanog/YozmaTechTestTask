from uuid import uuid4

import pytest


pytestmark = pytest.mark.validation


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("integrations", {"name": "wrong-type", "type": 42}),
        (
            "assets",
            {"name": "wrong-type", "description": "valid", "integration_id": 42},
        ),
    ],
)
def test_wrong_json_property_types_are_rejected(user1_client, path, payload):
    response = user1_client.post(path, json=payload)
    assert response.status_code == 400
    assert response.headers["Content-Type"].startswith("application/json")


@pytest.mark.parametrize("path", ["integrations", "assets"])
def test_malformed_json_is_rejected(user1_client, path):
    response = user1_client.post(
        path, data="{broken", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert response.headers["Content-Type"].startswith("application/json")


def test_assets_require_integration_id_query(user1_client):
    response = user1_client.get("assets")
    assert response.status_code == 400
    assert response.json()["error"] == "integrationId is required"


def test_valid_nonexistent_resource_ids_return_not_found(user1_client):
    nonexistent_id = str(uuid4())
    integration = user1_client.get(f"integrations/{nonexistent_id}")
    asset = user1_client.get(f"assets/{nonexistent_id}")
    assert integration.status_code == asset.status_code == 404


def test_malformed_resource_ids_return_not_found(user1_client):
    integration = user1_client.get("integrations/not-a-uuid")
    asset = user1_client.get("assets/not-a-uuid")
    assert integration.status_code == asset.status_code == 404


@pytest.mark.xfail(reason="BUG-010: invalid pagination produces non-contract error", strict=True)
def test_invalid_pagination_returns_contract_error(user1_client, swagger):
    from jsonschema import validate

    response = user1_client.get("integrations", params={"page": "text", "limit": -1})
    schema = swagger["definitions"]["httputil.HTTPError"]
    body = response.json()
    validate(body, schema)
    assert set(body) == set(schema["properties"])
    assert response.status_code == 400
