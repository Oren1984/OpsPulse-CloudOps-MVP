from prometheus_client import Counter, Gauge, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "opspulse_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "opspulse_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
)

HTTP_ERRORS_TOTAL = Counter(
    "opspulse_http_errors_total",
    "Total HTTP 5xx responses",
    ["method", "path"],
)

DATABASE_UP = Gauge(
    "opspulse_database_up",
    "1 if the database connection is healthy, else 0",
)

INCIDENTS_TOTAL = Gauge(
    "opspulse_incidents_open_total",
    "Number of open incidents",
)

DEMO_FAILURE_ACTIVE = Gauge(
    "opspulse_demo_failure_active",
    "1 if the controlled demo-failure mode is currently active",
)

BUILD_INFO = Gauge(
    "opspulse_build_info",
    "Static build/deployment metadata (value is always 1)",
    ["version", "environment"],
)
