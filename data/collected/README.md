# Collected centre directory data — 24 November 2026

The five-page React application loads the supplemental directory from `src/frontend/public/collected-centres.json.gz`.

## Reconciliation
- Existing directory preserved: 76 source-tracked APMC/mandi and procurement references.
- Added: 220 official Haryana State Agricultural Marketing Board (HSAMB) purchase-centre inventory rows.
- Added: 13 non-duplicate non-Haryana discovery leads from 14 source rows.
- One Uttar Pradesh lead (`Ramaipur 1 (FCS) BDH`, Mirzapur) duplicates an existing source-tracked entry, so it is suppressed from the supplemental asset; the existing directory entry remains available in the UI.
- Combined selectable UI directory: 309 listings and leads across 20 States/UTs.

## Verification boundaries
HSAMB inventory is a government market-facility directory dated 28 November 2024. It does not prove current-season procurement activation, crop eligibility, agency assignment, active hours, capacity or live farmer intake. The non-Haryana additions are discovery leads; they are not confirmed operating centres. Missing data is left blank rather than invented.

Real bookings, published slots, live capacity, centre queue and live wait estimates remain disabled. Demo reservations remain local browser-session state.
