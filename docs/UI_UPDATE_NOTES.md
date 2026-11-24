# Aapurtikar UI update — 24 November 2026

## Updated interface

The frontend now uses Aapurtikar branding and the approved farmer/centre design direction. It has five responsive screens:

1. Overview — project explanation, Punjab mandi source profile and research workflow.
2. Farmer portal — mobile-first visit-planning preview, project crop-scope selector and language toggle.
3. Slot preview — illustrates appointment options but does not publish slots or reserve capacity.
4. Centre desk — administrator/centre workspace preview with live bookings, queue, check-ins and mean wait intentionally unavailable.
5. Analytics — separate offline simulation results from real-centre operational evidence.

## Research-data integration

The Analytics page reads aggregate values embedded in `src/frontend/src/researchData.ts`. The source facts and benchmark transformations are documented in `india_mandi_benchmark_provenance.md`; aggregate CSV exports are retained in `data/benchmark/`. The raw cleaned source CSV and synthetic event-level trace are intentionally not included due to the upstream source repository's unclear redistribution licence.

The public source profile is 1,410 Punjab potato market-day records across 81 markets and 25,582.56 tonnes for November 2021. The UI shows top-five market totals and the 30-replication policy summary. Farmer-level event times, service durations and queue waits are synthetic simulation outputs. They are not actual farmer records or observed centre performance.

## Safety and scope

- Do not enable booking, slot publication, booking confirmation or live wait estimates.
- CMS Kapurthala, New Dana Mandi remains a proposed, unverified candidate.
- The API status remains separate from the static research benchmark; the Analytics simulation tab stays viewable if the backend is offline.
- The operational analytics tab continues to report that genuine centre observations are unavailable.
- Refresh the report and presentation screenshots only after the local app is tested and approved.

## Validation performed in the build workspace

- Backend tests: 26 passed.
- TypeScript/JSX syntax transpilation: no diagnostics.
- Strict TypeScript check with temporary React declaration shims: passed. (The package dependencies were not installed in this build workspace, so a full Vite production build was not run here.)
- CSS parser validation: passed.

On the Windows development PC, use the existing `node_modules` and run `npm.cmd run typecheck` and `npm.cmd run build` from `src/frontend` after applying the update.
