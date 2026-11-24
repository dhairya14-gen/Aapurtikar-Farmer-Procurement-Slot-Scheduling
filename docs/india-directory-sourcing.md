# Aapurtikar India-wide market and procurement directory

## Current seed status (24 November 2026)

The frontend seed contains **76 named records across 20 States/UTs**. This is a starter source-backed directory, not complete nationwide operational coverage.

The records are deliberately separated by type:

- **63 e-NAM APMC/mandi directory records** from the official e-NAM Aspirational Districts mapping. These are physical market/mandi listings. They are **not automatically MSP purchase centres**.
- **10 HSAMB purchase-centre directory entries** from Haryana's official list dated 28 November 2024. These are historical directory entries; current season operation is not confirmed.
- **2 Uttar Pradesh procurement-centre tender references** from the official UP eProcurement portal, published 20 July 2026 and 18 November 2026.
- **1 NAFED e-Samridhi APMC portal listing** for Magathane APMC Center, Thane. The specific commodity and live procurement schedule are not confirmed.

States/UTs with seed records: Andhra Pradesh, Assam, Bihar, Chhattisgarh, Gujarat, Haryana, Himachal Pradesh, Jammu and Kashmir, Jharkhand, Kerala, Madhya Pradesh, Maharashtra, Nagaland, Odisha, Punjab, Rajasthan, Tamil Nadu, Tripura, Uttar Pradesh and Uttarakhand.

All 36 States/UTs are available in the farmer selector. For States/UTs with no source-backed record loaded, the app says so rather than inventing a centre.

## Primary national sources

### e-NAM
- National APMC directory: https://enam.gov.in/NAMV2/home/mandis.html
- Aspirational Districts state/district/mandi mapping: https://enam.gov.in/aspirational-districts
- APMC contact details and directory locator: https://enam.gov.in/apmc-contact-details
- Older downloadable e-NAM Directory PDF (20 July 2021): https://enam.gov.in/assest/download/eNAM_Directory_20210720.pdf

The aspirational-district page exposes a named State / District / Mandi table. The app labels these as e-NAM APMC/mandi records and does not infer that they procure at MSP.

### Central Foodgrains Procurement Portal (CFPP)
- Portal: https://cfpp.nic.in/
- Master reports: https://cfpp.nic.in/cfppui/reports/master_reports.html
- Agencies and centre reports: https://cfpp.nic.in/cfppui/reports/agency_center_reports.html
- Centre/master report landing page: https://cfpp.nic.in/cfppui/reports/reportsdata.html

The CFPP homepage displayed KMS 2026-27 as the current season and a portal refresh of 24 November 2026. Its public dashboard showed zero values at the time of inspection. Do not treat those zeroes as proof that no procurement is taking place. The “List of Procurement Centres in State” report was visible in the master reports menu, but its public navigation did not expose a distinct filterable centre table or export during this inspection. Granular report access may require further investigation/authentication.

### Haryana
- HSAMB market and purchase-centre directory: https://hsamb.org.in/infrastructure/hsamb-mandi-s
- Detailed PDF dated 28 November 2024: https://hsamb.org.in/sites/default/files/documents/Latest%20List%20of%20Principal%20Yard%2C%20Sub%20Yard%20and%20Purchase%20Center%20as%20on%2028.11.2024.pdf

The HSAMB page reports counts of Principal Yards, Purchase Centres and Sub Yards and provides district-wise names. The detailed list is dated 28 November 2024; it is not a 2026-27 operating calendar.

### Uttar Pradesh
- Official UP eProcurement portal: https://etender.up.nic.in/
- Bijaura (PCF) tender reference, published 20 July 2026: https://etender.up.nic.in/nicgep/app?component=%24DirectLink_0&page=FrontEndAdvancedSearchResult&service=direct&sp=SoM41VKVw%2BfHh9gZ2WC3Umg%3D%3D
- Ramaipur 1 (FCS) BDH tender reference, published 18 November 2026: https://etender.up.nic.in/nicgep/app?component=%24DirectLink&page=FrontEndViewTender&service=direct&sp=SlPMpmX%2FmXtXQtOQru200aA%3D%3D

These tenders identify named procurement-centre references and location/agency context. They do not prove current farmer intake, opening hours, crop eligibility, available capacity or live appointments.

### Maharashtra
- NAFED e-Samridhi / PM-AASHA portal: https://esamridhi.da.gov.in/
- e-NAM APMC directory (Basmat, Hingoli): https://enam.gov.in/NAMV2/home/mandis.html

The Magathane portal listing shows a Thane address. Commodity, active procurement window and real-time capacity require confirmation from the relevant active portal record.

### State portal research leads
- West Bengal ePaddy public “Know Your Nearest Purchase Center”: https://epaddy.wb.gov.in/PublicProfile/KnowYourNearestPurchaseCenter
- Andhra Pradesh paddy procurement portal: https://paddyprocurement.ap.gov.in/
- Telangana Paddy Procurement System: https://pps.telangana.gov.in
- Assam FCSCA PPC list: https://fcsca.assam.gov.in/information-services/detail/list-of-paddy-purchase-centre-ppcs
- Odisha State Civil Supplies Corporation: https://oscsc.in/en/transparency-portal/paddy-procurement/

West Bengal's public locator exposes district, block, agency and centre-type filters, and centre results include name, type, agency, venue/address, purchase date and slot status; its endpoint was intermittent from the research browser. Andhra Pradesh's current CFPP state dashboard exposed aggregated centre counts but not individual PPC/RSK names/addresses. Telangana's PPS portal and Assam's FCSCA page did not expose a public centre-level list in this inspection.

## Product rules

1. Keep e-NAM APMC/mandi records, state marketing-board purchase-centre records, MSP procurement-centre tender references, CPCs, mCPCs, DPCs and PPCs as distinct entity types.
2. A mandi/APMC listing is not proof of MSP procurement. Never infer that an e-NAM mandi accepts a particular MSP commodity.
3. Never infer a procurement agency, address, PIN, coordinates, commodity eligibility, operating hours, opening date, current operating status, public contact, slot inventory or bay capacity.
4. Every record keeps its exact source URL, source date or “undated” label, record type, and a verification caveat.
5. The national location selector covers all States/UTs, but only source-backed states have loaded records. Do not claim complete coverage.
6. Real operational bookings and live wait APIs remain disabled in the backend.
7. Demo reservations are local React page-session state only. They are not sent to the API, stored in the backend, transmitted to a procurement agency or counted as real bookings.
8. The sample time windows are illustrative UI values, not centre-published availability.
