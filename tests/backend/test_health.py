from app.main import app


def test_health_endpoint_reports_live_api_and_disabled_bookings() -> None:
    route = next(route for route in app.routes if getattr(route, "path", None) == "/api/v1/health")

    assert "GET" in route.methods
    assert route.status_code == 200
    assert route.endpoint() == {
        "status": "ok",
        "service": "farmer-procurement-api",
        "application_status": "unverified",
        "booking_status": "disabled",
        "booking_enabled": False,
        "wait_estimate_status": "disabled",
        "centre_status": "unverified",
        "database_status": "not_checked",
    }
