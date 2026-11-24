# CA-1 Requirements and Evaluation Plan

## Official allocation

- Course: CSE276
- Section: K3P25LH
- Group: G24
- Project: Farmer Procurement Slot Scheduling and Wait Time Reduction
- SIH Problem ID: SIH26032
- Location: Kapurthala district, Punjab, India
- Proposed centre: CMS Kapurthala, New Dana Mandi. Proposed academic candidate only; crop eligibility, capacity, operating hours, exact location and participation are unverified.

## Mandatory objectives

1. Build a scheduling system that allocates arrival slots and publishes expected wait, reducing total queueing.
2. Produce a slot allocation policy compared against unmanaged arrival on total wait.
3. Report mean and worst-case wait, throughput, fairness spread.

**Mandatory baseline:** unmanaged first-come-first-served (FCFS).
**Required deliverable:** slot booking interface with live wait estimate.

This exact allocation wording must be preserved. The booking interface and live estimate are not implemented or enabled. No centre-level improvement has been measured. A separate, offline Indian demand-profile benchmark is presented in the website analytics; it is a synthetic scenario study, not observed procurement performance.

## CA-1 report and presentation requirements

The report chapter sequence, 12-20 page range (Chapter 1 through References), A4 / Times New Roman 12 pt / 1.5 spacing / 1-inch margins, IEEE numbered referencing, 8-10 slides and approximately 8-minute presentation are mapped in `report/university_compliance_checklist.md`. Include the AI-use declaration, individual contributions and signatures. The instructor's exact declaration and signature requirements remain to be confirmed.

## Evaluation definitions and protocol

The complete operational policy, event definitions, metric formulas, inclusion rules, fair-comparison design and unresolved authorization questions are specified in [`scheduling_methodology.md`](scheduling_methodology.md). Key estimands are:

- Observed visit wait: `W_i = service_start_at_i - check_in_at_i`, in minutes.
- Total wait: `sum(W_i)` over valid served visits in a declared cohort/window, in person-minutes.
- Mean wait: total wait divided by valid served visits, in minutes per visit.
- Worst-case wait: maximum observed visit wait in that scope, in minutes; sample maximum only.
- Throughput: completed service episodes divided by scheduled open operating hours, in completed episodes/hour.
- Fairness spread: maximum minus minimum subgroup mean wait, in minutes, over predeclared and authorized groups.

Valid events, censored records, closures, cancellations, no-shows, and comparison rules must follow the methodology document. Predicted wait is an estimate and is never a substitute for observed wait.

## Objective-to-artifact mapping

The mappings distinguish implemented calculation code from operational readiness: the calculation and input-driven evaluation code exists, but no genuine project evaluation has been run and booking/live estimates remain disabled.

| Objective | Methodology | Code module | Isolated tests | Report chapters | Readiness |
|---|---|---|---|---|---|
| 1. Allocate slots and publish expected wait, reducing total queueing. | Slot policy, verified configuration gates, live estimate method; `scheduling_methodology.md` sections 3, 4, 8 | Implemented candidate-only `services/allocation.py`; live estimate and booking API remain unimplemented | `tests/backend/test_scheduling_services.py`; no live-estimate test because no estimator exists | 5 Methodology; 6 Implementation; 7 Results and Evaluation | Pure slot eligibility/selection checks exist. No reservation is created. Operational allocation/estimate requires authorized centre config and genuine service data. |
| 2. Produce a slot allocation policy compared against unmanaged arrival on total wait. | Precise unmanaged FCFS; equivalent cohort/window comparison; `scheduling_methodology.md` sections 2, 7, 9 | Implemented `services/baseline.py`, `services/metrics.py`, `app/evaluation/pipeline.py` | `tests/backend/test_scheduling_services.py`, `test_evaluation_pipeline.py` | 5 Methodology; 7 Results and Evaluation | Pipeline is ready for reviewed genuine observed-arm data. No project evaluation has been run. |
| 3. Report mean and worst-case wait, throughput, fairness spread. | Formal definitions, denominators, record rules; `scheduling_methodology.md` sections 5-6, 9 | Implemented `services/validation.py`, `waiting.py`, `throughput.py`, `fairness.py`, `metrics.py` | `tests/backend/test_scheduling_services.py`, `test_evaluation_pipeline.py` | 5 Methodology; 7 Results and Evaluation; 8 Limitations and Ethical Considerations | Pure metrics return unavailable when required inputs are missing/invalid; reportable results require real valid data and authorized fairness groups. |

## Current readiness and integrity

- The existing frontend/API foundation remains informational; bookings are disabled and centre status remains unverified.
- CMS Kapurthala, New Dana Mandi is not a verified operating configuration.
- There are no genuine centre-level event observations. Real-centre mean/worst wait, throughput, fairness and impact remain unavailable.
- A separate offline benchmark uses public historical Punjab potato mandi arrivals as aggregate demand-volume inputs and synthetically generates farmer-level arrivals/service durations for a scenario replay. Its results are scenario outputs only, not operational records or measured field effects.
- Public aggregate arrivals/quantities cannot establish an individual farmer's check-in, service-start, wait, or completed-service throughput.
- Do not load synthetic benchmark events or isolated software fixtures into the observed-data evaluation pipeline, or report them as actual farmer records.

## Dependencies and approvals before operational work

Required from an authorized centre/instructor: centre identity and participation; crop and season eligibility; operating calendar and closures; capacity and its unit; service resources/routing; service-duration definitions/data; slot granularity and allocation rules; late-arrival/cancellation/no-show policies; priority rules; timestamp/event collection permission; privacy/legal basis, access/retention, and approved fairness grouping. See the unresolved decision register in `scheduling_methodology.md`.
