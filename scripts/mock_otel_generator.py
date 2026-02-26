import time
import requests
import random
import os

OTEL_COLLECTOR_URL = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318/v1/traces")

def send_mock_span(service_name, span_name, status_code=0):
    span = {
        "resourceSpans": [{
            "resource": {
                "attributes": [{"key": "service.name", "value": {"stringValue": service_name}}]
            },
            "scopeSpans": [{
                "spans": [{
                    "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
                    "spanId": "00f067aa0ba902b7",
                    "name": span_name,
                    "kind": 2,
                    "status": {"code": status_code},
                    "startTimeUnixNano": int(time.time() * 1e9),
                    "endTimeUnixNano": int((time.time() + 0.1) * 1e9)
                }]
            }]
        }]
    }
    try:
        requests.post(OTEL_COLLECTOR_URL, json=span)
    except Exception as e:
        print(f"Failed to send span: {e}")

def main():
    print("🚀 Mock OTel Generator Started...")
    while True:
        # Normal traffic
        send_mock_span("user-service", "get_user", 1)
        
        # Check for failure injection (could be a shared volume or env var)
        if os.path.exists("/tmp/inject_leak"):
            print("🔥 Injecting Database Connection Leak...")
            send_mock_span("policy-service", "db_query", 2) # 2 = Error
            send_mock_span("policy-service", "db_connect_timeout", 2)
        
        time.sleep(2)

if __name__ == "__main__":
    main()
