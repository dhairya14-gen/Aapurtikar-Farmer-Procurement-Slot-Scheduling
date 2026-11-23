# Aapurtikar — Farmer Procurement Slot Scheduling and Wait Time Reduction

**SIH26032 | CSE276 – Artificial Intelligence Foundations | Group G24**

This repository contains the supplied Aapurtikar source bundle, the CA-1 report (editable DOCX and PDF), and the project presentation.

## Repository contents

- `project/` — supplied application source (FastAPI backend and static HTML/CSS/JavaScript farmer and worker portals).
- `docs/` — CA-1 report in DOCX and PDF formats.
- `presentation/` — project presentation.

## Source-bundle note

The supplied application archive contains a legacy FastAPI/SQLite backend and static HTML/CSS/JavaScript portals. The CA-1 report also discusses a separate React/TypeScript and FastAPI architecture from an earlier project audit and records that these are not yet reconciled as the same implementation. Do not assume this source bundle implements every architecture or feature described in the report.

## Local setup

Backend dependencies are listed in `project/backend/requirements.txt`. The original run instructions are in `project/README.md`. Create a fresh local virtual environment before installing dependencies; do not commit it.

## Data and operational status

The upload excludes the local SQLite database and bundled Python virtual environment. The report distinguishes deterministic synthetic simulation results from genuine operational observations and documents limitations around live deployment, verified procurement-centre partnership, and booking activation. The worker portal's bundled hard-coded demo identities have been removed from the public source version.

## Team

- Ananmay Saroch — Registration 12518907
- Dhairya Jaiswal — Registration 12514042

Instructor: Piyush Sharma
