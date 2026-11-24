# Evaluation Dataset and Pipeline Input Contract

This document describes inputs for `app.evaluation`. It contains no dataset or example operational records. Do not run the evaluation on test fixtures or unapproved/personal data. A CSV is eligible only after the centre/university approvals in `scheduling_methodology.md` have been recorded.

## CSV structure

One row represents one visit episode in one observed policy arm. The CSV must contain every column below. Empty event timestamp cells mean the event was not recorded/has not occurred; they are not zero or imputed values. Timestamps that are present must be ISO-8601 and include a timezone offset. Use pseudonymous episode references; do not include farmer names, phone numbers, or identifiers unnecessary for evaluation.

| Column | Required value/rule |
|---|---|
| `episode_id` | Stable pseudonymous episode key; unique for one episode across both arms |
| `centre_id` | Authorized evaluation centre key; must match settings |
| `crop_code`, `season_code` | Authorized crop/season scope; both match settings |
| `policy_arm` | Exactly `fcfs` or `slot_policy` |
| `policy_version` | Policy/configured baseline version; must match the value in settings for that arm |
| `service_stream_id` | Authorized stream/resource identifier; used by FCFS ordering and matched demand checks |
| `centre_configuration_reference` | Version/source reference for the effective centre configuration |
| `service_assumptions_reference` | Service-duration/resource assumptions reference; must match settings in both arms |
| `operating_period_id` | Actual authorized operating session identifier for provenance |
| `comparison_block_id` | Approved matched/switchback block key; used to require equal eligible demand per block and stream |
| `check_in_at` | Actual check-in event time; required to enter the on-site wait cohort |
| `service_start_at` | Actual service-start event time; required for observed wait |
| `service_complete_at` | Actual completion event time; required for throughput |
| `cancelled_at` | Actual cancellation/departure event time, if applicable |
| `no_show_declared_at` | Actual no-show declaration time, if applicable |
| `no_show_confirmed` | `true` only when an approved cutoff/status verification supports the declaration; otherwise `false` |
| `check_in_sequence` | Server event sequence for check-in ties; non-negative integer or blank if unavailable (episode key is deterministic fallback) |
| `fairness_group` | Approved grouping value or blank; used only when grouping is authorized in settings |
| `deduplication_resolved` | `true` only after duplicate resolution is documented |
| `correction_resolved` | `true` only after timestamp correction review is complete |
| `provenance_valid` | `true` only when source/permission/provenance is verified |
| `eligible` | `true` only under the frozen authorized evaluation scope |

Rows with malformed timestamps, unresolved corrections/duplicates, invalid provenance, invalid event order, incomplete outcomes, or records outside the declared scope are excluded by reason. The pipeline does not impute missing timestamps. A check-in without service start is right-censored at extraction; a valid service start without completion may contribute to wait but not throughput.

## Settings JSON contract

The `--settings` JSON file must supply all of these keys; no operational value is defaulted:

| Key | Meaning |
|---|---|
| `evaluation_id` | Student/instructor-assigned run/protocol identifier |
| `protocol_version`, `dataset_schema_version` | Frozen evaluation and input schema versions |
| `comparison_design`, `comparison_protocol_reference` | Approved switchback/matched-period design and its reference |
| `source_description`, `source_reference`, `permission_reference` | Dataset source and approved collection/reuse provenance |
| `centre_id`, `crop_code`, `season_code` | Authorized scope keys |
| `period_start`, `period_end`, `extracted_at` | Timezone-aware ISO-8601 cohort boundaries and follow-up extraction time; period uses `[start, end)` for check-ins |
| `centre_configuration_reference`, `service_assumptions_reference` | Approved configuration and service assumptions shared by both arms |
| `policy_versions_by_arm` | Object with explicit non-empty `fcfs` and `slot_policy` version strings |
| `scheduled_open_minutes_by_arm` | Object with explicit positive scheduled open minutes for each arm, sourced from authorized calendar settings |
| `demand_equivalence_mode` | Currently must be `exact_equal_arrival_counts_per_period`; no adjustment model is implemented |
| `fairness_groups_authorized` | Boolean authorization gate |
| `fairness_group_authorization_reference` | Required if grouping is authorized; otherwise leave blank |
| `fairness_minimum_group_observations` | Approved positive integer or null; null makes fairness spread unavailable |
| `no_show_policy_authorized` | Boolean authorization gate for confirmed no-show rows |
| `no_show_policy_authorization_reference` | Required when no-show classification is authorized; otherwise leave blank |

The pipeline requires both arms, identical matched comparison-block identifiers, equal eligible arrival counts per block and service stream, equal scheduled open minutes, matching centre/crop/season/configuration/service assumptions, and equal right-censored counts before it reports a total-wait difference. Otherwise arm metrics may still be returned while the comparison is explicitly unavailable. It reports the arithmetic `slot_policy total - FCFS total`; this is descriptive only and does not establish reduction or causality.

## Reproducibility and output

Run from the repository root in PowerShell after activating `.venv` and setting `PYTHONPATH` as shown in `README.md`. The CLI accepts an authorized CSV and settings JSON, computes SHA-256 hashes, and writes machine-readable JSON to stdout or a path explicitly supplied with `--output`. It records source and permission references, protocol/schema versions, environment version and run time. Invalid schema/settings produce JSON with `result_status: invalid_input` and a nonzero exit code.

The pipeline computes observed arm metrics and checks FCFS arrival ordering. It does not generate slots, simulate arrivals/service, infer missing capacity/hours/durations, fit a live-wait estimator, calculate confidence intervals, or create project results by itself. An approved uncertainty/adequacy analysis remains necessary before reporting inferential claims.
