# Initial Architecture

## Academic allocation

- Course: CSE276
- Section: K3P25LH
- Group: G24
- Project: Farmer Procurement Slot Scheduling and Wait Time Reduction
- SIH problem: SIH26032
- Proposed location: Kapurthala district, Punjab, India
- Proposed centre: CMS Kapurthala, New Dana Mandi (unverified candidate only)

Mandatory objectives:

1. Build a scheduling system that allocates arrival slots and publishes expected wait, reducing total queueing.
2. Produce a slot allocation policy compared against unmanaged arrival on total wait.
3. Report mean and worst-case wait, throughput, fairness spread.

Mandatory baseline: unmanaged first-come-first-served (FCFS). Required deliverable: slot booking interface with live wait estimate. These are project requirements. The current foundation does not support booking creation or live wait estimates; it must not be represented as satisfying the operational deliverable yet.

## Components

- **React + TypeScript frontend:** Responsive Aapurtikar website with Overview, Farmer Portal, Slot Preview, Centre Desk and Analytics views. Booking, slot publication, live estimates, queue records and real-centre metrics remain unavailable. The Analytics view also embeds a separate offline Punjab mandi synthetic benchmark as aggregate research output; source provenance and assumptions are documented in `india_mandi_benchmark_provenance.md`. The home view calls the API health endpoint through the Vite `/api` proxy.
- **FastAPI backend:** Status and configuration API with a fixed booking-disabled response. CORS is limited to local development origins. Authentication, farmer profile, queue, scheduling and analytics API endpoints do not exist.
- **PostgreSQL:** Optional local service via Docker Compose. The database is explicit in `.env`; the Compose file requires the developer to set a local password. The API does not connect to it yet.
- **SQLAlchemy and Alembic:** SQLAlchemy metadata and an initial schema-only migration are present. Migrations use explicit `DATABASE_URL`; no seed data is included.
- **Pandas and NumPy:** Pinned for later analysis of permitted, provenance-documented data; no data or metrics are included.

## Centre and booking safety

CMS Kapurthala, New Dana Mandi is a proposed academic candidate only. Its crop eligibility, opening hours, capacity, exact location, and participation remain unverified. No operational centre configuration is stored in the application. The interface labels the candidate as unverified; the API reports booking disabled and centre unverified. The disabled UI control cannot create a booking; the API's only booking route returns a fixed 409 rejection without storing request data.

Booking availability must remain disabled until an authorized centre operator verifies a centre, crop/season configuration, operating calendar, and capacity. The system must not infer those values from public market aggregates.

## Data and evaluation integrity

- No fabricated operational records, seed data, or field-performance claims.
- The separate offline Punjab mandi benchmark uses public historical market-day aggregate volumes and explicitly generated synthetic farmer-level events; its charts are labelled scenario simulation and must not be represented as operational evidence.
- Public imports must retain source URL, retrieval time, licence/terms, geographic coverage, and validation metadata.
- Future operational event records require authorization and must be collected at the time of the event, with actor and timestamp provenance.
- Predicted wait and observed wait must remain separate. No improvement claim should be made without genuine baseline and intervention observations.

## Scheduling calculations and evaluation design

The proposed policy and metric contract are documented in [`scheduling_methodology.md`](scheduling_methodology.md). The mandatory comparison condition is unmanaged actual-arrival FCFS within the authorized service stream, with a server event sequence for timestamp ties. The proposed arm assigns slots only from an authorized, effective-dated centre calendar and capacity configuration, and retains check-in FCFS within a slot unless an approved rule says otherwise.

Do not add operational defaults for capacity, crop/season eligibility, opening periods, resource routing, service durations, late arrivals, no-shows, cancellations or fairness groups. Missing or expired required configuration must leave bookings disabled. Live wait must be an explicitly labeled estimate with an as-of time and evidence/coverage; it must be unavailable when validation criteria are not met. Observed wait is derived only from genuine check-in and service-start events.

