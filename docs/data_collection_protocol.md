# Genuine Operational Timestamp Collection Protocol

This is a plan only. Do not collect farmer data until the university and relevant centre authority approve the pilot, privacy notice, purpose, retention period, and staff workflow. CMS Kapurthala, New Dana Mandi remains a proposed, unverified candidate. Bookings remain disabled.

## Minimum event model

| Event | Timestamp source / recorder | Purpose and validation |
|---|---|---|
| Booking created | Application server records the time when a farmer or staff member submits a booking | Store event ID, booking reference, actor role, centre/config version, and UTC timestamp. Booking remains unavailable until centre configuration is authorized. |
| Slot allocated | Scheduling service records the chosen window and policy/config version | Preserve the requested and assigned slot; do not derive a historical allocation timestamp. |
| Cancellation | Farmer or authorized staff action; server records time and actor | Append cancellation event and reason category if approved. Keep the prior booking event history. |
| Farmer arrival / check-in | Authorized centre staff records check-in, or an approved check-in flow records it | Validate booking reference and centre; timestamp is server generated, actor/source recorded. A correction requires a reason and audit event. |
| Service start | Authorized staff records the agreed first procurement service step | Define this step with centre staff before collection. Require a valid check-in; retain actor and event timestamp. |
| Service completion | Authorized staff records the agreed end of the measured service episode | Define endpoint with centre staff before collection. Require a prior service-start event; retain actor and event timestamp. |
| No-show | Authorized staff or documented system rule after an approved grace period | Do not infer no-show from missing data alone. Grace period is currently unconfigured. |

## Data handling

- Store event instants in UTC; record centre timezone `Asia/Kolkata` for local display and reporting.
- Keep actual timestamps, estimated waits, slot windows, and imported public aggregate rows in distinct fields/tables.
- Use an append-only event history. Never silently overwrite an event; link corrections to the original and record reason, actor, and correction time.
- Collect the minimum identifiers necessary for appointment reconciliation. Keep direct contact details separate from evaluation exports; do not collect Aadhaar or bank details for this scheduling study.
- Restrict staff and administrator access by centre and role; log access and configuration changes.
- Before any pilot: obtain written authorization, define a farmer-facing notice/consent method, access list, retention/deletion date, incident process, and approved export procedure.

## Data quality checks

Flag missing check-in/start/completion events, duplicate event types, out-of-order times, time-zone conversions, duplicate booking references, and corrections. Retain the original source and audit trail. A flagged record is not silently repaired or included without a documented rule.
