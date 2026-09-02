# Automation Engineer Home Assignment

Pytest coverage for the multi-tenant integrations/assets API supplied as
`infralightio/test-integration-api:latest`.

## Prerequisites

- Docker with Docker Compose
- Make

## Quick start

```bash
make test
```

This builds the test image, starts a fresh API, waits on `/swagger/doc.json`, runs
all non-load tests, writes reports, and stops the environment even on failure.

Reports:

- `reports/report.html` — self-contained human-readable report
- `reports/junit.xml` — CI-compatible JUnit report

Confirmed product defects appear as strict expected failures and are documented
in [BUGS.md](BUGS.md). Strict `xfail` means the run fails if a known-bug test
unexpectedly passes, forcing investigation of either the test or changed product
behavior. The 18 expected failing cases represent 17 documented defects because
BUG-013 is independently checked for integration and asset creation. Coverage
rationale is in [TEST_PLAN.md](TEST_PLAN.md).

## Commands

```bash
make test             # functional, security, validation, and contract tests
make test-functional  # core CRUD behavior
make test-security    # authentication and tenant isolation
make test-contract    # live Swagger contract checks
make test-load        # >= 1,000 requests/minute check
make up               # start API only
make down             # stop and remove the environment
```

## Design

- `tests/api_client.py`: small HTTP client handling base URL, Basic Auth, timeout,
  and common methods.
- `tests/conftest.py`: centralized clients plus independent resource factories
  that clean up with `yield` fixtures.
- `tests/functional`, `security`, `validation`, `contract`, and `load`: focused
  suites selected by pytest markers.
- Contract tests consume the live `/swagger/doc.json`; schemas are not duplicated.

Runtime values are configurable through `API_BASE_URL`, `API_USER_1`,
`API_PASSWORD_1`, `API_USER_2`, `API_PASSWORD_2`, and `API_TIMEOUT_SECONDS`.
Defaults match the assignment's local credentials.

Load execution additionally supports `LOAD_REQUESTS` (default `1000`) and
`LOAD_WORKERS` (default `20`). Results are written to
`reports/load-report.html` and `reports/load-junit.xml`.

The load check sends a fixed local burst and extrapolates its observed completion
rate to requests per minute. It verifies the assignment threshold in the local
Docker environment; it is not a sustained production-capacity benchmark. Median
and p95 latency are informational only and are not enforced as an SLA.

The assignment supplies only the mutable `latest` service-image tag, so exact
service reproducibility depends on Docker Hub retaining that image unchanged.
