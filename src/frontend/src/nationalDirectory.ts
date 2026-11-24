/**
 * Aapurtikar India-wide starter directory.
 *
 * These are source-backed directory/tender references, NOT a claim that a centre
 * is currently accepting farmers or has live appointment capacity. Source type,
 * publication date and verification caveats are retained per record.
 */
export type CentreRecord = {
  id: string
  name: string
  state: string
  district: string
  address?: string
  pincode?: string
  agency?: string
  centreType: string
  commodity?: string
  season?: string
  sourceDate: string
  sourceName: string
  sourceUrl: string
  recordStatus: 'official-tender-reference' | 'official-directory-listing' | 'portal-listing'
  verificationNote: string
}

export const INDIA_STATES_AND_UTS = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
  'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
  'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
  'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu',
  'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry',
] as const

export const CENTRE_DIRECTORY_SOURCES = [
  {
    name: 'CFPP — Central Foodgrains Procurement Portal',
    url: 'https://cfpp.nic.in/',
    detail: 'National current-season reporting portal. Refreshed 24 Nov 2026; KMS 2026-27 is shown as current. Public dashboard values may be zero/not yet reported; not used as centre-level proof by itself.',
  },
  {
    name: 'e-NAM APMC Contact Details',
    url: 'https://enam.gov.in/apmc-contact-details',
    detail: 'National mandi/APMC locator with state, district and APMC filters. A mandi/APMC is not automatically an MSP procurement centre.',
  },
  {
    name: 'Haryana State Agricultural Marketing Board — Mandi directory',
    url: 'https://hsamb.org.in/infrastructure/hsamb-mandi-s',
    detail: 'Official purchase-centre / sub-yard / principal-yard directory. The linked detailed list is dated 28 Nov 2024; seasonal operation must be rechecked.',
  },
  {
    name: 'Uttar Pradesh eProcurement System',
    url: 'https://etender.up.nic.in/',
    detail: 'Official tender notices identify named procurement centres for transport/handling work; a tender reference is not proof of open farmer intake or live slots.',
  },
  {
    name: 'NAFED e-Samridhi PM-AASHA portal',
    url: 'https://esamridhi.da.gov.in/',
    detail: 'Portal listing evidence for procurement-related centres. Crop, season, procurement dates and centre operation need confirmation from the active portal record.',
  },
] as const

