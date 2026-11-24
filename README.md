# Farmer Procurement Slot Scheduling and Wait Time Reduction

**Problem ID:** SIH26032
**Course / Section / Group:** CSE276 / K3P25LH / G24
**Initial research benchmark:** Punjab, India
**Application scope:** India-wide directory architecture; source-backed seed coverage is partial
**Status:** Academic prototype. No procurement centre is connected for live operations.

This repository contains the Aapurtikar React/TypeScript website, a FastAPI status API, scheduling/evaluation services, and an optional local PostgreSQL foundation. The farmer portal has a national State/UT selector, district and market/centre selection, crop/date inputs, and a slot preview that carries the selections forward. The seed directory currently contains 76 named e-NAM APMC/mandi and government procurement-centre references across 20 States/UTs; these entity types and their source/verification statuses are kept separate. This is a partial directory, not complete national coverage. A selectable sample time window can create a local-only demo reservation that appears on the centre desk. It is not sent to an API or stored in the backend. Real bookings, published slots, live queue and live wait estimates remain intentionally disabled. No real farmer, booking, queue, or operational records are included.

## Mandatory CA-1 objectives

1. Build a scheduling system that allocates arrival slots and publishes expected wait, reducing total queueing.
2. Produce a slot allocation policy compared against unmanaged arrival on total wait.
3. Report mean and worst-case wait, throughput, fairness spread.

**Mandatory baseline:** unmanaged first-come-first-served (FCFS).
**Required deliverable:** slot booking interface with live wait estimate.

These are target requirements, not all achieved operational outcomes. The website is an academic prototype: the farmer can complete a local-only simulated reservation for demonstration, while real booking and live wait estimates remain disabled. The national market directory is source-tracked but not complete. Analytics separates (a) historical Indian mandi demand data replayed through a synthetic farmer-level queue simulation and (b) real-centre operational evidence, which remains unavailable. The modelled reductions are not measured field improvements. Do not enable booking or present live estimates until an authorized centre configuration and sufficient genuine operational observations exist. See [requirements and evaluation plan](docs/requirements_and_evaluation.md), the [scheduling methodology](docs/scheduling_methodology.md), the [India mandi benchmark provenance](docs/india_mandi_benchmark_provenance.md), and the [CA-1 compliance checklist](report/university_compliance_checklist.md).

The supplied CA-1 format requires Chapters 1–9 in the listed order, IEEE numbered citations, a 12–20 page report from Chapter 1 through References, and an 8–10 slide presentation targeting approximately 8 minutes plus questions. The compliance checklist maps these requirements to planned artifacts. The AI-use declaration and Appendix A contributions/signatures must use truthful student-supplied information.

## Requirements

- Windows 10/11 with PowerShell
- Python 3.14 and pip
- Node.js 26 LTS and npm
- Docker Desktop with its Linux engine running, only if using the Compose PostgreSQL service

## Setup on Windows

From the repository root in PowerShell. The API and frontend do not need PostgreSQL to start; PostgreSQL is an optional schema-validation target and is not currently connected to API routes.

```powershell
# Create the backend environment with the Python 3.14 launcher.
py -3.14 -m venv .venv
# If the Python launcher is unavailable, use the full path to your installed Python 3.14 executable:
# $pythonExe = 'C:\Path\To\Python314\python.exe'
# & $pythonExe -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# Optional: only needed to start the Docker Compose PostgreSQL service.
Copy-Item .env.example .env
notepad .env

# Optional: Docker Desktop's Linux engine must be running.
docker compose up -d postgres
docker compose ps
```

### Start the application

Use two PowerShell terminals from the repository root. In the first terminal, start FastAPI:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir src/backend --host 127.0.0.1 --port 8000 --reload
```

In the second terminal, start Vite:

```powershell
Set-Location src/frontend
npm.cmd ci  # first setup only
npm.cmd run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to `http://127.0.0.1:8000`, as configured in `src/frontend/vite.config.ts`. FastAPI's health endpoint is `http://127.0.0.1:8000/api/v1/health`; interactive API documentation is at `http://127.0.0.1:8000/docs`. `--strictPort` makes Vite stop with a clear error if 5173 is occupied instead of quietly changing the demo URL.

See [the live local demonstration guide](docs/live_demo_guide.md) for all five view URLs, API checks, expected safety statuses and troubleshooting. In the current audit environment, localhost HTTP access returned Windows `WinError 10013`; API/browser connectivity has not been verified here.

For a PostgreSQL migration, set `DATABASE_URL` explicitly in the PowerShell terminal where Alembic will run. The app does not load `.env` automatically and currently does not connect to PostgreSQL from API requests:

