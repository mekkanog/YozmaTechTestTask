# Confirmed Defects

All defects were reproduced against `infralightio/test-integration-api:latest`.

## BUG-001 — Integration collection leaks all tenants

**Severity:** Critical

Create one integration as each user, then list integrations as either user.
Expected only the caller's tenant; actual `200` contains both tenant IDs.

Automated test: `tests/security/test_tenant_isolation.py::test_integration_collections_are_tenant_scoped`

## BUG-002 — Cross-tenant integration retrieval is allowed

**Severity:** Critical

Create an integration as user 1 and GET its ID as user 2. Expected `403` or
non-disclosing `404`; actual `200` returns user 1's complete integration.

Automated test: `tests/security/test_tenant_isolation.py::test_other_tenant_cannot_get_integration`

## BUG-003 — Cross-tenant integration update is accepted

**Severity:** High

User 2 PUTs user 1's integration. Expected `403/404`; actual `200`. The current
update is also a no-op (BUG-009), but accepting the unauthorized request is itself
an authorization defect. Owner state is checked after the request.

Automated test: `tests/security/test_tenant_isolation.py::test_other_tenant_cannot_update_integration`

## BUG-004 — Cross-tenant integration deletion succeeds

**Severity:** Critical

User 2 DELETEs user 1's integration. Actual response is `200`, and the owner then
receives `404` for the resource.

Automated test: `tests/security/test_tenant_isolation.py::test_other_tenant_cannot_delete_integration`

## BUG-005 — Cross-tenant asset retrieval is allowed

**Severity:** Critical

User 2 GETs an asset created by user 1. Actual `200` exposes the full asset.

Automated test: `tests/security/test_tenant_isolation.py::test_other_tenant_cannot_get_asset`

## BUG-006 — Cross-tenant asset update succeeds

**Severity:** Critical

User 2 PATCHes user 1's asset. Actual `200`; an owner GET confirms the foreign
name and description persisted.

Automated test: `tests/security/test_tenant_isolation.py::test_other_tenant_cannot_patch_asset`

## BUG-007 — Cross-tenant asset deletion succeeds

**Severity:** Critical

User 2 DELETEs user 1's asset. Actual `204`, followed by owner `404`.

Automated test: `tests/security/test_tenant_isolation.py::test_other_tenant_cannot_delete_asset`

## BUG-008 — Asset may reference another tenant's integration

**Severity:** High

User 2 creates an asset using user 1's integration ID. Actual `201` creates a
user-2 asset attached to the foreign integration instead of rejecting it.

Automated test: `tests/security/test_tenant_isolation.py::test_asset_cannot_reference_other_tenant_integration`

## BUG-009 — Integration update returns success without persisting state

**Severity:** High

The owner sends a valid PUT with a changed name. Actual response is `200`, but
both response and subsequent GET retain the original name.

Automated test: `tests/functional/test_integrations.py::test_update_integration_persists`

## BUG-010 — Invalid pagination produces a non-contract error

**Severity:** Medium

Non-integer/negative pagination returns `500` and an error representation that
does not match `HTTPError` (and may have an empty body) instead of a client error.

Automated test: `tests/validation/test_requests.py::test_invalid_pagination_returns_contract_error`

## BUG-011 — Documented integration PUT route does not exist

**Severity:** Medium

Swagger defines `PUT /api/v1/integrations`; it returns plain-text `404`. Runtime
instead implements undocumented `PUT /api/v1/integrations/{id}`.

Automated test: `tests/contract/test_openapi_contract.py::test_documented_integration_update_route_exists`

## BUG-012 — Asset ID path type contradicts runtime UUIDs

**Severity:** Medium

Swagger declares asset `{id}` as integer. Created asset IDs and working item
requests use UUID strings.

Automated test: `tests/contract/test_openapi_contract.py::test_asset_path_id_schema_matches_runtime`

## BUG-013 — Create success status is undocumented

**Severity:** Medium

Integration and asset POST operations document `200`, but runtime returns `201`.

Automated test: `tests/contract/test_openapi_contract.py::test_create_status_is_documented`

## BUG-014 — Empty collection violates array schema

**Severity:** Medium

An empty filtered asset collection returns `200` with JSON `null`; Swagger
requires an array. Empty integration collections exhibit the same behavior.

Automated test: `tests/contract/test_openapi_contract.py::test_empty_integration_collection_matches_array_schema`

## BUG-015 — Runtime errors violate HTTPError schema

**Severity:** Medium

Swagger requires `{code: integer, message: string}`. Runtime errors use
`{"error":"..."}` and omit both documented properties.

Automated test: `tests/contract/test_openapi_contract.py::test_error_body_matches_documented_schema`

## BUG-016 — Swagger omits enforced Basic Authentication

**Severity:** Medium

The service enforces Basic Authentication, but Swagger has no security definition
or security requirement and omits `401` from relevant integration operations.

Automated test: `tests/contract/test_openapi_contract.py::test_basic_authentication_is_documented`

## BUG-017 — Duplicate integration conflict is undocumented

**Severity:** Low

Creating a duplicate integration returns `409`, but integration POST does not
document that response.

Automated test: `tests/contract/test_openapi_contract.py::test_duplicate_integration_status_is_documented`