export const INDIA_CENTRES: CentreRecord[] = [
  {
    id: 'up-bijaura-pcf',
    name: 'Centre-B Pax Bijaura (PCF)',
    state: 'Uttar Pradesh',
    district: 'Siddharth Nagar',
    address: 'Centre-B Pax Bijaura (PCF), District Siddharth Nagar',
    pincode: '272203',
    agency: 'Pradesh Cooperative Federation (PCF)',
    centreType: 'Paddy procurement centre',
    commodity: 'Paddy',
    season: 'KMS 2026-27',
    sourceDate: '20 Jul 2026',
    sourceName: 'eProcurement System, Government of Uttar Pradesh',
    sourceUrl: 'https://etender.up.nic.in/nicgep/app?component=%24DirectLink_0&page=FrontEndAdvancedSearchResult&service=direct&sp=SoM41VKVw%2BfHh9gZ2WC3Umg%3D%3D',
    recordStatus: 'official-tender-reference',
    verificationNote: 'Official tender names this centre for paddy purchase 2026-27 transport work and gives PIN 272203. This verifies a procurement tender reference, not current farmer intake, operating hours or available slots.',
  },
  {
    id: 'up-ramaipur1-fcs',
    name: 'Ramaipur 1 (FCS) BDH',
    state: 'Uttar Pradesh',
    district: 'Mirzapur',
    address: 'Mirzapur, Uttar Pradesh',
    pincode: '231001',
    agency: 'Department of Food and Civil Supplies, Uttar Pradesh',
    centreType: 'Paddy and wheat procurement centre',
    commodity: 'Paddy (KMS 2026-27); Wheat (RMS 2027-28)',
    season: 'KMS 2026-27 / RMS 2027-28',
    sourceDate: '18 Nov 2026',
    sourceName: 'eProcurement System, Government of Uttar Pradesh',
    sourceUrl: 'https://etender.up.nic.in/nicgep/app?component=%24DirectLink&page=FrontEndViewTender&service=direct&sp=SlPMpmX%2FmXtXQtOQru200aA%3D%3D',
    recordStatus: 'official-tender-reference',
    verificationNote: 'Official tender identifies the centre and RFC Mirzapur; published 18 Nov 2026 with bid opening 23 Nov 2026. This is not evidence of live farmer intake or slot capacity.',
  },
  {
    id: 'hr-munak',
    name: 'Munak',
    state: 'Haryana',
    district: 'Karnal',
    agency: 'Haryana State Agricultural Marketing Board (HSAMB)',
    centreType: 'Purchase centre directory listing',
    sourceDate: '28 Nov 2024',
    sourceName: 'HSAMB List of Purchase Centre, Sub Yard & Principal Yard',
    sourceUrl: 'https://hsamb.org.in/sites/default/files/documents/Latest%20List%20of%20Principal%20Yard%2C%20Sub%20Yard%20and%20Purchase%20Center%20as%20on%2028.11.2024.pdf',
    recordStatus: 'official-directory-listing',
    verificationNote: 'Official Haryana directory entry under Karnal. The detailed list is dated 28 Nov 2024; commodity and current 2026-27 procurement operation are not confirmed.',
  },
  {
    id: 'hr-salwan',
    name: 'Salwan',
    state: 'Haryana',
    district: 'Karnal',
    agency: 'Haryana State Agricultural Marketing Board (HSAMB)',
    centreType: 'Purchase centre directory listing',
    sourceDate: '28 Nov 2024',
    sourceName: 'HSAMB List of Purchase Centre, Sub Yard & Principal Yard',
    sourceUrl: 'https://hsamb.org.in/sites/default/files/documents/Latest%20List%20of%20Principal%20Yard%2C%20Sub%20Yard%20and%20Purchase%20Center%20as%20on%2028.11.2024.pdf',
    recordStatus: 'official-directory-listing',
    verificationNote: 'Official Haryana directory entry under Karnal. The detailed list is dated 28 Nov 2024; commodity and current 2026-27 procurement operation are not confirmed.',
  },
  {
    id: 'hr-rahar',
    name: 'Rahara',
    state: 'Haryana',
    district: 'Karnal',
    agency: 'Haryana State Agricultural Marketing Board (HSAMB)',
    centreType: 'Purchase centre directory listing',
    sourceDate: '28 Nov 2024',
    sourceName: 'HSAMB List of Purchase Centre, Sub Yard & Principal Yard',
    sourceUrl: 'https://hsamb.org.in/sites/default/files/documents/Latest%20List%20of%20Principal%20Yard%2C%20Sub%20Yard%20and%20Purchase%20Center%20as%20on%2028.11.2024.pdf',
    recordStatus: 'official-directory-listing',
    verificationNote: 'Official Haryana directory entry under Karnal. The detailed list is dated 28 Nov 2024; commodity and current 2026-27 procurement operation are not confirmed.',
  },
  {
    id: 'hr-sagga',
    name: 'Sagga',
    state: 'Haryana',
    district: 'Karnal',
    agency: 'Haryana State Agricultural Marketing Board (HSAMB)',
    centreType: 'Purchase centre directory listing',
    sourceDate: '28 Nov 2024',
    sourceName: 'HSAMB List of Purchase Centre, Sub Yard & Principal Yard',
    sourceUrl: 'https://hsamb.org.in/sites/default/files/documents/Latest%20List%20of%20Principal%20Yard%2C%20Sub%20Yard%20and%20Purchase%20Center%20as%20on%2028.11.2024.pdf',
    recordStatus: 'official-directory-listing',
    verificationNote: 'Official Haryana directory entry under Karnal. The detailed list is dated 28 Nov 2024; commodity and current 2026-27 procurement operation are not confirmed.',
  },
  {
    id: 'hr-garhi-birbal',
    name: 'Garhi Birbal',
    state: 'Haryana',
    district: 'Karnal',
    agency: 'Haryana State Agricultural Marketing Board (HSAMB)',
    centreType: 'Purchase centre directory listing',
    sourceDate: '28 Nov 2024',
    sourceName: 'HSAMB List of Purchase Centre, Sub Yard & Principal Yard',
    sourceUrl: 'https://hsamb.org.in/sites/default/files/documents/Latest%20List%20of%20Principal%20Yard%2C%20Sub%20Yard%20and%20Purchase%20Center%20as%20on%2028.11.2024.pdf',
    recordStatus: 'official-directory-listing',
    verificationNote: 'Official Haryana directory entry under Karnal. The detailed list is dated 28 Nov 2024; commodity and current 2026-27 procurement operation are not confirmed.',
  },
  {
    id: 'hr-samana-bahu',
    name: 'Samana Bahu',
    state: 'Haryana',
    district: 'Karnal',
    agency: 'Haryana State Agricultural Marketing Board (HSAMB)',
    centreType: 'Purchase centre directory listing',
    sourceDate: '28 Nov 2024',
    sourceName: 'HSAMB List of Purchase Centre, Sub Yard & Principal Yard',
    sourceUrl: 'https://hsamb.org.in/sites/default/files/documents/Latest%20List%20of%20Principal%20Yard%2C%20Sub%20Yard%20and%20Purchase%20Center%20as%20on%2028.11.2024.pdf',
    recordStatus: 'official-directory-listing',
    verificationNote: 'Official Haryana directory entry under Karnal. The detailed list is dated 28 Nov 2024; commodity and current 2026-27 procurement operation are not confirmed.',
  },
  {
    id: 'hr-barna',
    name: 'Barna',
    state: 'Haryana',
    district: 'Kurukshetra',
    agency: 'Haryana State Agricultural Marketing Board (HSAMB)',
    centreType: 'Purchase centre directory listing',
    sourceDate: '28 Nov 2024',
    sourceName: 'HSAMB List of Purchase Centre, Sub Yard & Principal Yard',
    sourceUrl: 'https://hsamb.org.in/sites/default/files/documents/Latest%20List%20of%20Principal%20Yard%2C%20Sub%20Yard%20and%20Purchase%20Center%20as%20on%2028.11.2024.pdf',
    recordStatus: 'official-directory-listing',
    verificationNote: 'Official Haryana directory entry under Kurukshetra. The detailed list is dated 28 Nov 2024; commodity and current 2026-27 procurement operation are not confirmed.',
  },
  {
    id: 'hr-kirmach',
    name: 'Kirmach',
    state: 'Haryana',
    district: 'Kurukshetra',
    agency: 'Haryana State Agricultural Marketing Board (HSAMB)',
    centreType: 'Purchase centre directory listing',
    sourceDate: '28 Nov 2024',
    sourceName: 'HSAMB List of Purchase Centre, Sub Yard & Principal Yard',
    sourceUrl: 'https://hsamb.org.in/sites/default/files/documents/Latest%20List%20of%20Principal%20Yard%2C%20Sub%20Yard%20and%20Purchase%20Center%20as%20on%2028.11.2024.pdf',
    recordStatus: 'official-directory-listing',
    verificationNote: 'Official Haryana directory entry under Kurukshetra. The detailed list is dated 28 Nov 2024; commodity and current 2026-27 procurement operation are not confirmed.',
  },
  {
    id: 'hr-lukhi',
    name: 'Lukhi',
    state: 'Haryana',
    district: 'Kurukshetra',
    agency: 'Haryana State Agricultural Marketing Board (HSAMB)',
    centreType: 'Purchase centre directory listing',
    sourceDate: '28 Nov 2024',
    sourceName: 'HSAMB List of Purchase Centre, Sub Yard & Principal Yard',
    sourceUrl: 'https://hsamb.org.in/sites/default/files/documents/Latest%20List%20of%20Principal%20Yard%2C%20Sub%20Yard%20and%20Purchase%20Center%20as%20on%2028.11.2024.pdf',
    recordStatus: 'official-directory-listing',
    verificationNote: 'Official Haryana directory entry under Kurukshetra. The detailed list is dated 28 Nov 2024; commodity and current 2026-27 procurement operation are not confirmed.',
  },
  {
    id: 'hr-bodni',
    name: 'Bodni',
    state: 'Haryana',
    district: 'Kurukshetra',
    agency: 'Haryana State Agricultural Marketing Board (HSAMB)',
    centreType: 'Purchase centre directory listing',
    sourceDate: '28 Nov 2024',
    sourceName: 'HSAMB List of Purchase Centre, Sub Yard & Principal Yard',
    sourceUrl: 'https://hsamb.org.in/sites/default/files/documents/Latest%20List%20of%20Principal%20Yard%2C%20Sub%20Yard%20and%20Purchase%20Center%20as%20on%2028.11.2024.pdf',
    recordStatus: 'official-directory-listing',
    verificationNote: 'Official Haryana directory entry under Kurukshetra. The detailed list is dated 28 Nov 2024; commodity and current 2026-27 procurement operation are not confirmed.',
  },
  {
    id: 'mh-magathane',
    name: 'Magathane APMC Center',
    state: 'Maharashtra',
    district: 'Thane',
    address: 'APC 0091 to 0093, Ground floor, Agro Industries, 12B SP Marg, Thane City, Thane - 400066',
    agency: 'NAFED (e-Samridhi / PM-AASHA portal)',
    centreType: 'APMC / procurement portal listing',
    season: 'PSS 2026-27 (portal listing; crop and centre operations require confirmation)',
    sourceDate: 'Portal listing accessed 24 Nov 2026',
    sourceName: 'NAFED e-Samridhi Unified Portal',
    sourceUrl: 'https://esamridhi.da.gov.in/',
    recordStatus: 'portal-listing',
    verificationNote: 'A named APMC Center and address appear in the NAFED e-Samridhi portal index. The specific commodity, current procurement window and live slot/capacity are not established by this listing alone.',
  },
]
