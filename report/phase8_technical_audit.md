# Phase 8 — Technical Audit

**Project:** Farmer Procurement Slot Scheduling and Wait Time Reduction
**Problem:** SIH26032
**Audit date:** 2026-11-15

## Scope and result

The backend tests, scheduling/evaluation tests, frontend type check and production build passed. The Alembic migration was applied to a temporary SQLite database and the expected schema was inspected. Dependency health and local configuration were checked.

Live HTTP/browser integration and PostgreSQL runtime were **not verified**. Local HTTP probes failed with Windows `WinError 10013`, the in-app browser could not reach localhost, and the Docker Desktop Linux engine was not available. No security setting was changed to work around these limits. The current Phase 8B pass used no Computer Use/browser automation.

## Checks performed

| Check | Command or method | Actual result |
|---|---|---|
| Complete backend suite | `.\.venv\Scripts\python.exe -m pytest -q` | `26 passed in 0.97s`, exit 0 |
| Scheduling and evaluation tests | `.\.venv\Scripts\python.exe -m pytest tests/backend/test_scheduling_services.py tests/backend/test_evaluation_pipeline.py -q` | `15 passed in 0.11s`, exit 0; these tests are included in the complete suite count |
| Frontend TypeScript | `npm.cmd run typecheck` from `src/frontend` | Exit 0; no TypeScript diagnostics |
| Frontend production build | `npm.cmd run build` from `src/frontend` | Exit 0; Vite transformed 30 modules and built the bundle |
| Python dependency health | `.\.venv\Scripts\python.exe -m pip check` | `No broken requirements found.` |
| SQLAlchemy relationship mapping | `configure_mappers()` after importing models | `SQLAlchemy mapper configuration passed` |
| SQLite Alembic migration | Set `DATABASE_URL` to a unique temporary SQLite file, then run `python -m alembic -c src/backend/alembic.ini upgrade head` | Exit 0. Alembic applied revision `bddb0878f183`; all 12 expected tables, including `alembic_version`, were present. The temporary database file was removed. |
| SQLite constraints | Included in complete backend suite using transient in-memory SQLite | Passed as part of the 26 tests; tests cover unauthorized verification and nonpositive slot capacity |
| PostgreSQL availability | `docker info`; check for `psql` and a PostgreSQL process | Docker CLI/Compose are installed, but Docker could not connect to `npipe:////./pipe/dockerDesktopLinuxEngine` because the engine pipe was missing. `psql` and a PostgreSQL process were not found. No PostgreSQL runtime or migration check was claimed. |

The significant outputs were:

```text
..........................                                               [100%]
26 passed in 0.97s
```

```text
...............                                                          [100%]
15 passed in 0.11s
```

```text
No broken requirements found.
```

```text
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Running upgrade  -> bddb0878f183, initial schema foundation
Expected schema tables present: True
Table count: 12
migration_exit=0
```

## Local HTTP startup investigation

The documented backend command is:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir src/backend --host 127.0.0.1 --port 8000 --reload
```

Vite is started with:

```powershell
Set-Location src/frontend
npm.cmd run dev -- --host 127.0.0.1
```

Vite's `/api` proxy target is `http://127.0.0.1:8000` in `src/frontend/vite.config.ts`.

A bounded process probe observed the Uvicorn process still running after launch and Vite printed its ready message (`VITE v7.2.2`, local URL `http://127.0.0.1:5178/` for the alternate-port probe). Requests from the audit command process to the API health route, Vite home page and Vite `/api` proxy each failed with:

```text
urllib.error.URLError: <urlopen error [WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions>
```

The earlier in-app browser also reported `net::ERR_CONNECTION_TIMED_OUT` for localhost. Therefore server process launch was observed, but HTTP response delivery, the Vite-to-FastAPI proxy, loading/error states in a running browser, and all five rendered views remain unverified. The handler/API contracts are covered by in-process pytest tests; those are not live HTTP tests.

`Get-NetTCPConnection` and `netstat -ano -p tcp` showed no current listener on ports 8000 or 5173 when checked. An earlier Vite launch reported port 5173 in use and selected 5174; a later strict-port launch reported ready on 5173. The transient port owner was not identified. The Windows `netsh` command in this environment returned `The following command was not found: int ipv4 show excludedportrange protocol=tcp.` Consequently, whether either port is excluded/reserved could not be established. No firewall, antivirus or network setting was changed.

## Safety, secrets and data checks

- The booking handler is a fixed rejection response with status 409 and code `booking_disabled`; the handler contract test verifies this. A live HTTP `POST` could not be verified because of the socket restriction. The handler has no database/session dependency and does not persist the submitted request.
- Booking availability is disabled, wait estimates are disabled, and the proposed CMS Kapurthala, New Dana Mandi centre remains unverified. Existing tests assert these states.
- `data/raw/`, `data/processed/`, and `results/` contained only their `.gitkeep` placeholders. No operational data or result artifacts were found. Test fixtures are confined to test files and temporary test storage.
- No `.env` file or `DATABASE_URL` was present. `.env.example` contains a development placeholder. `.gitignore` ignores `.env` and other local `.env.*` files while allowing the example template.
- `git ls-files .env .env.*` returned no tracked environment files. Git status showed workspace files as untracked; no files were staged, committed, or pushed during this audit.
- The UI source has a viewport meta tag, semantic navigation/main landmarks, accessible labels/status roles, and responsive CSS breakpoints at 900, 650 and 380 pixels. These are source inspections only; desktop/mobile visual layout, keyboard use and screen-reader behavior were not browser-tested.
- No separate frontend unit or browser automation test suite is configured.

## Bugs found and fixed

- The README referred to `$env:LOCALAPPDATA\Python\bin\python.exe`; that path did not exist in the audit environment. The Windows setup instructions now use the Python 3.14 launcher with a full-path fallback.
- The README presented PostgreSQL startup as part of the normal application setup even though the API does not use PostgreSQL. The instructions now make database startup optional and state that the API has no database runtime integration.
- The README now documents the separate terminal startup commands, explicit `DATABASE_URL` requirement for migrations, test commands, and the HTTP/browser/PostgreSQL verification limitation.

No application code bug was confirmed or changed as part of this audit.

## Outstanding work

1. Resolve the Windows localhost socket restriction through the machine administrator or a permitted local development environment. Do not disable firewall/antivirus protections or expose the server publicly.
2. Once local HTTP is available, verify FastAPI startup, each endpoint over HTTP, the frontend proxy, the 409 booking response, and the five desktop/mobile views with normal browser QA.
3. Start Docker Desktop's Linux engine and run PostgreSQL migrations against a disposable local database if PostgreSQL compatibility is required. The SQLite migration result does not prove PostgreSQL runtime compatibility.
4. Add a frontend test/browser automation suite if the project later adopts a test runner; no new package was installed for this audit.
5. Continue to require verified centre configuration, approved operating policies and genuine authorized observations before enabling bookings, live estimates or reporting measured metrics.
