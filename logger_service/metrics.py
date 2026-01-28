from prometheus_client import Counter, Histogram, Gauge, start_http_server

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "Request latency",
    ["method", "path"],
)

IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "In-progress HTTP requests",
)

def start_metrics_server():
    start_http_server(9090)