```powershell
$env:DATABASE_URL = 'postgresql+psycopg://procurement_app:YOUR_LOCAL_PASSWORD@localhost:5432/procurement_slots'
python -m alembic -c src/backend/alembic.ini upgrade head
python -m alembic -c src/backend/alembic.ini current
```

Replace the example password locally. Do not commit `.env` or put credentials in source files.

## Tests and build

From the repository root (run the frontend checks from `src/frontend`):

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q
python -m pytest tests/backend/test_scheduling_services.py tests/backend/test_evaluation_pipeline.py -q
python -m pip check
Set-Location src/frontend
npm.cmd run typecheck
npm.cmd run build
```

Backend tests exercise API handler contracts, scheduling/evaluation logic and schema constraints in isolated test storage; they do not create project records or connect to PostgreSQL. `npm.cmd run typecheck` checks TypeScript; `npm.cmd run build` checks TypeScript and creates the production frontend bundle. The interface has no separate frontend or browser automation suite. **Audit limitation:** PostgreSQL runtime and browser/HTTP integration were not verified in the current Windows environment; see [the Phase 8 technical audit](report/phase8_technical_audit.md).

### Website pages

- `/#home` — Aapurtikar overview, source-data profile and workflow map
- `/#farmer` — India-wide State/UT → district → source-listed mandi/centre selection, commodity and date inputs
- `/#slots` — carries the farmer selections forward; sample time windows can be selected and a local demo reservation can be confirmed
- `/#staff` — centre desk shows the local demo reservation separately from unavailable live check-ins, queue and waiting-time states
- `/#analytics` — separate tabs for offline simulation results and unavailable real-centre operational evidence

Use the navigation at the top of the page to move between views. API status is informational and does not enable any operational action. Demo reservations exist only in frontend page-session state and disappear on refresh; they do not call the booking API. The research benchmark is embedded as aggregate static output in `src/frontend/src/researchData.ts`, so it remains visible even if the local API is temporarily offline. The source-tracked market/centre seed is in `src/frontend/src/nationalDirectory.ts` and `data/india/centre-directory-seed.csv`; read [the national directory sourcing notes](docs/india-directory-sourcing.md) before describing any listing as an active procurement centre.


## Indian mandi data and synthetic queue benchmark

The Analytics page uses the project's collected Indian public dataset: ICTD–IIT Delhi's `Commodity_Analysis` repository, Punjab potato wholesale arrivals for 1–30 November 2021. The cleaned source profile contains 1,410 market-day rows across 81 markets and 25,582.56 tonnes of reported arrivals. The UI shows the five highest-volume markets, preserving the market-level aggregate context.

Because the source does not contain individual farmer arrival timestamps, service-start times or service durations, the benchmark creates 10,981 synthetic farmer visit events using a 2.5-tonne conversion threshold, a morning-weighted 06:00–14:00 arrival profile, 15-minute mean synthetic service duration and eight assumed bays. Thirty Monte Carlo replications compare FCFS, hourly batches, 30-minute slots and 15-minute staggered slots. The UI labels every result as an offline simulation. The 15-minute scenario's 81.6% mean and 82.1% P95 on-site wait reductions are conditional model outputs, not real-centre performance. The trade-off in booking lead and elapsed time is displayed alongside them.

Only aggregate benchmark outputs are embedded in the frontend; the UI does not bundle the raw cleaned CSV or synthetic event-level trace. The upstream repository did not include an explicit licence file in the inspected version. Confirm redistribution permissions before publishing the source CSV publicly. Full source links, transformations, assumptions and wording guidance are in [benchmark provenance](docs/india_mandi_benchmark_provenance.md).

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/health` | API liveness and explicit booking, estimate, centre and database-check statuses |
| GET | `/api/v1/status` | Application readiness and staff-permission status |
| GET | `/api/v1/centres/proposed` | Proposed CMS Kapurthala candidate; unverified, no hours/capacity |
| GET | `/api/v1/configuration/crop-seasons` | Paddy/wheat project scope separately from unverified centre eligibility |
| GET | `/api/v1/bookings/availability` | Booking disabled; no slots returned |
| GET | `/api/v1/scheduling/configuration` | Required configuration gates and authorization status |
| GET | `/api/v1/analytics/availability` | Real-centre operational metric availability only; no operational results (separate synthetic benchmark is embedded in the frontend) |
| GET | `/api/v1/scheduling/readiness` | Offline calculation availability versus operational authorization gates |
| GET | `/api/v1/methodology/fcfs` | Mandatory FCFS baseline ordering and tie rules |
| GET | `/api/v1/methodology/allocation` | Proposed candidate allocation steps and unresolved approvals |
| GET | `/api/v1/metrics/definitions` | Exact metric formulas, units, valid-set requirements and result unavailability |
| GET | `/api/v1/evaluation/readiness` | Pipeline/input/validation/provenance status; does not run an evaluation |
| POST | `/api/v1/bookings` | Always rejects with HTTP 409 `booking_disabled`; does not persist request data |

HTTP errors use `{"error":{"code":"…","message":"…"}}`. The booking POST is only a safe rejection route; no route creates bookings or exposes live wait estimates.

## Scheduling calculations and evaluation pipeline

The pure scheduling services are under `src/backend/app/services/`. They can order FCFS arrivals, validate a user-selected slot against explicitly supplied authorization/configuration, classify late/cancelled/no-show/incomplete episodes, and calculate total/mean/worst wait, throughput and fairness spread. Slot selection returns `candidate_only` and never creates a reservation. Missing configuration or data yields `unavailable`; all policies/values must be passed explicitly.

The offline evaluation CLI accepts only an authorized event-level CSV and a reviewed settings JSON. Required columns and all settings are listed in [the dataset input contract](docs/evaluation_dataset_schema.md). No example operational dataset or default settings file is included.

```powershell
# From the repository root, with .venv activated. Set PYTHONPATH for this shell.
$env:PYTHONPATH = (Join-Path $PWD 'src/backend')
python -m app.evaluation --help

