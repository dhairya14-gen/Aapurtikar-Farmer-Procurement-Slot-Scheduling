"""Read-only project status API; operational actions remain disabled."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(
    title="Farmer Procurement Slot Scheduling API",
    version="0.2.0",
    description=(
        "Status APIs and persistence foundation for SIH26032. Booking and live wait "
        "estimates are disabled; no operational centre configuration is loaded."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(StarletteHTTPException)
def http_error_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    if exc.status_code == 404:
        code = "not_found"
    elif exc.status_code == 405:
        code = "method_not_allowed"
    else:
        code = "request_rejected"
    message = exc.detail if isinstance(exc.detail, str) else "The request could not be completed."
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": message}},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
def validation_error_handler(_request: Request, _exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "invalid_request", "message": "Request validation failed."}},
    )


@app.get("/api/v1/health", tags=["health"], status_code=200)
def health_check() -> dict[str, str | bool]:
    """Report liveness and safety gates without checking the database."""
    return {
        "status": "ok",
        "service": "farmer-procurement-api",
        "application_status": "unverified",
        "booking_status": "disabled",
        "booking_enabled": False,
        "wait_estimate_status": "disabled",
        "centre_status": "unverified",
        "database_status": "not_checked",
    }


@app.get("/api/v1/status", tags=["health"])
def application_status() -> dict[str, object]:
    """Summarize project readiness gates."""
    return {
        "application_status": "unverified",
        "booking_status": "disabled",
        "wait_estimate_status": "disabled",
        "staff_permissions_status": "awaiting_authorization",
        "database_status": "not_checked",
    }


@app.get("/api/v1/centres/proposed", tags=["configuration"])
def proposed_centre() -> dict[str, object]:
    """Return only the student-proposed centre label and known project geography."""
    return {
        "candidate_key": "cms-kapurthala-new-dana-mandi",
        "name": "CMS Kapurthala, New Dana Mandi",
        "district": "Kapurthala",
        "state": "Punjab",
        "project_role": "proposed_academic_candidate",
        "verification_status": "unverified",
        "participation_status": "awaiting_authorization",
        "operational_status": "disabled",
        "operating_hours": None,
        "capacity": None,
        "booking_enabled": False,
    }


@app.get("/api/v1/configuration/crop-seasons", tags=["configuration"])
def crop_season_status() -> dict[str, object]:
    """Separate project crop scope from centre-approved eligibility."""
    return {
        "status": "awaiting_authorization",
        "configured": False,
        "project_crop_scope": ["paddy", "wheat"],
        "centre_eligibility": [
            {"crop": "paddy", "status": "unverified", "seasons": []},
            {"crop": "wheat", "status": "unverified", "seasons": []},
        ],
        "booking_enabled": False,
    }


@app.get("/api/v1/bookings/availability", tags=["booking"])
def booking_availability() -> dict[str, object]:
    """Explain why booking is unavailable; no slots are queried or published."""
    return {
        "status": "disabled",
        "available": False,
        "booking_enabled": False,
        "reason": "Centre participation and operational configuration are not authorized and verified.",
        "slots": None,
    }


@app.get("/api/v1/scheduling/configuration", tags=["configuration"])
def scheduling_configuration_status() -> dict[str, object]:
    """List required configuration gates without assigning operational values."""
    required = [
        "authorized centre participation",
        "crop and season eligibility",
        "operating calendar and closures",
        "capacity and capacity unit",
        "staffed resources and routing",
        "service event definitions and duration evidence",
        "approved slot, walk-in, late-arrival, cancellation and no-show policy",
    ]
    return {
        "status": "awaiting_authorization",
        "configured": False,
        "booking_enabled": False,
        "wait_estimate_status": "disabled",
        "required_configuration": [
            {"item": item, "status": "awaiting_authorization"} for item in required
        ],
    }


@app.get("/api/v1/scheduling/readiness", tags=["scheduling"])
def scheduling_readiness() -> dict[str, object]:
    """Report software readiness separately from operational authorization."""
    return {
        "engine_status": "available_for_offline_calculation",
        "operational_status": "awaiting_authorization",
        "configuration_status": "awaiting_authorization",
        "booking_status": "disabled",
        "wait_estimate_status": "disabled",
        "components": {
            "fcfs_baseline": "available",
            "candidate_slot_review": "candidate_only",
            "metric_calculations": "available_for_validated_inputs",
            "fastapi_booking_integration": "disabled",
        },
        "limitations": [
            "No verified centre configuration is loaded.",
            "No genuine operational observations are available.",
            "Candidate slot review does not reserve capacity or create bookings.",
        ],
    }


@app.get("/api/v1/methodology/fcfs", tags=["methodology"])
def fcfs_methodology() -> dict[str, object]:
    return {
        "name": "Unmanaged first-come-first-served (FCFS)",
        "status": "mandatory_baseline",
        "arrival_order": "Actual recorded check-in order within the relevant service stream.",
        "tie_break": "Server-assigned event sequence, then documented stable episode key.",
        "scope_rule": "Use the same authorized crop eligibility, safety rules and resource routing as the proposed condition.",
        "booking_enabled": False,
    }


@app.get("/api/v1/methodology/allocation", tags=["methodology"])
def allocation_methodology() -> dict[str, object]:
    return {
        "name": "Proposed arrival-slot allocation",
        "status": "candidate_design_requires_approval",
        "steps": [
            "Generate candidate slots only within authorized operating periods and crop/season scope.",
            "Check explicit centre, participation, eligibility, calendar, capacity, routing and policy authorization.",
            "Review candidate capacity without reserving it; atomic reservation is a future requirement.",
            "Use workload ranking only after its inputs and tie rules are approved and validated.",
            "Preserve check-in order within a slot unless another rule is authorized.",
        ],
        "unresolved_policies": ["allocation ranking", "walk-ins", "late arrivals", "cancellations", "no-shows", "capacity release"],
        "booking_enabled": False,
        "wait_estimate_status": "disabled",
    }


@app.get("/api/v1/metrics/definitions", tags=["metrics"])
def metric_definitions() -> dict[str, object]:
    return {
        "results_status": "unavailable_no_genuine_observations",
        "definitions": [
            {"name": "total_wait", "formula": "TW = sum(W_i for i in V_W)", "unit": "person-minutes", "valid_set": "Deduplicated genuine in-scope episodes with valid provenance, check-in and service-start; W_i >= 0."},
            {"name": "mean_wait", "formula": "MW = TW / N_W", "unit": "minutes per valid served episode", "denominator": "N_W = |V_W|; unavailable if N_W = 0."},
            {"name": "worst_case_wait", "formula": "WW = max(W_i for i in V_W)", "unit": "minutes; observed sample maximum", "denominator": "N_W; unavailable if N_W = 0."},
            {"name": "throughput", "formula": "TP = N_C / H_open", "unit": "completed episodes per scheduled open hour", "denominator": "Authorized scheduled open minutes / 60; N_C requires valid check-in, start and completion."},
            {"name": "fairness_spread", "formula": "FS = max_g(mean(W_i in g)) - min_g(mean(W_i in g))", "unit": "minutes between approved subgroup means", "validity": "Requires predeclared, authorized, privacy-reviewed groups and adequate observations; otherwise unavailable."},
        ],
        "provenance_status": "no_evaluation_input_supplied",
    }


@app.get("/api/v1/evaluation/readiness", tags=["evaluation"])
def evaluation_readiness() -> dict[str, object]:
    return {
        "pipeline_status": "implemented_for_authorized_observed_data",
        "input_status": "unavailable_no_genuine_dataset_supplied",
        "validation_status": "not_run",
        "results_status": "unavailable",
        "provenance_status": "not_available",
        "required_inputs": ["authorized event-level dataset", "source and permission references", "approved comparison protocol and configuration references", "explicit evaluation settings"],
        "test_fixtures_included": False,
        "booking_enabled": False,
        "wait_estimate_status": "disabled",
    }


@app.get("/api/v1/analytics/availability", tags=["analytics"])
def analytics_availability() -> dict[str, object]:
    """Expose planned metric names while verified results are unavailable."""
    units = {
        "mean_wait": "minutes per valid served visit",
        "worst_case_wait": "minutes; observed sample maximum",
        "throughput": "completed service episodes per scheduled open hour",
        "fairness_spread": "minutes between approved subgroup mean waits",
    }
    return {
        "status": "disabled",
        "results_available": False,
        "message": "Verified results are unavailable because no authorized operational observations exist.",
        "metrics": [
            {"name": name, "status": "awaiting_authorization", "unit": unit}
            for name, unit in units.items()
        ],
    }


@app.post("/api/v1/bookings", tags=["booking"], status_code=409)
def reject_booking_attempt() -> JSONResponse:
    """Reject booking creation without inspecting or persisting submitted data."""
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "booking_disabled",
                "message": "Bookings are disabled until centre participation and configuration are authorized and verified.",
            },
            "booking_enabled": False,
        },
    )
