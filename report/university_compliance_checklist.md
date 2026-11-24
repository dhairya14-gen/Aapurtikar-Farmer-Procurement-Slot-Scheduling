# CA-1 Compliance Checklist and Report-to-Artifact Map

**Course / Section / Group:** CSE276 / K3P25LH / G24
**Project:** Farmer Procurement Slot Scheduling and Wait Time Reduction
**SIH Problem ID:** SIH26032
**Checklist basis:** CA-1 requirements supplied by the student on 15 November 2026.
**Status key:** `Ready` means the requested planning artifact exists; `Planned` means a future deliverable is mapped but not complete; `Blocked` means evidence, real student information, or approval is missing.

The exact report, formatting, referencing, presentation, and declaration requirements below are taken from the supplied CA-1 instructions. A separate marking rubric, cover-page template, exact AI declaration wording, and precise signature roles were not included in the provided requirements; confirm those details if the instructor requires them.

## Required report structure and chapter map

Planned final report artifact: `report/CA1_Report.docx`. This file has not been created. Use the exact chapter sequence below. The report must be **12–20 pages from Chapter 1 through References**.

| Required chapter / section | Planned content and supporting artifact | Status / gap |
|---|---|---|
| Chapter 1: Introduction | Problem context, SIH26032, Kapurthala scope, stakeholders, and boundary that the centre is only proposed | Planned; final narrative not written |
| Chapter 2: Objectives | Copy the three allocated objectives exactly; state unmanaged FCFS as mandatory baseline | Objectives are recorded in `README.md` and `docs/requirements_and_evaluation.md`; final report chapter planned |
| Chapter 3: Related Work | Literature and comparable methods, with claims supported by IEEE numbered citations | Planned; literature review not completed |
| Chapter 4: Dataset | Candidate public sources, provenance, fields, temporal/geographic coverage, reuse terms, data dictionary, and distinction between aggregates and event-level operational data | Source register at `data/metadata/source_register.csv`; dictionary template at `data/metadata/data_dictionary_template.csv`; no operational records |
| Chapter 5: Methodology | FCFS baseline, proposed slot policy, metric formulas, event handling, expected-wait evidence, reproducible pipeline, and comparison design | Detailed design in `docs/scheduling_methodology.md`, summarized in `docs/requirements_and_evaluation.md`; proposal only, no method implemented/evaluated |
| Chapter 6: Implementation | Implemented system, verified screens/endpoints, dependencies, and test evidence | Current code is only a Phase 3 foundation; booking/scheduling/live estimate are not implemented |
| Chapter 7: Results and Evaluation | Compare proposed method against unmanaged FCFS for total wait and report the objective metrics: mean and worst-case wait, throughput, fairness spread | Blocked until genuine authorized baseline and intervention observations exist; no results, charts, or performance claims currently exist |
| Chapter 8: Limitations and Ethical Considerations | Data access limits, proposed-centre uncertainty, privacy/consent, fairness, missingness, and limits of the comparison | Planning notes in `docs/data_collection_protocol.md` and this checklist; final chapter planned |
| Chapter 9: Conclusion and Future Work | Conclusions supported only by completed evidence; next development and data-approval steps | Planned; cannot claim measured reduction now |
| References | IEEE numbered citations in order of appearance; every cited source has a corresponding numbered reference | Source URLs recorded in `data/metadata/source_register.csv`; IEEE bibliography not yet prepared |
| Appendix A: Individual Contribution | Per-member name/identifier, specific contribution, evidence/artifact, and signature | Template needed in final report; member names, contribution evidence, and signatures must come from students |
| Appendix B: Code Repository and Folder Structure | Repository URL, branch/commit reference at submission time, required directory tree, and concise file descriptions | Structure exists and is listed below; final submission reference must be recorded by the group |
| Appendix C: Additional Results | Supplementary genuine results only, with definitions and provenance | No additional results exist; leave empty or state none if permitted by instructor |

## Formatting and presentation requirements

