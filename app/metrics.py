import time

from fastapi import Request
from prometheus_client import Counter, Gauge, Histogram

from app.db import db_is_up

# Errors are not a separate counter: they are requests with status 5xx,
# so PromQL filters this one counter by its status label.
REQUESTS = Counter(
    "http_requests_total", "HTTP requests handled", ["method", "route", "status"]
)
LATENCY = Histogram(
    "http_request_duration_seconds", "Time to handle a request", ["method", "route"]
)
DB_UP = Gauge("db_up", "1 if the database answers SELECT 1, else 0")
# Runs on every scrape, so the value is never stale.
DB_UP.set_function(db_is_up)


async def record_metrics(request: Request, call_next):
    start = time.perf_counter()
    status = 500  # stays 500 if the endpoint crashes before returning
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        # The route template ("/tasks/{task_id}"), never the raw path
        # ("/tasks/42"): one series per endpoint, not one per id.
        route = request.scope.get("route")
        path = route.path if route else "unmatched"
        if path != "/metrics":
            REQUESTS.labels(request.method, path, str(status)).inc()
            LATENCY.labels(request.method, path).observe(time.perf_counter() - start)
