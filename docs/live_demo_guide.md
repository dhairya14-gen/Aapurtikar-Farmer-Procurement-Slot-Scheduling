# Live Local Demonstration Guide

This guide starts the academic prototype on the same Windows computer. Both servers bind to loopback (`127.0.0.1`); do not change the host to `0.0.0.0` or expose either service publicly. PostgreSQL and a `.env` file are not required to run the current API or website.

## 1. Start FastAPI

Open PowerShell at the repository root and run:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir src/backend --host 127.0.0.1 --port 8000 --reload
```

Leave the terminal open. Uvicorn should report that it is running on `http://127.0.0.1:8000`.

## 2. Start React/Vite

Open a second PowerShell terminal at the repository root and run:

```powershell
Set-Location src/frontend
npm.cmd run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Run `npm.cmd ci` from `src/frontend` once if the dependencies have not yet been installed.

Leave this terminal open too. The expected website address is `http://127.0.0.1:5173`. The existing Vite proxy forwards `/api` to `http://127.0.0.1:8000`; no proxy setting was changed for this guide. `--strictPort` makes Vite stop if port 5173 is unavailable, so it will not silently choose a different URL.

If recreating the environment, use the Python version listed in the root README and install `requirements.txt` in `.venv`; the frontend package lock is available for `npm.cmd ci`. No database is needed for the status API. The simulation summary used by the Analytics UI is bundled in the frontend and does not depend on the backend being online.

## 3. Website views

Open these URLs in Chrome after both development servers are running:

| View | URL | Demonstration point |
|---|---|---|
| Overview | `http://127.0.0.1:5173/#home` | Aapurtikar identity, Indian mandi source profile, farmer/centre entry points and research workflow |
| Farmer portal | `http://127.0.0.1:5173/#farmer` | Mobile-first visit-planning preview, crop-scope selection, proposed centre and booking-disabled notice |
| Slot preview | `http://127.0.0.1:5173/#slots` | Illustrative slot layout; capacity is unverified, no slots are published and confirmation is disabled |
| Centre desk | `http://127.0.0.1:5173/#staff` | Administrator workspace preview with no live bookings, check-ins, queue or wait metrics |
| Analytics | `http://127.0.0.1:5173/#analytics` | Separate offline synthetic benchmark and unavailable real-centre operational evidence tabs |

Recommended sequence: Overview → Farmer portal → Slot preview → Centre desk → Analytics (offline simulation, then real operations). Explain that these are academic demonstration screens and are not connected to a participating procurement centre.

## 4. API checks and expected status

With FastAPI running, these read-only routes should return HTTP 200 and the status described:

| Request | Expected response content |
|---|---|
| `GET http://127.0.0.1:8000/api/v1/health` | `status: ok`, bookings disabled, wait estimate disabled, centre unverified |
| `GET http://127.0.0.1:8000/api/v1/status` | Application unverified; staff permissions awaiting authorization |
| `GET http://127.0.0.1:8000/api/v1/centres/proposed` | CMS Kapurthala, New Dana Mandi proposed only and unverified; hours/capacity are null |
| `GET http://127.0.0.1:8000/api/v1/scheduling/readiness` | Offline calculation available; operational configuration awaiting authorization |
| `GET http://127.0.0.1:8000/api/v1/methodology/fcfs` | `mandatory_baseline` and FCFS check-in/tie rules |
| `GET http://127.0.0.1:8000/api/v1/methodology/allocation` | Candidate design requires approval; booking remains disabled |
| `GET http://127.0.0.1:8000/api/v1/metrics/definitions` | Formula definitions; results unavailable without genuine observations |
| `GET http://127.0.0.1:8000/api/v1/evaluation/readiness` | Input unavailable, validation `not_run`, results unavailable |
| `GET http://127.0.0.1:8000/api/v1/bookings/availability` | Booking disabled; no slots returned |
| `POST http://127.0.0.1:8000/api/v1/bookings` | HTTP 409 `booking_disabled`; does not store the request |

