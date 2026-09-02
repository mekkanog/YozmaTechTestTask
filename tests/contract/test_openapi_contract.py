from uuid import UUID, uuid4

import pytest
from jsonschema import validate


pytestmark = pytest.mark.contract


def find_parameter(operation: dict, *, name: str, location: str) -> dict:
    return next(
        parameter
        for parameter in operation.get("parameters", [])
        if parameter.get("name") == name and parameter.get("in") == location
    )


def resolve_schema(swagger: dict, schema: dict) -> dict:
    """Resolve the local references used by this API's response schemas."""
    if "$ref" in schema:
        definition_name = schema["$ref"].removeprefix("#/definitions/")
        return swagger["definitions"][definition_name]
    if schema.get("type") == "array" and "$ref" in schema.get("items", {}):
        return {**schema, "items": resolve_schema(swagger, schema["items"])}
    return schema


def response_schema(swagger: dict, path: str, method: str, status: int) -> dict:
    schema = swagger["paths"][path][method]["responses"][str(status)]["schema"]
    return resolve_schema(swagger, schema)


@pytest.mark.xfail(
    reason="BUG-011: documented integration PUT path does not exist at runtime",
    strict=True,
)
def test_documented_integration_update_route_exists(user1_client, swagger):
    documented = user1_client.put(
        "integrations", json={"id": "unused", "name": "unused"}
    )
    assert "put" in swagger["paths"]["/integrations"]
    assert documented.status_code != 404
    assert "put" in swagger["paths"]["/integrations/{id}"]


@pytest.mark.xfail(
    reason="BUG-012: asset ID is documented as integer but runtime uses UUID strings",
    strict=True,
)
def test_asset_path_id_schema_matches_runtime(
    user1_client, integration_factory, asset_factory, swagger
):
    integration = integration_factory(user1_client)
    asset = asset_factory(user1_client, integration["id"])
    UUID(asset["id"])
    operation = swagger["paths"]["/assets/{id}"]["get"]
    parameter = find_parameter(operation, name="id", location="path")
    assert parameter["type"] == "string"
    assert parameter.get("format") == "uuid"


@pytest.mark.parametrize(
    ("path", "payload", "operation"),
    [
        ("integrations", {"name": "contract-create-integration", "type": "github"}, "integration"),
        ("assets", None, "asset"),
    ],
)
@pytest.mark.xfail(
    reason="BUG-013: create returns undocumented 201 instead of documented 200",
    strict=True,
)
def test_create_status_is_documented(
    user1_client, integration_factory, swagger, path, payload, operation
):
    payload = payload.copy() if payload else None
    if payload:
        payload["name"] = f"{payload['name']}-{uuid4().hex[:10]}"
    if operation == "asset":
        integration = integration_factory(user1_client)
        payload = {
            "name": f"contract-create-asset-{uuid4().hex[:10]}",
            "description": "contract",
            "integration_id": integration["id"],
        }

    response = user1_client.post(path, json=payload)
    resource = response.json()
    try:
        assert str(response.status_code) in swagger["paths"][f"/{path}"]["post"]["responses"]
    finally:
        if response.status_code in {200, 201}:
            user1_client.delete(f"{path}/{resource['id']}")


@pytest.mark.xfail(
    reason="BUG-014: empty collection is JSON null instead of an array", strict=True
)
def test_empty_integration_collection_matches_array_schema(user1_client, swagger):
    response = user1_client.get("integrations")
    if response.json():
        pytest.skip("requires an otherwise clean service to exercise empty serialization")
    schema = swagger["paths"]["/integrations"]["get"]["responses"]["200"]["schema"]
    validate(response.json(), schema)


@pytest.mark.xfail(
    reason="BUG-015: runtime error body does not match HTTPError schema", strict=True
)
def test_error_body_matches_documented_schema(user1_client, swagger):
    response = user1_client.get(f"integrations/{uuid4()}")
    schema = swagger["definitions"]["httputil.HTTPError"]
    assert response.status_code == 404
    body = response.json()
    validate(body, schema)
    assert set(body) == set(schema["properties"])


@pytest.mark.xfail(
    reason="BUG-016: Swagger omits enforced Basic authentication and some 401 responses",
    strict=True,
)
def test_basic_authentication_is_documented(swagger):
    definitions = swagger.get("securityDefinitions", {})
    basic_schemes = [value for value in definitions.values() if value.get("type") == "basic"]
    assert basic_schemes
    assert swagger.get("security")
    assert "401" in swagger["paths"]["/integrations"]["get"]["responses"]
    assert "401" in swagger["paths"]["/integrations"]["post"]["responses"]


@pytest.mark.xfail(
    reason="BUG-017: integration duplicate 409 response is undocumented", strict=True
)
def test_duplicate_integration_status_is_documented(
    user1_client, integration_factory, swagger
):
    created = integration_factory(
        user1_client, name=f"contract-duplicate-{uuid4().hex[:10]}"
    )
    response = user1_client.post(
        "integrations", json={"name": created["name"], "type": created["type"]}
    )
    assert response.status_code == 409
    assert "409" in swagger["paths"]["/integrations"]["post"]["responses"]


def test_integration_success_responses_match_live_schemas(
    user1_client, integration_factory, swagger
):
    created = integration_factory(user1_client)
    item_response = user1_client.get(f"integrations/{created['id']}")
    collection_response = user1_client.get("integrations")

    assert item_response.status_code == collection_response.status_code == 200
    validate(
        item_response.json(),
        response_schema(swagger, "/integrations/{id}", "get", 200),
    )
    validate(
        collection_response.json(),
        response_schema(swagger, "/integrations", "get", 200),
    )


def test_asset_success_responses_match_live_schemas(
    user1_client, integration_factory, asset_factory, swagger
):
    integration = integration_factory(user1_client)
    created = asset_factory(user1_client, integration["id"])
    item_response = user1_client.get(f"assets/{created['id']}")
    collection_response = user1_client.get(
        "assets", params={"integrationId": integration["id"]}
    )

    assert item_response.status_code == collection_response.status_code == 200
    validate(
        item_response.json(), response_schema(swagger, "/assets/{id}", "get", 200)
    )
    validate(
        collection_response.json(), response_schema(swagger, "/assets", "get", 200)
    )
