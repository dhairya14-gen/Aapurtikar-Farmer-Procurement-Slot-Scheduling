# Live Local Demonstration Guide

This guide demonstrates Aapurtikar on one Windows computer. Both development servers bind to loopback (`127.0.0.1`); do not change the host to `0.0.0.0` or expose either service publicly. PostgreSQL and a `.env` file are not required for the website or status API.

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
npm.cmd ci  # first setup only
npm.cmd run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Leave this terminal open too. The website address is `http://127.0.0.1:5173`. The existing Vite proxy forwards `/api` to `http://127.0.0.1:8000`.

## 3. Recommended classroom demo sequence

Open Chrome and present the screens in this order.

### A. Overview

Open `http://127.0.0.1:5173/#home`.

Explain the purpose of Aapurtikar and the research workflow. The Punjab potato-arrivals benchmark is the initial regional simulation case study; it is not the geographic limit of the application.

### B. Farmer portal — complete the interactive workflow

Open `http://127.0.0.1:5173/#farmer`.

The directory currently contains 76 named records across 20 States/UTs. All 36 States/UTs appear in the selector, but not all have loaded centre/market entries yet. The directory distinguishes e-NAM APMC/mandi listings from government procurement-centre directory and tender references.

Recommended starting selection:
- State: Uttar Pradesh
- District: Siddharth Nagar
- Mandi / procurement centre: Centre-B Pax Bijaura (PCF)
- Commodity: Paddy
- Preferred visit date: choose a date convenient for the demo

Read the source status and caveat shown under the selected listing. Then click **Continue to slot preview**. The state, district, centre, crop and date are held in the app state and carried to the next screen.

If using a different state, choose one with loaded records. When a state has no source-backed records in the current seed, the interface says so; do not claim it has no real procurement centres in the real world.

### C. Slot preview — select a sample window and confirm the demo

Open `http://127.0.0.1:5173/#slots` or continue from the Farmer portal.

Choose one of the three illustrative windows (09:00–10:00, 10:00–11:00, 11:00–12:00), then click **Confirm demo reservation**. A reference beginning `AAP-DEMO-` should appear in the confirmation panel.

These times are hard-coded demonstration values, not published centre inventory. The reservation is held only in local React page-session state. It is not posted to FastAPI, stored in the database, transmitted to an agency, or reserved at a real centre. Refreshing the page clears it.

### D. Centre desk — show the staff-side record

Open `http://127.0.0.1:5173/#staff`.

The local demo reservation created in the previous step should appear with its reference, centre, location, commodity, date and sample window. Explain that this is how a centre staff view could present an appointment record. The page separately labels live farmer check-ins, queue and wait estimates as unavailable.

### E. Analytics — explain the evidence

Open `http://127.0.0.1:5173/#analytics`.

Show **Offline simulation results**, explaining that the benchmark uses historical Punjab potato arrivals and synthetic farmer-level event/service assumptions. Then switch to **Real centre operations** to show the missing operational evidence and readiness gates. Do not describe simulated waiting-time improvements as measured results from a real centre.

## 4. API checks and expected status

With FastAPI running, this read-only health route should return HTTP 200:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health | Format-List
```

Expected safety states:
- `status: ok`
- `booking_status: disabled`
- `booking_enabled: False`
- `wait_estimate_status: disabled`
- `centre_status: unverified`

The API does not create demo reservations. The demo reservation is a frontend-only teaching flow and does not change backend readiness.

The backend booking route must continue to reject real booking requests with HTTP 409 `booking_disabled`. Do not attempt to enable it during a classroom demo.

## 5. What is real, what is simulated, and what is not integrated

**Source-backed directory records:** the seed combines e-NAM state/district/mandi mapping entries, a Haryana purchase-centre directory dated 28 Nov 2024, two Uttar Pradesh official procurement-centre tender references, and one NAFED e-Samridhi portal listing. Their types, source dates and caveats are visible in the farmer portal and documented in [the national directory sourcing notes](india-directory-sourcing.md). The data is a partial directory, not complete national coverage. An e-NAM APMC/mandi record is not automatically an MSP procurement centre.

**Local demonstration:** farmer selections carry forward, sample time windows can be selected, and a local-only demo reservation appears on the centre desk.

**Still unavailable:** real farmer booking, slot publication, centre authorization, live capacity, current centre hours, live wait estimates, operational queue/check-ins, authentication and database persistence. Do not claim that a centre is accepting bookings because it appears in the directory.

## 6. Troubleshooting

- **Python command/import error:** verify `.venv\Scripts\python.exe` exists, install backend dependencies, and start from the repository root.
- **Frontend dependencies missing:** from `src/frontend`, run `npm.cmd ci`, then retry Vite.
- **Port 5173 already in use:** this often means Vite is already running. Refresh `http://127.0.0.1:5173` rather than starting a second instance. If restarting, press Ctrl+C in the original Vite terminal first.
- **API appears offline:** keep FastAPI running on port 8000 and test `Invoke-RestMethod http://127.0.0.1:8000/api/v1/health` from a second PowerShell window.
- **Windows reports `WinError 10013`:** do not disable firewall/antivirus, broaden the bind address or expose the server publicly. Ask the device administrator to inspect local socket/port policy.
- **PostgreSQL/Docker errors:** PostgreSQL is not required for the current demonstration. The API health response reports `database_status: not_checked`.

Stop each development server with Ctrl+C in its own PowerShell terminal.
