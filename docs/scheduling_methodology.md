# Scheduling Methodology and Evaluation Design

**Project:** Farmer Procurement Slot Scheduling and Wait Time Reduction
**Allocation:** CSE276 / K3P25LH / G24 / SIH26032
**Scope:** Method and evaluation design only. This document does not configure a centre, collect operational records, enable bookings, or present results.

## 1. Operating boundary and notation

CMS Kapurthala, New Dana Mandi is a proposed academic candidate. Its participation, crop/season eligibility, authorized operating hours, capacity, service resources and service durations have not been verified. All such configuration is `UNCONFIGURED`; no numeric or inferred defaults may be used. A configuration must identify its authorizing centre representative, source, effective period, version and approval.

An **episode** is one farmer procurement visit/service episode as defined by the centre-approved protocol. Timestamps are event times, stored with timezone/offset and displayed in Asia/Kolkata local time. Preserve the original event and append corrections with actor, correction time and reason; do not silently overwrite source evidence. A server-recorded monotonic event sequence may resolve same-timestamp ties. Client clocks alone must not establish ordering.

## 2. Mandatory unmanaged FCFS baseline

The baseline is unmanaged arrival with no appointment/slot allocation. Eligible arrivals join the relevant service stream in actual recorded check-in order. Within a stream/resource, the next eligible episode is served in that order. Equal check-in timestamps are resolved by the server-assigned event sequence, then a documented stable episode key if needed. The tie rule is for determinism, not a priority policy.

Use the centre's authorized crop eligibility, operational safety rules and resource routing in both conditions. Do not assume a single queue or server. If the centre has an existing priority rule or does not operate FCFS, the centre and instructor must approve how the required unmanaged FCFS baseline can be observed or evaluated; do not silently override real operations. Record deviations and the baseline policy version. Baseline arrivals must be genuine check-ins, not reconstructed from aggregate market arrivals.

## 3. Proposed slot allocation policy

### 3.1 Eligibility and configuration gates

Before producing bookable slots, require an authorized, effective-dated configuration specifying: centre and participation; crop and season eligibility; operating calendar, open intervals and closures; staffed service streams/resources and routing; capacity and its unit; service/eligibility constraints; timezone; slot duration/granularity; booking horizon; and any operational allocation, priority, cancellation and late-arrival rules. The centre must define whether capacity counts visits, lots, vehicles, quantity, workload, or another unit. If unlike loads require different service times, their capacity conversion must be authorized and supported; the application must not invent it.

Any missing, expired, contradictory or unapproved required field keeps booking unavailable. Centre status remains unverified until reviewed. No slots should be shown as bookable for the proposed CMS centre in the current state.

### 3.2 Allocation flow (proposal for approval)

1. Construct candidate slots only inside the authorized operating calendar and within the configured crop/season scope.
2. A farmer or authorized staff member selects a slot. Both channels use the same eligibility and capacity validation.
3. Reserve capacity atomically in the database so concurrent requests cannot exceed the authorized cap. Persist configuration and policy versions with each reservation.
4. Where a policy offers multiple feasible slots, rank them by projected workload only if the workload measure, inputs and tie rules are approved and validated. Otherwise present feasible slots without a claimed optimization. Deterministic tie handling may prefer earlier slot and then server request sequence; it must not act as undisclosed priority.
5. Within an assigned slot, retain check-in order (FCFS) unless the centre authorizes another rule. Monitor actual arrivals and service state; slot allocation does not guarantee immediate service.
6. Reconcile no-shows, cancellations, late arrivals and remaining capacity under the authorized rules. Do not automatically release/reassign reservations until a release rule and timing are approved.

This is a candidate design, not an operational policy. Allocation objective weights, overbooking, quotas, walk-in treatment, priority access and capacity release are unresolved and require explicit approval. Do not promise that this design reduces total queueing before evaluation.

## 4. Inputs required

| Input | Required meaning / provenance | State |
|---|---|---|
| Centre, participation, crop and season | Authorized eligible centre/service scope and effective dates | Unverified; required before activation |
| Operating calendar | Local timezone, dates/open intervals, scheduled breaks and authorized closure rules | Unknown; no hours assumed |
| Capacity | Cap and exact unit per slot/stream/period, method of counting, effective dates | Unknown; no cap assumed |
| Service resources | Number/type of staffed channels, routing eligibility, concurrency and outages | Unknown; no single-server assumption |
| Service duration | Valid service-start/completion definitions and observed durations by relevant crop/season/load/resource strata | No observations; no duration default |
| Demand | Booking requests, slot choice, actual check-in, walk-ins and eligibility in a consented/authorized scope | No operational data |
| Slot policy | Granularity, booking horizon, allocation rule, tie-breaks, quotas, release, walk-ins | Requires centre/instructor approval |
| Event clock | Server timestamp source, timezone handling, sequence and correction audit | Must be implemented/validated |
| Fairness groups | Operationally justified, approved, privacy-reviewed grouping variable(s) | Not selected; no sensitive collection assumed |

