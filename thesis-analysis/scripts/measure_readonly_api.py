from __future__ import annotations

import json
import statistics
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


BASE_URL = "http://127.0.0.1:8000"
OUTPUT = Path("/Users/eddy/Codes/design-platform/thesis-analysis/test-results/api-readonly-benchmark.json")
ENDPOINTS = [
    "/api/health",
    "/api/home",
    "/api/products?page=1&page_size=12",
    "/api/categories",
]
REQUESTS_PER_ENDPOINT = 30
CONCURRENCY = 5


def request_once(path: str) -> dict[str, object]:
    started = time.perf_counter()
    status = 0
    size = 0
    error = ""
    try:
        with urllib.request.urlopen(BASE_URL + path, timeout=10) as response:
            payload = response.read()
            status = response.status
            size = len(payload)
    except (urllib.error.URLError, TimeoutError) as exc:
        error = str(exc)
    elapsed_ms = (time.perf_counter() - started) * 1000
    return {"status": status, "elapsed_ms": elapsed_ms, "bytes": size, "error": error}


def summarize(path: str) -> dict[str, object]:
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(request_once, path) for _ in range(REQUESTS_PER_ENDPOINT)]
        rows = [future.result() for future in as_completed(futures)]
    elapsed = sorted(float(row["elapsed_ms"]) for row in rows)
    successes = [row for row in rows if row["status"] == 200]
    p95_index = max(0, int(len(elapsed) * 0.95) - 1)
    return {
        "path": path,
        "requests": len(rows),
        "concurrency": CONCURRENCY,
        "successes": len(successes),
        "errors": len(rows) - len(successes),
        "mean_ms": round(statistics.fmean(elapsed), 2),
        "median_ms": round(statistics.median(elapsed), 2),
        "p95_ms": round(elapsed[p95_index], 2),
        "min_ms": round(min(elapsed), 2),
        "max_ms": round(max(elapsed), 2),
        "response_bytes": int(successes[0]["bytes"]) if successes else 0,
    }


def main() -> None:
    overall_started = time.perf_counter()
    report = {
        "scope": "local read-only demonstration benchmark",
        "base_url": BASE_URL,
        "requests_per_endpoint": REQUESTS_PER_ENDPOINT,
        "concurrency": CONCURRENCY,
        "results": [summarize(path) for path in ENDPOINTS],
        "total_elapsed_seconds": round(time.perf_counter() - overall_started, 2),
        "limitations": [
            "localhost only",
            "read-only endpoints only",
            "small sample size",
            "not a production load or capacity test",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