| Requirement | Planned artifact / check | Status |
|---|---|---|
| Report length: 12–20 pages from Chapter 1 through References | `report/CA1_Report.docx`; count the specified section only | Not yet prepared |
| Paper size: A4 | Set document page size to A4 | Not yet applied |
| Body font: Times New Roman, 12 pt | Apply to report body; check headings, captions, tables, and references against any instructor exceptions | Not yet applied |
| Line spacing: 1.5 | Apply to report body | Not yet applied |
| Margins: 1 inch | Apply on all sides | Not yet applied |
| Referencing: IEEE numbered citations | In-text bracketed numbers and ordered reference list | Not yet applied |
| Presentation: 8–10 slides, approximately 8 minutes plus questions | `presentation/CA1_Presentation.pptx` (planned) | No slides created; timing/rehearsal pending |
| AI-use declaration | Include a truthful declaration in the report front matter or location specified by the instructor; describe assistance and student verification | Not yet included; students must confirm required wording and where it belongs |
| Individual contributions and signatures | Appendix A contribution table, then required member signature(s) | Not yet included; names, contributions, and signatures must be supplied by the group |

## Required implementation structure

| Required path | Present? | Current content / status |
|---|---:|---|
| `README.md` | Yes | Project identity, allocated objectives, baseline, deliverable, safety/readiness notes |
| `requirements.txt` | Yes | Pinned backend and later analytics dependencies |
| `data/` | Yes | `raw/`, `processed/`, `metadata/`; metadata register/template only, no dataset observations |
| `notebooks/` | Yes | `00_eda_template.ipynb`; outline only, no analysis executed |
| `src/` | Yes | React/TypeScript frontend and FastAPI foundation |
| `app/` | Yes | Reserved application artifacts; placeholder only |
| `results/` | Yes | Reserved for genuine results; currently empty |
| `report/` | Yes | This checklist; final report not yet created |
| `presentation/` | Yes | Reserved; no slide deck yet |

## Mandatory objective and baseline integrity

The following text must remain unchanged in the final report and project materials:

1. Build a scheduling system that allocates arrival slots and publishes expected wait, reducing total queueing.
2. Produce a slot allocation policy compared against unmanaged arrival on total wait.
3. Report mean and worst-case wait, throughput, fairness spread.

**Mandatory baseline:** unmanaged first-come-first-served (FCFS).

The Chapter 7 comparison must include the proposed method versus this FCFS baseline for total wait. It must also report the objective metrics—mean and worst-case wait, throughput, and fairness spread—with definitions, observation windows, sample counts, exclusions, and missing-data disclosure. Do not report predicted wait as observed wait or claim improvement before genuine observations support it.

The Phase 5 metric definitions and protocol are specified in `docs/scheduling_methodology.md`. Total wait uses valid served-episode wait observations in a declared cohort/window; mean and worst-case use the same valid set; throughput uses completed episodes per authorized scheduled open hour; fairness spread requires predeclared and approved groups. The Chapter 7 analysis remains blocked until authorized genuine observations exist. The protocol also defines censored check-ins, incomplete service, cancellations, late arrivals and no-shows; unresolved operational rules require centre authorization.

## Data integrity, centre and ethics gates

- [x] No synthetic farmer, booking, queue, or wait records included.
- [x] CMS Kapurthala, New Dana Mandi remains proposed and unverified; booking remains disabled.
- [x] No capacity, opening hours, or crop eligibility invented.
- [x] Public market-arrival aggregates are not treated as individual wait-time records.
- [x] No fabricated results or charts are present.
- [ ] Obtain written university/centre permission before collecting genuine operational timestamps.
- [ ] Approve the Phase 5 protocol, including FCFS feasibility, comparison design, cohort/follow-up, closure and missingness rules, service event definitions, and statistical adequacy criteria.
- [ ] Verify centre configuration: participation, crop/season eligibility, calendar, capacity unit, staffed resources/routing, and slot/cancellation/late/no-show policies. Until verified, bookings and live estimates remain unavailable.
- [ ] Approve the live-estimate validation/release criterion and authorized service-duration evidence before showing any numeric estimate.
- [ ] Approve a justified fairness grouping and privacy basis before collecting or reporting subgroup comparisons.
- [ ] Confirm privacy notice/consent or other approved authority, access controls, retention, and deletion.
- [ ] Confirm student names, contribution records, and signatures for Appendix A.
- [ ] Confirm AI-use declaration wording and required signatory/location with the instructor.
- [ ] Check exact formatting and IEEE citation details against the supplied CA-1 document during final report production.
- [ ] Confirm source-specific reuse terms before redistributing any downloaded data.
- [ ] Create and rehearse the 8–10 slide presentation to the approximately 8-minute target.