# Run only after obtaining genuine data and approved protocol/settings.
python -m app.evaluation --input 'C:\approved-data\events.csv' --settings 'C:\approved-data\evaluation-settings.json' --output 'C:\approved-data\evaluation-output.json'
```

The evaluator computes metrics for recorded FCFS and slot-policy arms; it does not simulate service or claim an improvement. It requires matching comparison blocks, exact arrival counts by block and stream, equal open-time denominators, and matching approved configuration/service references before returning a total-wait contrast. Statistical uncertainty remains uncomputed until an analysis method is approved. Do not use test fixtures as project results.

The website loads the read-only methodology and readiness endpoints in all five views. The shared methodology panel displays the exact metric formulas; loading and API errors are shown explicitly. The evaluation readiness endpoint reports `validation_status: not_run` until a separate authorized offline evaluation is conducted. These endpoints contain no sample records or measured values.

## Database and migrations

Docker Compose starts PostgreSQL only; the API currently does not connect to it. Once Docker Desktop and the local PostgreSQL service are running, set the database URL in the PowerShell session used for migrations:

```powershell
$env:DATABASE_URL = 'postgresql+psycopg://procurement_app:YOUR_LOCAL_PASSWORD@localhost:5432/procurement_slots'
python -m alembic -c src/backend/alembic.ini upgrade head
python -m alembic -c src/backend/alembic.ini current
```

Replace `YOUR_LOCAL_PASSWORD` with the local value from `.env`; do not commit it. The initial migration creates schema only and inserts no roles, users, centres, crop seasons, slots, bookings, queue events or audit entries. Migration commands require the database URL in the current shell. For schema changes, update the SQLAlchemy models, create and review a migration with `python -m alembic -c src/backend/alembic.ini revision --autogenerate -m "describe change"`, then apply it with `upgrade head`.

The persistence models cover users, roles and role links, farmer profiles, procurement centres, crop/season configuration, slots, bookings, booking events, queue service events, and audit logs. Authorization provenance fields are optional until approval exists. Slots require explicit configured values; there are no operational defaults. Authentication, role enforcement, capacity transactions and operational event routes are not implemented.

## PostgreSQL notes

The Compose file uses a named Docker volume and binds the database port to localhost. The health endpoint reports API liveness and explicitly returns `database_status: not_checked`; it does not claim PostgreSQL is reachable. No ORM session is connected to an application route.

Never commit `.env`, database files, or local raw/processed operational data. `.gitignore` excludes these paths. Do not collect real farmer information until the required project and centre approvals and privacy process are in place.

## Project structure

```text
data/                 Raw/processed folders are protected; metadata, benchmark aggregates and India directory seed
docs/                 Architecture notes
notebooks/            EDA outline only; no observations or charts
src/backend/app/      FastAPI status API, models, pure scheduling services and evaluation CLI
src/backend/alembic/  Alembic environment and schema migrations
src/frontend/         React and TypeScript application
tests/backend/        API, schema, scheduling and TEST DATA-only evaluation tests
app/                  Reserved application artifacts
results/              Reserved for measured results; currently empty
report/               Draft report and live-demo/compliance evidence; refresh after final UI screenshots
presentation/         Presentation placeholder; refresh with final UI screenshots
```

See [docs/architecture.md](docs/architecture.md) for system boundaries and safeguards. Dataset details are in [data/metadata/source_register.csv](data/metadata/source_register.csv), and the field template is [data/metadata/data_dictionary_template.csv](data/metadata/data_dictionary_template.csv).
