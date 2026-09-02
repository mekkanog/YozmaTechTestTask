from concurrent.futures import ThreadPoolExecutor
from statistics import median
from time import monotonic

import pytest


pytestmark = pytest.mark.load


def test_observed_throughput_exceeds_one_thousand_requests_per_minute(
    user1_client, settings, record_property
):
    def list_integrations(_: int) -> tuple[int, float]:
        started = monotonic()
        response = user1_client.get("integrations")
        return response.status_code, monotonic() - started

    started = monotonic()
    with ThreadPoolExecutor(max_workers=settings.load_workers) as executor:
        results = list(executor.map(list_integrations, range(settings.load_requests)))
    duration = monotonic() - started

    statuses = [status for status, _ in results]
    latencies = sorted(latency for _, latency in results)
    failures = [status for status in statuses if status != 200]
    requests_per_minute = len(results) / duration * 60
    p95 = latencies[min(int(len(latencies) * 0.95), len(latencies) - 1)]

    record_property("requests", len(results))
    record_property("measurement", "fixed local burst; rate extrapolated per minute")
    record_property("duration_seconds", round(duration, 3))
    record_property("requests_per_minute", round(requests_per_minute, 1))
    record_property("median_latency_ms", round(median(latencies) * 1000, 2))
    record_property("p95_latency_ms", round(p95 * 1000, 2))
    record_property("failures", len(failures))

    assert not failures, f"{len(failures)} requests returned non-200 statuses"
    assert requests_per_minute >= 1000, (
        f"measured {requests_per_minute:.1f} requests/minute, expected at least 1000"
    )