## 5. Event model and metric definitions

Minimum event names: `booking_created_at` (if booked), `check_in_at`, `service_start_at`, `service_complete_at`, `cancelled_at` and `no_show_declared_at`, plus slot start/end where applicable. Store episode ID, centre/configuration and policy version, crop/season scope, event actor/source, event timestamp, server receipt timestamp, sequence, and correction/audit details. Collect only approved fields; avoid farmer names/phone numbers in evaluation exports where pseudonymous episode identifiers suffice.

Let `W_i = (service_start_at_i - check_in_at_i)` converted to minutes. Require same visit episode, valid provenance, timestamps in chronological order and `W_i >= 0`. Do not impute missing times or silently repair invalid order.

Define `V_W` as deduplicated, correction-resolved genuine episodes in the declared centre, crop/season, policy and observation cohort/window that have valid check-in and service-start timestamps. Publish `N_W = |V_W|` and exclusions/missingness with every wait metric. `service_complete_at` is not required for a valid wait if service genuinely started.

| Metric | Exact definition | Units and denominator | Record rules |
|---|---|---|---|
| Total observed wait | `TW = sum(W_i for i in V_W)` | Person-minutes (one episode's minutes summed once) | Valid check-in and service-start. State cohort/window, policy and `N_W`. Follow each cohort sufficiently to capture delayed starts; report still-waiting episodes separately as right-censored at extraction rather than treating as zero or dropping silently. |
| Mean observed wait | `MW = TW / N_W` | Minutes per valid served episode; denominator `N_W` | Defined only when `N_W > 0`. Same valid set as total wait. |
| Worst-case observed wait | `WW = max(i in V_W) W_i` | Minutes; sample maximum over `N_W` | Defined only when `N_W > 0`; label as observed sample maximum, not a guaranteed bound. |
| Throughput | `TP = N_C / H_open` | Completed service episodes per scheduled open operating hour | `N_C` counts unique episodes with valid check-in, service-start and service-complete in order. `H_open` is authorized scheduled open minutes in the predeclared evaluation scope divided by 60. Predeclare treatment of authorized closures, partial days and staffing downtime; never selectively remove downtime after seeing outcomes. If `H_open <= 0`, undefined. Report closures/downtime separately. |
| Fairness spread | `FS = max_g(mean(W_i for i in V_W with group_i=g)) - min_g(mean(W_i for i in V_W with group_i=g))` | Minutes between largest and smallest subgroup means | Group field and categories must be predeclared, operationally justified, authorized and privacy-reviewed. Use the same wait validity rules; disclose each group count and uncertainty. Do not collect sensitive characteristics solely to populate this metric without approval. If no approved groups, fewer than two interpretable groups, or inadequate data, mark unavailable with reason; do not fabricate groups or impose an unapproved sample threshold. |

For a total-wait comparison, also report the observation window, eligible demand/arrival counts, cohort follow-up, `N_W`, censored/unresolved counts, invalid/missing event counts and configuration/policy versions. Total wait only among served visits can be biased if many arrivals remain unserved at cutoff; therefore use a prespecified cohort and sufficient follow-up, and disclose censored visits. If censoring differs materially across arms, total served wait alone is not a complete comparison.

## 6. Special event treatment (authorization required)

- **Late arrival:** Preserve booked slot and actual check-in. Whether a late arrival retains the slot, joins FCFS, loses reservation, or is rescheduled is an operational policy requiring centre authorization. Measure wait from actual check-in, not booked time.
- **Cancellation:** Record event/time and source. A cancellation before check-in has no observed on-site wait; report booking cancellation counts/rates separately with declared denominator. A post-check-in cancellation or departure before service is not a served wait; retain as unresolved/left-before-service and define follow-up handling with the centre. Do not recode as zero wait.
- **No-show:** Mark only after an authorized grace/cutoff and verified status. Before that, status is pending, not no-show. No-show has no on-site wait; report separately from served-visit metrics. Reservation release and capacity reuse require an approved rule.
- **Incomplete service:** A valid check-in and service-start can contribute to wait even if completion is missing; it cannot contribute to throughput. A checked-in episode with no service start by extraction is right-censored and excluded from `V_W` pending follow-up, but must be counted and reported as censored, not discarded. If service start exists but timestamps are invalid, quarantine and report the exclusion.
- **Corrections, duplicate/missing events:** Retain source evidence and audited correction; resolve duplicates with a documented deterministic rule. Unresolved, out-of-order or unverifiable records are excluded from metric numerators/denominators and reported by reason. Do not impute.
- **Walk-ins and policy violations:** Inclusion in policy cohorts, queue order, and slot capacity must be decided before collection. Record protocol deviations; do not retrospectively relabel an episode to improve results.

All grace periods, cutoffs, release timing, cancellation effects, late-arrival handling, walk-in treatment and cohort closure are unconfigured operational decisions.

## 7. Fair comparison design

### Preferred design

Subject to centre and instructor approval, use a cluster-randomized switchback over comparable operating sessions or days, assigning whole sessions to unmanaged FCFS or slot policy to limit spillover between farmers in the same queue. Block/stratify random assignment by relevant authorized factors such as crop/season, weekday or session type, and comparable planned staffing/resources. Keep eligibility, operating period definitions, service rules, timestamp quality and follow-up identical. Preserve access and never withhold required services for research.

Before collection, freeze the protocol: unit of assignment, eligible demand, outcome cohort, follow-up window, treatment of walk-ins/cancellations/no-shows/closures, primary total-wait comparison, secondary metrics, fairness groups, missingness rules, statistical uncertainty method and stopping/adequacy criteria. Use only authorized operational configuration and service assumptions; record deviations. Report both arm-specific totals and paired/block differences with uncertainty appropriate to the assignment unit. Power/precision and minimum sample adequacy should be determined from authorized pilot data and an agreed criterion, not an invented threshold.

### If randomization is not permitted

Use matched comparable real operating periods with the same centre, crop/season scope, operating-window definition, capacity/resource configuration and documented demand characteristics as far as possible. Report unmatched differences and confounders (for example, season, workload, staffing or weather if legitimately available). Treat results as descriptive association; do not claim causal reduction. A before/after comparison alone does not control these factors.

In either design, compare total wait for equivalent demand cohorts and equivalent follow-up, and report throughput and all objective metrics. Equalize or prespecify adjustment for demand differences; never scale or exclude observations opportunistically after seeing results. Because total wait increases with the number arriving, provide eligible arrival/request counts and clarify whether the estimand is the total for the observed cohort or a demand-standardized comparison. No adjustment model can be selected without data and protocol approval.

## 8. Expected-wait estimate

The UI estimate targets expected time from actual check-in to service start for a stated slot/queue state:

`E[service_start_at - check_in_at | current verified queue, scheduled arrivals, authorized resources/configuration, and valid historical service-duration evidence]`.

For a genuinely single-server stream with validated assumptions, a candidate calculation is residual duration of the job currently in service plus expected durations of eligible jobs ahead. For multiple resources, routing, parallel service, variable eligibility or changing availability, use an explicitly validated queue model or event replay; do not divide work by server count as an unverified shortcut. Estimate inputs, model/version, as-of time, scope, and uncertainty/coverage must be visible. Clearly label it “estimate”; distinguish forecast from actual wait.

Minimum genuine data to estimate: reliable service-start and service-completion timestamps linked to the same episode (duration); actual check-in time; crop/season and relevant load/work type only where authorized and needed; resource/service-stream identity and routing; queue position/state or all arrivals/service states needed to reconstruct it; authorized operating calendar, active capacity/resources, breaks/closures; and policy/configuration version. Include data provenance and enough representative observations to validate by relevant strata. If evidence does not meet a pre-registered accuracy/precision and coverage criterion, return “estimate unavailable” rather than a numeric display. That release criterion must be defined and reviewed before publication; no threshold is set here because none is verified.

## 9. Reproducible evaluation pipeline

1. **Protocol lock:** Record authorization, estimands, cohort, arms, windows, metric definitions, exclusions, subgroup definitions, uncertainty and adequacy criteria before access to outcomes.
2. **Source intake:** Register source/permission, collection method, timezone, configuration and policy versions. Preserve genuine raw inputs as access-controlled, immutable source artifacts where permitted; record hashes and schema version. Never add generated operational rows.
3. **Validation:** Validate required fields, episode identity, timezone, sequence, event order, uniqueness, authorization scope and configuration effective dates. Produce an audit count by valid, censored, duplicate, missing and invalid reason; quarantine questionable records.
4. **Derivation:** Derive `V_W`, `V_C`, scheduled open hours and censoring from approved rules. Keep cleaning/derived outputs reproducible and traceable to source versions.
5. **Metrics:** Compute metrics separately by policy, period, crop/season and approved strata. Export numerator, denominator, units, cohort counts, missingness and config/policy versions with every result.
6. **Comparison:** Apply the predeclared paired/block or approved matched-period analysis. Report uncertainty and deviations; publish no causal language where design does not support it.
7. **Reproduction:** Pin runtime/dependency versions and analysis code revision; store a run manifest (input hashes, protocol version, command, timestamp, environment, outputs). A reviewer with authorized data can rerun the pipeline. No data/results currently exist.

Offline replay can evaluate algorithm behavior against historical inputs where permitted, but must be explicitly labeled counterfactual replay/simulation, state assumptions, and remain distinct from operational evidence. The separate Punjab potato benchmark described in `docs/india_mandi_benchmark_provenance.md` demonstrates this distinction. Software test fixtures must stay isolated under tests and never be reported as farmer or centre records.

## 10. Objective, implementation and report mapping

| Objective | Method sections | Implementation/test mapping | CA-1 report |
|---|---|---|---|
| 1. Build a scheduling system that allocates arrival slots and publishes expected wait, reducing total queueing. | 3, 4, 8 | Candidate-only slot selection is implemented in `src/backend/app/services/allocation.py`; live-wait estimator and booking route are not implemented. Isolated tests: `tests/backend/test_scheduling_services.py`. | Chapter 5 Methodology; Chapter 6 Implementation; Chapter 7 Results and Evaluation |
| 2. Produce a slot allocation policy compared against unmanaged arrival on total wait. | 2, 7, 9 | FCFS ordering in `src/backend/app/services/baseline.py`; observed-arm evaluation in `src/backend/app/evaluation/pipeline.py`; tests in `tests/backend/test_scheduling_services.py` and `test_evaluation_pipeline.py`. | Chapter 5 Methodology; Chapter 7 Results and Evaluation |
| 3. Report mean and worst-case wait, throughput, fairness spread. | 5, 6, 9 | Implemented in `src/backend/app/services/validation.py`, `waiting.py`, `throughput.py`, `fairness.py` and aggregated by `metrics.py`; isolated service/pipeline tests. | Chapter 5 Methodology; Chapter 7 Results and Evaluation; Chapter 8 Limitations and Ethical Considerations |

The pure modules exist but are not connected to FastAPI routes or database writes. Slot selection is candidate-only and never reserves capacity. The operational evaluation pipeline accepts only authorized observed records for both arms; it does not generate counterfactual or synthetic operational results. Separately, the project includes an India-grounded synthetic queue benchmark based on aggregate Punjab mandi arrivals. That scenario benchmark is explicitly labelled simulation, is not part of the observed-data evaluation pipeline, and does not represent a real centre or actual farmer records. Test fixtures remain isolated under tests and are never used as research outputs.

## 11. Readiness and unresolved decisions

### Can be done now

- Preserve this protocol and exact allocated objectives/baseline.
- Pure, configuration-explicit metric/validation and candidate slot selection functions are implemented and covered by isolated tests.
- The evaluation CLI and schema/settings contract are implemented; it emits no project results until the operator supplies authorized genuine data and approved settings.
- Non-operational API boundaries and disabled-state behavior remain in place.

### Requires verified authorization/configuration or genuine data

- Bookable slot generation, reservation, capacity enforcement, live estimate, crop/season availability, staffed-resource model, actual evaluation and any impact claim.
- Service-duration model calibration/validation, fairness spread, operational throughput, and baseline/policy comparison.
- Collection of personal or operational data, even pseudonymous, until permission, lawful/approved basis, notice/consent as applicable, access, retention and deletion are approved.

### Decisions requiring centre / instructor / student confirmation

1. Is CMS Kapurthala, New Dana Mandi participating, and who can authorize its configuration?
2. Which crops/seasons are eligible, and for which dates?
3. What are opening intervals, breaks, holidays and closure accounting rules?
4. What does capacity count, per what interval/resource, and how is it determined?
5. What service channels/resources exist; how are episodes routed and prioritized?
6. What is the authoritative service-start and completion event and timestamp source?
7. Which slot duration, booking horizon, allocation/tie rules, quotas, walk-in policy, overbooking policy and capacity release rule are approved?
8. What late grace/cutoff, cancellation, post-check-in departure and no-show declaration rules apply?
9. If actual operations are not unmanaged FCFS, how will the mandatory baseline be obtained without disrupting service?
10. What permissions, privacy notice/consent or other approved authority, identifiers, access controls, retention and deletion apply?
11. Which fairness groups are lawful, justified and collectable; what uncertainty/adequacy standard is acceptable?
12. Which design is feasible (randomized switchback or matched periods), and what precision/validation and stopping criteria will be approved?
13. Which deviations, closures and service outages remain in the primary analysis denominator?

Until these questions are resolved, booking remains disabled and all operational values remain unconfigured.
