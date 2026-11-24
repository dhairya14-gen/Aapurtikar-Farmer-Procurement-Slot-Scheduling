# Phase 9A CA-1 Report Draft Checklist

**Project:** Farmer Procurement Slot Scheduling and Wait Time Reduction
**Course / Section / Group:** CSE276 / K3P25LH / G24
**Problem ID:** SIH26032
**Draft:** `report/CA1_Report_Draft.docx`
**Status:** Editable draft based on the supplied CA-1 Report Template. It is not ready for final submission.

## Chapters and sections

| Required section | Draft status | Remaining work |
|---|---|---|
| Declaration | Included | Students must confirm declaration wording and sign. |
| Abstract (150–250 words) | Included; 205 words | Student review and instructor AI wording confirmation. |
| Keywords | Included | Confirm preferred terms if required. |
| Table of Contents | Included, matching template order | Replace `[TBD]` page numbers after pagination in Word. |
| 1. Introduction | Drafted with template subsections | Confirm the official SIH source link and project context. |
| 2. Objectives | Exact three allocated objectives included unchanged | Student/instructor review. |
| 3. Related Work | Public data-system context reviewed | Add verified peer-reviewed scheduling literature if required; no such papers were verified in the source register. |
| 4. Dataset | Public context sources distinguished from operational event data | No operational dataset; source access and reuse terms remain incomplete. |
| 5. Methodology | FCFS, candidate policy, comparison design and metrics described | Confirm CSE276 syllabus mapping and operational policy approvals. |
| 6. Implementation | Describes inspected code, recorded tests and later live demonstration | Insert genuine screenshots if available; verify implementation statements as a group. |
| 7. Results and Evaluation | Evaluation setup and unavailable results documented | Numerical comparison is blocked by absence of genuine authorized data. No improvement claim is made. |
| 8. Limitations and Ethical Considerations | Drafted | Confirm institution/centre privacy and data-collection requirements. |
| 9. Conclusion and Future Work | Drafted | Update after actual evaluation and student review. |
| References | IEEE-numbered entries [1]–[8] included | Confirm exact official SIH link and validate source-specific citation details and reuse terms. |
| Appendix A: Individual Contribution | Table included with explicit placeholders | Replace with each member’s real contribution and share; obtain signatures. |
| Appendix B: Code Repository and Folder Structure | Current structure included | Insert repository URL or final ZIP/submission reference. |
| Appendix C: Additional Results | Included; states none are available | Add only genuine, validated results if produced. |

## Page count and formatting

- **Required length:** 12–20 pages from Chapter 1 through References, excluding title page, declaration, contents and appendices.
- **Actual page count:** Not verified. The bundled `render_docx.py` was run but stopped because bundled LibreOffice (`soffice.exe`) is unavailable. A read-only Microsoft Word COM pagination attempt was blocked by Windows with `80070005 (E_ACCESSDENIED)`. No page count is claimed.
- **Table of Contents page numbers:** Pending pagination; currently marked `[TBD]`.
- **A4 page size:** Set in the DOCX section properties and verified by reading the saved document.
- **Margins:** 1 inch on all four sides, verified in the saved DOCX.
- **Body font and spacing:** Normal/Body Text styles set to Times New Roman 12 pt and 1.5 line spacing. Table content uses smaller table typography for fit; confirm any instructor-specific table exception.
- **Visual formatting verification:** Incomplete. Page images could not be rendered after both the bundled renderer and local Word automation were unavailable/blocked. Final pagination, line breaks, table flow and visual fidelity still require review in Microsoft Word.
- **Official template:** Supplied template was used as the DOCX base; its chapter headings/order and existing cover, signature, mapping, results and contribution tables were retained and populated. The supplied source file was not modified.

## Evidence and data gaps

- No genuine event-level operational dataset or authorized check-in/service-start timestamps are available.
- No measured FCFS-versus-slot-policy results, EDA charts, operational statistics or waiting-time reduction claim are included.
- Public sources are contextual only. AGMARKNET file access failed; OGD resource records were not downloaded; CFPP aggregate HTML was inspected but not an event dataset; e-NAM access failed; PSAMB record fields and terms were not verified.
- No screenshot images are present in `report/demo_evidence/`; five clearly labelled image placeholders are in the DOCX. Copy actual screenshots into that folder before inserting them.
- Phase 8B recorded 26 backend tests and 15 scheduling/evaluation tests passing; frontend TypeScript check and production build passed. These are software verification results, not operational performance results.
- The later live demonstration record reports manual Chrome inspection of all five views, health/status API responses and a booking `POST` response of HTTP 409. It was not browser automation.
- PostgreSQL runtime remains unverified; the running API reports database status `not_checked`.
- CMS Kapurthala, New Dana Mandi remains proposed and unverified; bookings and live wait estimates remain disabled.

## Student or instructor confirmation required

- All member names, registration numbers and roll numbers; correct number of member rows.
- Actual individual contributions, contribution percentages, and signatures.
- Instructor name and confirmed submission date.
- Exact AI-use declaration wording and location required by the instructor; the draft discloses ChatGPT assistance.
- Exact official SIH26032 problem statement URL from the allocation document.
- CSE276 course title and syllabus-unit mapping.
- Repository URL or intended final ZIP reference.
- Whether a wider peer-reviewed related-work review is required and which sources the instructor approves.
- Centre and institutional permissions, verified operating configuration, event definitions, privacy process and approved evaluation rules before real data collection.

## Finalization gate

Before submission, paginate and visually inspect the document in Word, confirm the Chapter 1–References page count is 12–20, refresh the contents page, replace all student/instructor placeholders, verify every reference and citation, add actual screenshots if available, and obtain the required signatures. Do not add fabricated results or enable bookings to fill report gaps.
