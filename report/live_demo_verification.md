# Live Demonstration Verification

**Project:** Farmer Procurement Slot Scheduling and Wait Time Reduction
**Problem ID:** SIH26032
**Demonstration date:** 15 November 2026

This record uses the live demonstration observations and HTTP response outputs supplied for this verification. It does not add test results or approvals beyond those observations.

## Website verification

The website opened successfully in Google Chrome at [http://127.0.0.1:5173/#home](http://127.0.0.1:5173/#home). The following five pages were manually opened and visually inspected:

| Page | Recorded observation |
|---|---|
| Home | Project identity, SIH26032, academic prototype label, and project introduction displayed. |
| Farmer dashboard | Proposed centre, unverified crop and season information, and unavailable booking functionality displayed. |
| Slot selection | No available slots published; booking confirmation disabled. |
| Staff dashboard | Centre operations disabled, queue not connected, and upcoming arrivals disabled. |
| Analytics | Metric definitions displayed; verified results unavailable; baseline comparison pending. |

## Live API verification

These results are from the live HTTP demonstration, distinct from earlier tests that invoked route handlers directly.

### `GET /api/v1/health`

```text
status: ok
service: farmer-procurement-api
application_status: unverified
booking_status: disabled
booking_enabled: false
wait_estimate_status: disabled
centre_status: unverified
database_status: not_checked
```

### `GET /api/v1/status`

```text
application_status: unverified
booking_status: disabled
wait_estimate_status: disabled
staff_permissions_status: awaiting_authorization
database_status: not_checked
```

### `POST /api/v1/bookings`

```text
HTTP status: 409
Outcome: booking request rejected as expected.
```

The 409 above is recorded as a live HTTP result. It is separate from earlier direct handler tests, which invoked the route function without sending an HTTP request.

## Limitations and safety status

- CMS Kapurthala, New Dana Mandi remains proposed and unverified.
- No genuine operational dataset is available.
- No measured waiting-time improvement is claimed.
- PostgreSQL runtime is not verified.
- The running API reports `database_status: not_checked` and does not check database connectivity.
- Staff authorization is not implemented.
- Real booking and live wait estimates remain disabled.

## Screenshot evidence

The `report/demo_evidence/` folder is present for actual screenshots. No screenshot files were present in the project folder when checked. Copy actual demonstration screenshots into that folder manually; none are claimed as saved by this report.
