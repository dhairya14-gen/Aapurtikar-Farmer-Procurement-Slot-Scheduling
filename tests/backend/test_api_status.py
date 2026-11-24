"""Endpoint contract tests invoke handlers in-process without external services."""

import json

from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.main import (
    analytics_availability,
    allocation_methodology,
    app,
    booking_availability,
    crop_season_status,
    health_check,
    evaluation_readiness,
    fcfs_methodology,
    http_error_handler,
    proposed_centre,
    metric_definitions,
    scheduling_readiness,
    scheduling_configuration_status,
)


def test_health_endpoint_returns_application_safety_status() -> None:
    body = health_check()

    assert body["application_status"] == "unverified"
    assert body["booking_status"] == "disabled"
    assert body["booking_enabled"] is False
    assert body["wait_estimate_status"] == "disabled"


def test_proposed_centre_is_unverified_and_has_no_operational_values() -> None:
    body = proposed_centre()

    assert body["name"] == "CMS Kapurthala, New Dana Mandi"
    assert body["verification_status"] == "unverified"
    assert body["participation_status"] == "awaiting_authorization"
    assert body["operating_hours"] is None
    assert body["capacity"] is None
    assert body["booking_enabled"] is False


def test_crop_season_eligibility_is_not_assumed() -> None:
    body = crop_season_status()

    assert body["status"] == "awaiting_authorization"
    assert body["configured"] is False
    assert [entry["status"] for entry in body["centre_eligibility"]] == ["unverified", "unverified"]
    assert all(entry["seasons"] == [] for entry in body["centre_eligibility"])


def test_booking_availability_is_disabled_and_create_route_rejects() -> None:
    availability = booking_availability()
    create_route = next(route for route in app.routes if getattr(route, "path", None) == "/api/v1/bookings")
    rejected = create_route.endpoint()
    response_body = json.loads(rejected.body)

    assert availability["available"] is False
    assert availability["slots"] is None
    assert rejected.status_code == 409
    assert response_body["error"]["code"] == "booking_disabled"
    assert response_body["booking_enabled"] is False


def test_invalid_api_path_has_structured_error_response() -> None:
    request = Request({"type": "http", "method": "GET", "path": "/unknown", "headers": [], "query_string": b"", "server": ("test", 80), "scheme": "http", "http_version": "1.1"})
    response = http_error_handler(request, StarletteHTTPException(status_code=404, detail="Not Found"))
    body = json.loads(response.body)

    assert response.status_code == 404
    assert body["error"]["code"] == "not_found"
    assert body["error"]["message"] == "Not Found"


def test_scheduling_configuration_and_analytics_remain_unavailable() -> None:
    scheduling = scheduling_configuration_status()
    analytics = analytics_availability()

    assert scheduling["configured"] is False
    assert scheduling["booking_enabled"] is False
    assert scheduling["wait_estimate_status"] == "disabled"
    assert analytics["results_available"] is False
    assert {item["name"] for item in analytics["metrics"]} == {
        "mean_wait", "worst_case_wait", "throughput", "fairness_spread"
    }


def test_engine_methodology_and_evaluation_readiness_are_exposed_safely() -> None:
    readiness = scheduling_readiness()
    fcfs = fcfs_methodology()
    allocation = allocation_methodology()
    metrics = metric_definitions()
    evaluation = evaluation_readiness()

    assert readiness["engine_status"] == "available_for_offline_calculation"
    assert readiness["operational_status"] == "awaiting_authorization"
    assert readiness["booking_status"] == "disabled"
    assert fcfs["status"] == "mandatory_baseline"
    assert "actual recorded check-in" in fcfs["arrival_order"].lower()
    assert allocation["status"] == "candidate_design_requires_approval"
    assert allocation["booking_enabled"] is False
    assert {item["name"] for item in metrics["definitions"]} == {
        "total_wait", "mean_wait", "worst_case_wait", "throughput", "fairness_spread"
    }
    assert metrics["results_status"] == "unavailable_no_genuine_observations"
    assert evaluation["validation_status"] == "not_run"
    assert evaluation["results_status"] == "unavailable"
    assert evaluation["test_fixtures_included"] is False


def test_new_read_only_api_routes_are_mounted() -> None:
    routes = {
        "/api/v1/scheduling/readiness": "engine_status",
        "/api/v1/methodology/fcfs": "arrival_order",
        "/api/v1/methodology/allocation": "steps",
        "/api/v1/metrics/definitions": "definitions",
        "/api/v1/evaluation/readiness": "validation_status",
    }
    for path, expected_key in routes.items():
        route = next(route for route in app.routes if getattr(route, "path", None) == path)
        assert expected_key in route.endpoint()
    readiness_route = next(route for route in app.routes if getattr(route, "path", None) == "/api/v1/scheduling/readiness")
    evaluation_route = next(route for route in app.routes if getattr(route, "path", None) == "/api/v1/evaluation/readiness")
    assert readiness_route.endpoint()["booking_status"] == "disabled"
    assert evaluation_route.endpoint()["results_status"] == "unavailable"