Optional PowerShell GET check:

```powershell
$apiBase = 'http://127.0.0.1:8000'
$paths = @(
  '/api/v1/health',
  '/api/v1/status',
  '/api/v1/centres/proposed',
  '/api/v1/scheduling/readiness',
  '/api/v1/methodology/fcfs',
  '/api/v1/methodology/allocation',
  '/api/v1/metrics/definitions',
  '/api/v1/evaluation/readiness',
  '/api/v1/bookings/availability'
)
foreach ($path in $paths) {
  Write-Host "--- $path ---"
  Invoke-RestMethod -Uri ($apiBase + $path) -Method Get
}
```

For the booking check, issue only an empty test body; the expected response is rejection:

```powershell
try {
  Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/v1/bookings' -Method Post -ContentType 'application/json' -Body '{}' -ErrorAction Stop
  throw 'Unexpected response: booking creation must remain disabled.'
} catch {
  if ($_.Exception.Response -and [int]$_.Exception.Response.StatusCode -eq 409) {
    'Expected: HTTP 409 booking_disabled'
  } else {
    throw
  }
}
```

## 5. What works and what is disabled

**Works:** responsive Aapurtikar React navigation; farmer visit-planning controls; slot preview with confirmation disabled; centre operations readiness view; offline simulation benchmark sourced from historical Punjab mandi demand; source profile and policy comparison visualizations; backend health/configuration status reads; backend scheduling/evaluation service tests.

**Intentionally disabled or unavailable:** booking creation, slot publication/reservation, live wait estimates, farmer/staff authentication and permissions, operational queue/event collection, centre activation, PostgreSQL-backed API storage, and real-centre measured analytics. The offline benchmark uses public historical Punjab potato mandi arrivals to create synthetic farmer-level events; those events and outputs are not real farmer or centre records. CMS Kapurthala, New Dana Mandi remains a proposed unverified centre.

## 6. Troubleshooting

- **Python command/import error:** verify `.venv\Scripts\python.exe` exists and that the pinned backend dependencies are installed. Start the backend from the repository root so `--app-dir src/backend` resolves correctly.
- **Frontend dependencies missing:** from `src/frontend`, run `npm.cmd ci` once, then retry the Vite command.
- **Port 5173 is already in use:** this often means Vite is already running. Do not start a second server; refresh `http://127.0.0.1:5173`. If you need to restart it, return to the original Vite terminal and press Ctrl+C, then start it again. Inspect `Get-NetTCPConnection -State Listen -LocalPort 8000,5173` or `netstat -ano -p tcp | Select-String ':8000|:5173'` only if the owning terminal is unknown. Stop only a process you own. If changing the backend port, update `server.proxy['/api'].target` in `src/frontend/vite.config.ts` to that exact localhost port before starting Vite.
- **API appears offline in the browser:** keep the FastAPI terminal running on port 8000. From a second PowerShell window, run `Invoke-RestMethod http://127.0.0.1:8000/api/v1/health`. If that fails, restart FastAPI using the command in Section 1. The frontend still shows the offline simulation tab if the API is unavailable; that does not mean live bookings or wait estimates are active.
- **Windows reports `WinError 10013` or denies localhost HTTP:** stop the connectivity check. Do not disable Firewall/antivirus, broaden the bind address, or expose the server publicly. Ask the device administrator to inspect local socket/port policy.
- **Port reservation check unavailable:** the current shell's `netsh` did not support the excluded TCP port query. No conclusion about excluded/reserved port ranges can be made from this audit.
- **PostgreSQL/Docker errors:** PostgreSQL is not needed by the current application API. Docker Desktop's Linux engine was unavailable during this audit; do not treat a successful app startup as proof of PostgreSQL connectivity.

Stop each development server with Ctrl+C in its own PowerShell terminal.
