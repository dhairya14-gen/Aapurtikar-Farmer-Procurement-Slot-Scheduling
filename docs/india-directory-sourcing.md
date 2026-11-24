# Aapurtikar India-wide directory: source and verification notes

## Scope
The national directory is being built as a source-tracked catalogue of physical mandi/APMC listings and government procurement-centre references. Those are different entity types and must remain distinguishable in the UI and data model.

## Current seed records
- Uttar Pradesh: two 2026-27 procurement-centre references were checked on the official UP eProcurement portal:
  - Centre-B Pax Bijaura (PCF), Siddharth Nagar, PIN 272203; tender published 20 July 2026 for paddy 2026-27 and wheat 2027-28 transport work.
  - Ramaipur 1 (FCS) BDH, Mirzapur, PIN 231001; tender published 18 November 2026 for KMS 2026-27 paddy and RMS 2027-28 wheat transport work.
  These tender notices prove that the named centres are referenced in government procurement/handling tenders. They do not prove that a centre is open for farmer arrivals or has slots/capacity now.
- Haryana: the HSAMB public directory lists 220 purchase centres. The linked detailed list is dated 28 November 2024. The starter app seeds ten named examples from Karnal and Kurukshetra districts. The list is a market infrastructure directory, not a current-season operational status feed.
- Maharashtra: the NAFED e-Samridhi portal index surfaces Magathane APMC Center, Thane, with an address. Commodity and live operating schedule are not confirmed by the portal listing alone.

## National source catalogue
- CFPP: https://cfpp.nic.in/ — current season displayed as KMS 2026-27 and portal refresh 24 Nov 2026. The national public dashboard showed zero values at the time of inspection; do not interpret zero as zero real-world procurement. The master report list includes “List of Procurement Centres in State”; report extraction is still being checked.
- e-NAM APMC Contact Details: https://enam.gov.in/apmc-contact-details — national APMC contact directory. APMC participation does not itself prove MSP procurement.
- State portals should supply centre name, type, operating agency, address, season and active dates. West Bengal ePaddy public directory: https://epaddy.wb.gov.in/PublicProfile/KnowYourNearestPurchaseCenter (requires district/block filter; public endpoint was intermittently inaccessible during inspection).

## Critical product rules
1. Never label a mandi/APMC as an MSP procurement centre without source evidence.
2. Never infer a procurement agency, crop eligibility, opening hours, contact number, operating status, available slots or bay capacity.
3. Preserve source URL, publication/last-verified date and entity type.
4. Real operational booking and live wait APIs remain disabled until authorization and live feeds exist.
5. Demo bookings are local simulated transactions only and must be visibly labelled as such.