Pure calculation modules now live in `src/backend/app/services/`: `baseline.py` orders FCFS arrivals per stream; `allocation.py` returns candidate slot options only after all supplied authorization gates pass and never reserves a slot; `validation.py` builds valid/censored cohorts; `waiting.py`, `throughput.py` and `fairness.py` calculate the approved metrics; `events.py` classifies late arrival, cancellation, no-show and incomplete-service outcomes; `metrics.py` aggregates them. These functions do not access the database or FastAPI. They require explicit inputs and never invent capacity, opening hours, eligibility, service times or authorization.

The offline `src/backend/app/evaluation/` CLI validates documented CSV/settings inputs, computes observed metrics for FCFS and slot-policy arms, checks exact matched demand by comparison block and service stream, compares total wait descriptively, and records input hashes/provenance. It does not simulate counterfactual arrivals or generate a dataset. The separate Punjab mandi synthetic benchmark was run as a scenario study outside this operational evaluator. Schema and settings requirements are documented in `docs/evaluation_dataset_schema.md`. No booking, queue, live-wait or benchmark API endpoint is exposed; the benchmark summary is embedded as static frontend research data. Booking creation remains a fixed 409 rejection.

## Future request flow

```text
Farmer/staff browser
        │ HTTPS in a deployed environment; Vite proxy in local development
        ▼
React + TypeScript ───────► FastAPI API
                                  │
                                  │ SQLAlchemy (models now; database-backed routes future)
                                  ▼
                              PostgreSQL
```

## Status API

- `GET /api/v1/health` — API liveness and safety statuses. It returns `database_status: not_checked`; it does not attempt a connection.
- `GET /api/v1/status` — overall application and staff-permission status.
- `GET /api/v1/centres/proposed` — proposed CMS Kapurthala candidate with `unverified` verification, `awaiting_authorization` participation, null operating hours/capacity and disabled operational state.
- `GET /api/v1/configuration/crop-seasons` — project crop scope (paddy/wheat) separately from unverified centre eligibility; no season values are configured.
- `GET /api/v1/bookings/availability` — disabled status and no published slots.
- `GET /api/v1/scheduling/configuration` — required but unapproved configuration gates.
- `GET /api/v1/analytics/availability` — planned metric names and units; results unavailable.
- `GET /api/v1/scheduling/readiness` — offline calculation availability separated from operational authorization and configuration status.
- `GET /api/v1/methodology/fcfs` — mandatory unmanaged FCFS ordering and tie rule.
- `GET /api/v1/methodology/allocation` — proposed candidate allocation flow and unresolved operational policy approvals.
- `GET /api/v1/metrics/definitions` — methodology formulas, units and valid-data requirements; results unavailable.
- `GET /api/v1/evaluation/readiness` — pipeline availability and explicit input, validation, results and provenance status; no evaluation is run by this endpoint.
- `POST /api/v1/bookings` — deliberate `409 booking_disabled` rejection. It does not inspect or persist request data. No booking creation action exists.

API errors use a stable JSON `error.code` and `error.message` envelope. All five frontend views load the read-only methodology, metric definitions and readiness endpoints through a shared responsive panel; the analytics view separately shows planned metrics with no measured values. Loading/error states remain explicit. All UI booking controls remain disabled independently of API availability. No live wait endpoint exists.

## Database schema foundation

Models and the initial Alembic migration define users, roles, user-role links, farmer profiles, procurement centres, crop-season configuration, slots, bookings, booking events, queue service events and audit logs. Constraints cover unique identifiers, status vocabularies, authorization provenance for verified/authorized configuration, slot interval/capacity validity, and same-centre crop/slot linkage. No rows are seeded. No authentication, staff authorization enforcement, migration execution against PostgreSQL, booking transaction/capacity enforcement, event capture, or database-backed APIs are implemented. Any future operational write path must validate authorization and configuration before it is added.

Database schema commands are documented in `README.md`. PostgreSQL must be started separately with Docker Compose; the API does not currently require it for read-only status responses.

## Security foundation

Local secrets are read from ignored `.env` files and are not committed. The Compose database port binds to loopback. The API exposes no personal data and has no operational write action; its booking POST is a fixed rejection. Authentication, role and centre scoping, audit events, input validation, data retention controls, and a reviewed privacy process are required before operational use.
