# API Test Plan

## Objective

Assess release readiness of the integrations/assets REST API against the exposed
Swagger 2.0 contract and the assignment requirements for Basic Authentication,
tenant segregation, and at least 1,000 requests per minute.

## Observed API

- Integrations: collection `GET`, `POST`; item `GET`, runtime `PUT`, `DELETE`.
- Assets: collection `GET`, `POST`, `PATCH`; item `GET`, `DELETE`.
- Both resources contain a server-generated UUID and `tenant_id`.
- Assets reference an integration through `integration_id`.
- Swagger is served at `/swagger/doc.json` and is the contract source.

## Scope and coverage

### P0 — Authentication

- Valid credentials for both supplied users.
- Missing credentials, wrong password, unknown/empty user, empty password.
- Malformed Basic credentials, incomplete Base64 payload, and wrong scheme.
- Status, challenge header, empty response, and absence of data exposure.

### P0 — Tenant segregation

- Integration collection visibility for both tenants.
- Cross-tenant integration GET, PUT, and DELETE.
- Cross-tenant asset GET, PATCH, and DELETE.
- Creating an asset against another tenant's integration.
- Owner-state retrieval after every rejected mutation expectation.

### Core functionality

- Independent integration create/get, update/persistence, pagination, delete.
- Independent asset create/get, filtered listing, patch/persistence, delete.
- Parent deletion with a child asset. Cascade and orphan policies are not defined,
  so the test accepts either coherent result and rejects server errors/corruption.

### P1 — Contract

Checks use the live Swagger document rather than duplicated schemas:

- Documented versus runtime integration PUT path.
- Asset path-ID type versus runtime UUID.
- Documented `200` versus runtime `201` for creates.
- Empty collection array schema.
- `HTTPError` response schema.
- Missing Basic-auth security declaration and relevant `401` responses.
- Undocumented duplicate-integration `409`.

### P1 — Validation and errors

- JSON property type errors and malformed JSON.
- Required `integrationId` list parameter.
- Unknown resource IDs.
- Invalid pagination error handling and contract shape.
- Duplicate integration handling through contract coverage.

The models declare no required properties, enums, formats, string lengths, or
numeric pagination bounds. Tests therefore do not invent such validation rules.

### Load

Authenticated, non-destructive integration-list traffic. The pass criterion is
at least 1,000 completed requests per minute with zero HTTP/request failures.
Latency is reported but is not a pass/fail SLA.

## Isolation and cleanup

- Each test creates unique resources through function-scoped factories.
- Factories attempt cleanup even when assertions fail and tolerate resources
  already removed by the scenario.
- Tests do not depend on execution order or pre-existing domain records.
- Load traffic is read-only.

## Defect policy

Contract, authentication, and tenant requirements remain authoritative. Confirmed
product defects use strict `xfail` markers referencing `BUGS.md`; expectations are
not weakened to reproduce broken behavior. Undocumented behavior is not failed
unless it contradicts the assignment, contract, or a necessary ownership/data
integrity invariant.

## Out of scope

- UI testing of Swagger beyond service readiness.
- Full penetration, infrastructure, database, and transport-security testing.
- Arbitrary string boundaries or integration-type enums absent from Swagger.
- A mandated cascade policy when deleting an integration; none is specified.
- Latency SLA enforcement; the assignment specifies throughput only.

## Exit criteria

- P0, core functional, contract, and targeted P1 suites execute independently.
- Every unexpected failure is classified as a test/framework or product defect.
- Confirmed defects are reproducible and referenced from strict xfails.
- One command starts the service, waits for health, runs tests, preserves HTML and
  JUnit reports, and stops the environment.
- Load execution demonstrates whether 1,000 requests/minute is sustained.

