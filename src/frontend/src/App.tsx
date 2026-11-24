import { useEffect, useMemo, useState, type ReactNode } from 'react'
import {
  apiPaths,
  getApi,
  type ApiHealth,
  type Loadable,
} from './api'
import { benchmark } from './researchData'
import { INDIA_STATES_AND_UTS, INDIA_CENTRES, type CentreRecord } from './nationalDirectory'

type Page = 'home' | 'farmer' | 'slots' | 'staff' | 'analytics'
type Crop = 'Paddy' | 'Wheat' | 'Mustard' | 'Pulses' | 'Other'
type DemoBooking = { reference: string; centreId: string; state: string; district: string; crop: Crop; date: string; slot: string }

const pages: { id: Page; label: string; number: string }[] = [
  { id: 'home', label: 'Overview', number: '01' },
  { id: 'farmer', label: 'Farmer portal', number: '02' },
  { id: 'slots', label: 'Slot preview', number: '03' },
  { id: 'staff', label: 'Centre desk', number: '04' },
  { id: 'analytics', label: 'Analytics', number: '05' },
]

function pageFromHash(): Page {
  const requested = window.location.hash.replace('#', '')
  return pages.some(({ id }) => id === requested) ? (requested as Page) : 'home'
}

function App() {
  const [page, setPage] = useState<Page>(pageFromHash)
  const [health, setHealth] = useState<Loadable<ApiHealth>>({ state: 'loading' })
  const [selectedState, setSelectedState] = useState('Uttar Pradesh')
  const [selectedDistrict, setSelectedDistrict] = useState('Siddharth Nagar')
  const [selectedCentreId, setSelectedCentreId] = useState('up-bijaura-pcf')
  const [crop, setCrop] = useState<Crop>('Paddy')
  const [visitDate, setVisitDate] = useState('')
  const [demoSlot, setDemoSlot] = useState('')
  const [demoBooking, setDemoBooking] = useState<DemoBooking | null>(null)
  const [analyticsTab, setAnalyticsTab] = useState<'simulation' | 'operational'>('simulation')

  const selectedCentre = INDIA_CENTRES.find((centre) => centre.id === selectedCentreId)
  const districtsForState = Array.from(new Set(INDIA_CENTRES.filter((centre) => centre.state === selectedState).map((centre) => centre.district))).sort()
  const centresForSelection = INDIA_CENTRES.filter((centre) => centre.state === selectedState && centre.district === selectedDistrict)

  const confirmDemoBooking = (slot: string) => {
    if (!selectedCentre || !visitDate) return
    const reference = `AAP-DEMO-${String(Date.now()).slice(-7)}`
    setDemoSlot(slot)
    setDemoBooking({
      reference,
      centreId: selectedCentre.id,
      state: selectedCentre.state,
      district: selectedCentre.district,
      crop,
      date: visitDate,
      slot,
    })
  }

  useEffect(() => {
    const controller = new AbortController()
    getApi<ApiHealth>(apiPaths.health, controller.signal).then(setHealth)
    return () => controller.abort()
  }, [])

  useEffect(() => {
    const onHashChange = () => setPage(pageFromHash())
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  const navigate = (next: Page) => {
    window.location.hash = next
    setPage(next)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="header-inner">
          <a className="brand" href="#home" onClick={() => setPage('home')} aria-label="Aapurtikar home">
            <span className="brand-mark" aria-hidden="true"><span>अ</span><i /></span>
            <span className="brand-copy"><strong>Aapurtikar</strong><small>PROCUREMENT SLOT INTELLIGENCE</small></span>
          </a>
          <nav className="main-nav" aria-label="Main navigation">
            {pages.map(({ id, label }) => (
              <a key={id} href={`#${id}`} className={page === id ? 'active' : ''} aria-current={page === id ? 'page' : undefined} onClick={() => setPage(id)}>
                {label}
              </a>
            ))}
          </nav>
          <div className="header-meta">
            <span className="project-id">SIH26032 <b>·</b> G24</span>
            <span className="prototype-chip"><span className="chip-dot" /> Student prototype</span>
          </div>
        </div>
      </header>

      <main className="page-shell">
        <div className="prototype-banner">
          <div><span className="banner-pulse" /> ACADEMIC PROTOTYPE <b>·</b> INDIA-WIDE DIRECTORY PILOT <b>·</b> SOURCE-TRACKED CENTRE LISTINGS</div>
          <div className="banner-gates"><span>REAL BOOKINGS DISABLED</span><span>DEMO MODE LOCAL ONLY</span></div>
        </div>
        <ApiStatusBar health={health} />

        {page === 'home' && <Home navigate={navigate} />}
        {page === 'farmer' && <FarmerPortal navigate={navigate} selectedState={selectedState} setSelectedState={setSelectedState} selectedDistrict={selectedDistrict} setSelectedDistrict={setSelectedDistrict} selectedCentreId={selectedCentreId} setSelectedCentreId={setSelectedCentreId} crop={crop} setCrop={setCrop} visitDate={visitDate} setVisitDate={setVisitDate} selectedCentre={selectedCentre} districtsForState={districtsForState} centresForSelection={centresForSelection} />}
        {page === 'slots' && <SlotPreview selectedState={selectedState} selectedDistrict={selectedDistrict} selectedCentre={selectedCentre} crop={crop} visitDate={visitDate} demoSlot={demoSlot} setDemoSlot={(slot) => { setDemoSlot(slot); setDemoBooking(null) }} demoBooking={demoBooking} onConfirm={confirmDemoBooking} />}
        {page === 'staff' && <CentreDesk navigate={navigate} demoBooking={demoBooking} />}
        {page === 'analytics' && <Analytics activeTab={analyticsTab} setActiveTab={setAnalyticsTab} />}
      </main>

      <footer className="site-footer">
        <div className="footer-inner">
          <span><strong>Aapurtikar</strong> <b>·</b> SIH26032 <b>·</b> Group G24</span>
          <span>Academic demonstration only <b>·</b> Not an official government service</span>
        </div>
      </footer>
    </div>
  )
}

function ApiStatusBar({ health }: { health: Loadable<ApiHealth> }) {
  const online = health.state === 'ready' && health.data.status === 'ok'
  return (
    <div className="api-status-strip" aria-live="polite">
      <span className="api-health-item"><span className={`api-dot ${online ? 'online' : health.state === 'error' ? 'offline' : ''}`} />API {online ? 'connected' : health.state === 'loading' ? 'checking' : 'offline'}</span>
      <span>Centre: {online ? health.data.centre_status : 'unverified'}</span>
      <span>Bookings: disabled</span>
      <span>Live wait estimate: disabled</span>
      {health.state === 'error' && <span className="api-strip-error">Backend not connected — prototype information remains viewable.</span>}
    </div>
  )
}

function SectionHeading({ eyebrow, title, intro, action }: { eyebrow: string; title: string; intro: string; action?: ReactNode }) {
  return (
    <div className="section-heading">
      <div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="section-intro">{intro}</p></div>
      {action}
    </div>
  )
}

function Home({ navigate }: { navigate: (page: Page) => void }) {
  return (
    <>
      <section className="hero-grid">
        <div className="hero-copy">
          <p className="eyebrow"><span className="eyebrow-line" /> FARMER-FIRST PROCUREMENT PLANNING</p>
          <h1>Less time in queues.<br /><em>More certainty at the mandi.</em></h1>
          <p className="hero-description">Aapurtikar explores how structured arrival slots can help farmers and procurement teams plan visits, balance centre capacity and understand waiting-time trade-offs.</p>
          <div className="hero-actions">
            <button className="button button-primary" onClick={() => navigate('farmer')}>Explore farmer portal <span aria-hidden="true">→</span></button>
            <button className="button button-secondary" onClick={() => navigate('staff')}>Open centre desk</button>
          </div>
          <div className="hero-assurance"><span className="check-mark">✓</span> No personal farmer data. No live booking. Transparent research prototype.</div>
        </div>
        <div className="hero-art" aria-label="Illustration of agricultural fields in Punjab">
          <div className="art-sun" /><div className="art-cloud cloud-one" /><div className="art-cloud cloud-two" />
          <div className="art-hill hill-back" /><div className="art-hill hill-front" />
          <div className="art-row row-one" /><div className="art-row row-two" /><div className="art-row row-three" />
          <div className="art-stamp"><span className="stamp-icon">🌾</span><span><strong>Punjab mandi demand profile</strong><small>Historical market data · Nov 2021</small></span></div>
          <span className="art-caption">RESEARCH PROTOTYPE · NOT A LIVE PROCUREMENT CENTRE</span>
        </div>
      </section>

      <section className="research-strip">
        <div className="research-strip-title"><span className="mini-icon">↗</span><div><strong>Built on Indian mandi data</strong><small>Public historical arrivals used as a demand-volume profile</small></div></div>
        <div className="research-stat"><strong>{benchmark.source.marketDays.toLocaleString('en-IN')}</strong><span>Market-day records</span></div>
        <div className="research-stat"><strong>{benchmark.source.markets}</strong><span>Punjab markets</span></div>
        <div className="research-stat"><strong>{benchmark.source.arrivalsTonnes.toLocaleString('en-IN', { maximumFractionDigits: 2 })} t</strong><span>Potato arrivals in source</span></div>
        <div className="research-period"><strong>1–30 Nov 2021</strong><span>Historical source period</span></div>
      </section>

      <section className="home-lower">
        <div className="home-intro"><p className="eyebrow">EXPLORE AAPURTIKAR</p><h2>One workflow.<br />Two perspectives.</h2><p>Explore the proposed farmer journey, the centre-side workspace and the benchmark evidence behind the scheduling study.</p></div>
        <div className="entry-grid">
          <button className="entry-card" onClick={() => navigate('farmer')}><span className="entry-icon farmer-symbol">♧</span><span className="entry-card-copy"><strong>Farmer portal</strong><small>Explore crop scope, proposed centre and visit-planning steps</small></span><span className="entry-arrow">→</span></button>
          <button className="entry-card" onClick={() => navigate('staff')}><span className="entry-icon staff-symbol">▦</span><span className="entry-card-copy"><strong>Centre desk</strong><small>Review operations readiness, queue gates and policy design</small></span><span className="entry-arrow">→</span></button>
          <button className="entry-card" onClick={() => navigate('analytics')}><span className="entry-icon analytics-symbol">▥</span><span className="entry-card-copy"><strong>Analytics & evaluation</strong><small>Compare FCFS with simulated appointment policies</small></span><span className="entry-arrow">→</span></button>
        </div>
      </section>

      <section className="workflow-band">
        <div><p className="eyebrow">HOW THE PROTOTYPE FITS TOGETHER</p><h2>From mandi demand to a testable policy</h2></div>
        <div className="workflow-steps">
          <WorkflowStep number="01" title="Source data" detail="Punjab mandi arrivals" />
          <span className="workflow-arrow">→</span>
          <WorkflowStep number="02" title="Synthetic events" detail="Farmer-level test stream" />
          <span className="workflow-arrow">→</span>
          <WorkflowStep number="03" title="Policy replay" detail="FCFS vs appointment slots" />
          <span className="workflow-arrow">→</span>
          <WorkflowStep number="04" title="Evaluation" detail="Wait, tail and throughput" />
        </div>
      </section>
    </>
  )
}

function WorkflowStep({ number, title, detail }: { number: string; title: string; detail: string }) {
  return <div className="workflow-step"><span>{number}</span><strong>{title}</strong><small>{detail}</small></div>
}

function FarmerPortal({
  navigate, selectedState, setSelectedState, selectedDistrict, setSelectedDistrict,
  selectedCentreId, setSelectedCentreId, crop, setCrop, visitDate, setVisitDate,
  selectedCentre, districtsForState, centresForSelection,
}: {
  navigate: (page: Page) => void
  selectedState: string
  setSelectedState: (value: string) => void
  selectedDistrict: string
  setSelectedDistrict: (value: string) => void
  selectedCentreId: string
  setSelectedCentreId: (value: string) => void
  crop: Crop
  setCrop: (value: Crop) => void
  visitDate: string
  setVisitDate: (value: string) => void
  selectedCentre: CentreRecord | undefined
  districtsForState: string[]
  centresForSelection: CentreRecord[]
}) {
  const [language, setLanguage] = useState<'English' | 'हिन्दी'>('English')
  const statusText = selectedCentre?.recordStatus === 'official-tender-reference'
    ? 'Official procurement tender reference'
    : selectedCentre?.recordStatus === 'official-directory-listing'
      ? 'Official directory entry · operation unverified'
      : selectedCentre?.recordStatus === 'portal-listing'
        ? 'Government portal listing · verify season'
        : 'Not listed'
  return (
    <div className="page-content">
      <SectionHeading
        eyebrow="FARMER PORTAL · INDIA-WIDE DEMONSTRATION"
        title="Plan a procurement visit"
        intro="Select a state, district and source-listed centre. The selection carries into the slot preview. Any reservation created here is a local demo only, not a government booking."
        action={<span className="view-tag">NATIONAL WORKFLOW</span>}
      />
      <div className="farmer-layout">
        <section className="phone-shell">
          <div className="phone-top"><span className="phone-camera" /><span> Aapurtikar <b>●</b></span><span>DEMO</span></div>
          <div className="phone-content">
            <div className="phone-brand"><span className="phone-mark">अ</span><span><strong>Aapurtikar</strong><small>Farmer procurement portal</small></span><button className="language-toggle" onClick={() => setLanguage(language === 'English' ? 'हिन्दी' : 'English')}>{language === 'English' ? 'हिंदी' : 'EN'}</button></div>
            <div className="phone-hero"><span className="phone-hero-icon">🌾</span><p className="eyebrow">WELCOME FARMER</p><h2>{language === 'English' ? 'Your visit, better planned.' : 'आपकी यात्रा, बेहतर योजना।'}</h2><p>{language === 'English' ? 'Choose a location and preview a procurement visit.' : 'स्थान चुनें और खरीद यात्रा का पूर्वावलोकन करें।'}</p></div>

            <div className="directory-form">
              <div className="directory-field">
                <label htmlFor="india-state">1. State / Union Territory</label>
                <select id="india-state" value={selectedState} onChange={(event) => {
                  const nextState = event.target.value
                  const firstCentre = INDIA_CENTRES.find((centre) => centre.state === nextState)
                  setSelectedState(nextState)
                  setSelectedDistrict(firstCentre?.district ?? '')
                  setSelectedCentreId(firstCentre?.id ?? '')
                }}>
                  {INDIA_STATES_AND_UTS.map((state) => <option key={state} value={state}>{state}</option>)}
                </select>
              </div>
              <div className="directory-field">
                <label htmlFor="india-district">2. District</label>
                <select id="india-district" value={selectedDistrict} disabled={districtsForState.length === 0} onChange={(event) => {
                  const nextDistrict = event.target.value
                  const firstCentre = centresForSelection.find((centre) => centre.district === nextDistrict) ?? INDIA_CENTRES.find((centre) => centre.state === selectedState && centre.district === nextDistrict)
                  setSelectedDistrict(nextDistrict)
                  setSelectedCentreId(firstCentre?.id ?? '')
                }}>
                  {districtsForState.length === 0 ? <option value="">No sourced districts loaded</option> : districtsForState.map((district) => <option key={district} value={district}>{district}</option>)}
                </select>
              </div>
              <div className="directory-field">
                <label htmlFor="india-centre">3. Mandi / procurement centre</label>
                <select id="india-centre" value={selectedCentreId} disabled={centresForSelection.length === 0} onChange={(event) => setSelectedCentreId(event.target.value)}>
                  {centresForSelection.length === 0 ? <option value="">No source-backed centre loaded for this district</option> : centresForSelection.map((centre) => <option key={centre.id} value={centre.id}>{centre.name}</option>)}
                </select>
              </div>
              <div className="directory-field">
                <label htmlFor="crop-choice">4. Commodity (demo selection)</label>
                <select id="crop-choice" value={crop} onChange={(event) => setCrop(event.target.value as Crop)}>
                  <option value="Paddy">Paddy</option>
                  <option value="Wheat">Wheat</option>
                  <option value="Mustard">Mustard</option>
                  <option value="Pulses">Pulses</option>
                  <option value="Other">Other / not specified</option>
                </select>
                <small>Commodity eligibility must be confirmed with the relevant state agency for the active season.</small>
              </div>
              <div className="directory-field">
                <label htmlFor="visit-date">5. Preferred visit date</label>
                <input id="visit-date" type="date" value={visitDate} onChange={(event) => setVisitDate(event.target.value)} />
                <small>Date is a demo input; no centre calendar is connected.</small>
              </div>
            </div>

            {selectedCentre ? (
              <div className="centre-source-card">
                <div className="centre-source-heading"><strong>{selectedCentre.name}</strong><span className={selectedCentre.recordStatus === 'official-tender-reference' ? 'source-pill source-current' : 'source-pill'}>{statusText}</span></div>
                <p>{selectedCentre.district}, {selectedCentre.state}{selectedCentre.pincode ? ` · PIN ${selectedCentre.pincode}` : ''}</p>
                {selectedCentre.address && <p>{selectedCentre.address}</p>}
                <p className="centre-agency">Record type: {selectedCentre.centreType}</p>
                <p className="centre-agency">Agency: {selectedCentre.agency ?? 'Not stated in source'}</p>
                <p className="centre-agency">Source: {selectedCentre.sourceName} · {selectedCentre.sourceDate}</p>
                {selectedCentre.commodity && <p className="centre-agency">Source commodity/season: {selectedCentre.commodity}</p>}
                <p className="source-caveat">{selectedCentre.verificationNote}</p>
                <a href={selectedCentre.sourceUrl} target="_blank" rel="noreferrer">View source record ↗</a>
              </div>
            ) : (
              <div className="directory-empty"><strong>No source-backed centre record loaded for {selectedState} yet.</strong><p>We are expanding coverage state by state. We will not substitute an unverified mandi or invent an address, agency or crop eligibility.</p></div>
            )}

            <div className="demo-notice"><strong>Demo mode only</strong><p>Choose a centre and date to continue. The next screen will show selectable illustrative time windows and a simulated confirmation. Nothing is sent to a government system.</p></div>
            <button className="button button-primary full-width" disabled={!selectedCentre || !visitDate} onClick={() => navigate('slots')}>Continue to slot preview <span>→</span></button>
            <p className="phone-legal">Real procurement bookings and live queue estimates remain disabled</p>
          </div>
          <div className="phone-home-indicator" />
        </section>
        <div className="farmer-explainer">
          <div className="explainer-card"><span className="explainer-number">01</span><div><h3>Choose your region</h3><p>The selector covers all Indian states and Union Territories. Source-backed physical centre records are added as they are verified.</p><span className="status-pill status-amber">{INDIA_CENTRES.length} records · {new Set(INDIA_CENTRES.map((centre) => centre.state)).size} states/UTs</span></div></div>
          <div className="explainer-card"><span className="explainer-number">02</span><div><h3>Check the source status</h3><p>Each centre carries its source, date and verification note. A market directory entry or tender reference is not proof of live operations.</p><span className="status-pill status-muted">Source tracked</span></div></div>
          <div className="explainer-card"><span className="explainer-number">03</span><div><h3>Preview a demonstration slot</h3><p>Choose a sample time window and confirm a local demo reservation. It will appear on the centre desk but will not be transmitted externally.</p><span className="status-pill status-muted">Simulated only</span></div></div>
          <div className="notice notice-green"><strong>Why no real booking?</strong><p>Centre authorization, active crop eligibility, current capacity, opening times and a live booking service have not been integrated. Aapurtikar keeps actual booking and live waiting-time APIs disabled.</p></div>
        </div>
      </div>
    </div>
  )
}

function SlotPreview({
  selectedState, selectedDistrict, selectedCentre, crop, visitDate, demoSlot, setDemoSlot, demoBooking, onConfirm,
}: {
  selectedState: string
  selectedDistrict: string
  selectedCentre: CentreRecord | undefined
  crop: Crop
  visitDate: string
  demoSlot: string
  setDemoSlot: (slot: string) => void
  demoBooking: DemoBooking | null
  onConfirm: (slot: string) => void
}) {
  const formattedDate = useMemo(() => {
    if (!visitDate) return 'Date not selected'
    const value = new Date(`${visitDate}T00:00:00`)
    return value.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
  }, [visitDate])
  const sampleSlots = ['09:00 – 10:00', '10:00 – 11:00', '11:00 – 12:00']
  return (
    <div className="page-content">
      <SectionHeading eyebrow="DEMONSTRATION SCHEDULING · NOT A LIVE INVENTORY" title="Choose an arrival window" intro="These illustrative time windows make the proposed workflow testable in a classroom demo. They are not published by the selected centre and do not reserve real capacity." />
      <div className="slot-progress"><span className="progress-done">1 <b>Location & crop</b></span><i /><span className="progress-current">2 <b>Choose window</b></span><i /><span className={demoBooking ? 'progress-done' : ''}>3 <b>Demo confirmation</b></span></div>
      <div className="slot-layout">
        <section className="panel slot-panel">
          <div className="panel-heading"><div><p className="eyebrow">YOUR VISIT DETAILS</p><h2>Selected location</h2></div><span className="round-icon">02</span></div>
          {selectedCentre ? (
            <div className="visit-summary">
              <div><small>CENTRE</small><strong>{selectedCentre.name}</strong><span>{selectedDistrict}, {selectedState}</span></div>
              <div><small>COMMODITY</small><strong>{crop}</strong><span>Farmer-selected demo input; eligibility not verified</span></div>
              <div><small>PREFERRED DATE</small><strong>{formattedDate}</strong><span>Not sent to the centre</span></div>
            </div>
          ) : <div className="directory-empty"><strong>No source-backed centre selected.</strong><p>Return to the farmer portal and choose one of the available directory records.</p></div>}
          <div className="slot-list-heading"><div><p className="eyebrow">ILLUSTRATIVE TIME WINDOWS</p><h2>Select one for the demo</h2></div><span className="status-pill status-muted">Sample values only</span></div>
          <div className="demo-slot-grid">
            {sampleSlots.map((slot, index) => (
              <button key={slot} className={demoSlot === slot ? 'demo-slot-card selected' : 'demo-slot-card'} onClick={() => setDemoSlot(slot)} disabled={!selectedCentre || !visitDate}>
                <span className="demo-slot-index">0{index + 1}</span><strong>{slot}</strong><small>{demoSlot === slot ? 'Selected for demo' : 'Illustrative window'}</small>
              </button>
            ))}
          </div>
          <div className="demo-notice"><strong>Important distinction</strong><p>The centre's real operating hours and capacity have not been supplied. The displayed windows are hard-coded teaching examples, not live availability.</p></div>
        </section>
        <aside className="slot-aside">
          <div className="panel slot-summary-card">
            <p className="eyebrow">DEMO RESERVATION</p>
            <div className="summary-lock">▣</div>
            <h2>{demoBooking ? 'Demo confirmed' : 'Ready to simulate?'}</h2>
            <p className="muted">{demoBooking ? 'A local-only demonstration record has been created in this page session.' : 'Select a time window, then create a simulated reservation for the classroom walkthrough.'}</p>
            <button className={demoSlot && selectedCentre && visitDate ? 'button button-primary full-width' : 'button button-disabled full-width'} disabled={!demoSlot || !selectedCentre || !visitDate} onClick={() => onConfirm(demoSlot)}>{demoBooking ? 'Create another demo reservation' : 'Confirm demo reservation'}</button>
            {demoBooking && (
              <div className="demo-confirmation">
                <span className="source-pill source-current">LOCAL DEMO ONLY</span>
                <strong>{demoBooking.reference}</strong>
                <p>{demoBooking.date} · {demoBooking.slot}</p>
                <p>{demoBooking.crop} · {demoBooking.district}, {demoBooking.state}</p>
                <small>Not transmitted, not stored in the backend, and not a government booking.</small>
              </div>
            )}
            <div className="summary-checks"><span><b>✓</b> Farmer selections carried forward</span><span><b>✓</b> Demo time window selected</span><span><b>–</b> Real centre capacity not connected</span></div>
          </div>
          <div className="panel mini-info"><strong>Live wait estimate</strong><span className="status-pill status-muted">Disabled</span><p>The Analytics page contains offline simulation results only, not a live estimate for the selected centre.</p></div>
        </aside>
      </div>
    </div>
  )
}

function CentreDesk({ navigate, demoBooking }: { navigate: (page: Page) => void; demoBooking: DemoBooking | null }) {
  const demoCentre = demoBooking ? INDIA_CENTRES.find((centre) => centre.id === demoBooking.centreId) : undefined
  return (
    <div className="page-content">
      <SectionHeading eyebrow="CENTRE DESK · SIMULATED WORKSPACE" title="Procurement centre desk" intro="This workspace shows how a centre team could review farmer appointments. Any reservation shown here was created in local demo mode, not received from a live procurement system." action={<span className="view-tag">LIVE OPERATIONS DISABLED</span>} />
      <div className="centre-dashboard">
        <aside className="admin-sidebar"><div className="admin-brand"><span>🌾</span><div><strong>Aapurtikar</strong><small>Centre management</small></div></div><div className="admin-nav-item active">▦ <span>Dashboard</span></div><div className="admin-nav-item">▣ <span>Demo reservations</span><em>Local only</em></div><div className="admin-nav-item">☷ <span>Queue & operations</span></div><div className="admin-nav-item">⌖ <span>Centres & capacity</span></div><div className="admin-nav-item">◷ <span>Scheduling policy</span></div><div className="admin-nav-item" onClick={() => navigate('analytics')}>▥ <span>Analytics & evaluation</span></div></aside>
        <div className="admin-main">
          <div className="admin-topbar"><div><small>SELECTED DIRECTORY CENTRE</small><strong>{demoCentre?.name ?? 'No demo centre selected'}</strong></div><span className="status-pill status-amber">Source status varies · no live feed</span></div>
          <div className="admin-welcome"><div><p className="eyebrow">CENTRE WORKSPACE PREVIEW</p><h2>Demo operations overview</h2><p>Use the Farmer portal to create a local demo reservation. It will appear here as a sample centre-side record.</p></div><div className="welcome-mark">🌱</div></div>
          <div className="admin-kpis">
            <KpiCard title="Demo reservations" value={demoBooking ? '1' : '0'} label="Local page-session record" tone="blue" />
            <KpiCard title="Live farmer check-ins" value="—" label="Not connected" tone="green" />
            <KpiCard title="Farmers served" value="—" label="No operational events" tone="purple" />
            <KpiCard title="Live average wait" value="—" label="Live estimate disabled" tone="orange" />
          </div>
          {demoBooking ? (
            <section className="panel demo-booking-record">
              <div className="panel-heading"><div><p className="eyebrow">SIMULATED FARMER ARRIVAL PLAN</p><h3>Demo reservation record</h3></div><span className="source-pill source-current">LOCAL DEMO ONLY</span></div>
              <div className="demo-booking-grid">
                <div><small>REFERENCE</small><strong>{demoBooking.reference}</strong></div>
                <div><small>CENTRE</small><strong>{demoCentre?.name ?? 'Selected centre'}</strong></div>
                <div><small>LOCATION</small><strong>{demoBooking.district}, {demoBooking.state}</strong></div>
                <div><small>COMMODITY</small><strong>{demoBooking.crop}</strong></div>
                <div><small>VISIT DATE</small><strong>{demoBooking.date}</strong></div>
                <div><small>DEMO TIME WINDOW</small><strong>{demoBooking.slot}</strong></div>
              </div>
              <p className="record-caveat">This record exists only in the current browser session. It was not saved to the database, transmitted to a procurement agency, or added to a real centre queue.</p>
            </section>
          ) : (
            <section className="panel no-chart-data demo-empty-state">
              <span className="chart-placeholder">▣</span><strong>No demo reservations yet</strong>
              <p>Open the Farmer portal, select a source-listed centre and date, then complete a demo reservation. The simulated record will appear here.</p>
              <button className="button button-primary" onClick={() => navigate('farmer')}>Start farmer demo →</button>
            </section>
          )}
          <div className="admin-content-grid">
            <section className="panel admin-chart-panel"><div className="panel-heading"><div><p className="eyebrow">LIVE WAITING TIME TREND</p><h3>Operational history</h3></div><span className="status-pill status-muted">No live feed</span></div><div className="no-chart-data"><span className="chart-placeholder">▥</span><strong>No operational observations connected</strong><p>Verified waiting time requires authorized check-in, service-start and completion events from a participating centre.</p></div></section>
            <section className="panel admin-queue-panel"><div className="panel-heading"><div><p className="eyebrow">LIVE QUEUE</p><h3>Queue status</h3></div><span className="status-pill status-muted">Disabled</span></div><div className="queue-row"><span>Currently waiting</span><strong>—</strong></div><div className="queue-row"><span>In service</span><strong>—</strong></div><div className="queue-row"><span>Next published slot</span><strong>—</strong></div><div className="notice"><p>Only local demo reservations are shown above. This is not a live centre queue.</p></div></section>
          </div>
          <div className="panel policy-panel"><div><p className="eyebrow">SCHEDULING POLICY</p><h3>Baseline vs proposed policy</h3><p>The evaluation compares unmanaged first-come-first-served (FCFS) with staggered appointment slots using generated demand.</p></div><div className="policy-choice"><span className="policy-radio" /> Unmanaged FCFS <small>Baseline</small></div><div className="policy-choice selected"><span className="policy-radio" /> 15-minute staggered slots <small>Simulation candidate</small></div><button className="button button-secondary" onClick={() => navigate('analytics')}>View research results →</button></div>
        </div>
      </div>
    </div>
  )
}

function KpiCard({ title, value, label, tone }: { title: string; value: string; label: string; tone: string }) {
  return <div className="admin-kpi"><span className={`kpi-icon ${tone}`}>◈</span><small>{title}</small><strong>{value}</strong><span>{label}</span></div>
}

function Analytics({ activeTab, setActiveTab }: { activeTab: 'simulation' | 'operational'; setActiveTab: (tab: 'simulation' | 'operational') => void }) {
  return (
    <div className="page-content">
      <SectionHeading eyebrow="ANALYTICS & EVALUATION" title="Evidence before assumptions" intro="The dashboard keeps real operational evidence separate from the offline simulation. Switch between them to see what is known and what is modelled." />
      <div className="analytics-tabs" role="tablist" aria-label="Analytics evidence type">
        <button role="tab" aria-selected={activeTab === 'simulation'} className={activeTab === 'simulation' ? 'active' : ''} onClick={() => setActiveTab('simulation')}>Offline simulation results</button>
        <button role="tab" aria-selected={activeTab === 'operational'} className={activeTab === 'operational' ? 'active' : ''} onClick={() => setActiveTab('operational')}>Real centre operations</button>
      </div>
      {activeTab === 'simulation' ? <SimulationResults /> : <OperationalUnavailable />}
    </div>
  )
}

function SimulationResults() {
  const best = benchmark.policies.find((policy) => policy.key === '15m')!
  return (
    <>
      <div className="simulation-disclaimer"><span className="disclaimer-icon">ⓘ</span><div><strong>Research simulation — not live procurement performance</strong><p>Public historical Punjab mandi arrivals provide the demand-volume profile. Farmer-level arrival events, service durations, appointment assignments and queue waits are synthetic assumptions.</p></div><span className="status-pill status-green">30 replays</span></div>
      <div className="benchmark-source-grid">
        <div className="source-card source-lead"><span className="source-icon">▤</span><div><small>PUBLIC INDIAN SOURCE</small><strong>Punjab potato mandi arrivals</strong><p>ICTD–IIT Delhi · November 2021 · Historical, not live</p></div></div>
        <SourceStat value={benchmark.source.marketDays.toLocaleString('en-IN')} label="Market-day records" />
        <SourceStat value={String(benchmark.source.markets)} label="Markets in Punjab" />
        <SourceStat value={`${benchmark.source.arrivalsTonnes.toLocaleString('en-IN', { maximumFractionDigits: 2 })} t`} label="Reported arrivals" />
      </div>
      <section className="panel market-profile-panel">
        <div className="panel-heading"><div><p className="eyebrow">OBSERVED SOURCE DATA · MARKET-LEVEL AGGREGATES</p><h2>Largest reported potato arrival volumes</h2><p>Top five Punjab markets by total reported arrivals during November 2021 · tonnes</p></div><span className="metric-unit-tag">TONNES</span></div>
        <div className="market-bars">{benchmark.topMarkets.map((market) => <div className="market-bar-row" key={market.name}><span>{market.name}</span><div className="market-bar-track"><div className="market-bar-fill" style={{ width: `${(market.arrivalsTonnes / benchmark.marketChartMax) * 100}%` }} /></div><strong>{market.arrivalsTonnes.toLocaleString('en-IN', { maximumFractionDigits: 1 })}</strong></div>)}</div>
      </section>
      <div className="result-highlight-grid">
        <div className="result-highlight"><small>MODELLED MEAN ON-SITE WAIT REDUCTION</small><strong>{benchmark.improvement.meanWaitReduction}%</strong><span>15-minute slots vs FCFS</span></div>
        <div className="result-highlight"><small>MODELLED P95 WAIT REDUCTION</small><strong>{benchmark.improvement.p95WaitReduction}%</strong><span>15-minute slots vs FCFS</span></div>
        <div className="result-highlight"><small>MEAN APPOINTMENT LEAD</small><strong>{(best.bookingLead ?? 0).toFixed(1)} min</strong><span>Generated arrival to assigned slot</span></div>
      </div>
      <section className="panel results-panel">
        <div className="panel-heading result-heading"><div><p className="eyebrow">POLICY COMPARISON</p><h2>On-site queue wait by scheduling policy</h2><p>Average metric across 30 Monte Carlo replications · 8 assumed service bays</p></div><span className="metric-unit-tag">MINUTES</span></div>
        <div className="bar-legend"><span><i className="legend-mean" /> Mean wait</span><span><i className="legend-p95" /> P95 wait</span></div>
        <div className="results-chart" role="img" aria-label="Bar chart comparing mean and 95th percentile queue waits for FCFS, hourly, 30-minute and 15-minute appointment policies">
          {benchmark.policies.map((policy) => <div className="bar-group" key={policy.key}><div className="bar-values"><strong>{policy.mean.toFixed(2)}</strong><span>{policy.p95.toFixed(2)}</span></div><div className="bar-pair"><div className="bar-track"><div className="bar-fill mean-fill" style={{ height: `${(policy.mean / benchmark.chartMax) * 100}%` }} /></div><div className="bar-track"><div className="bar-fill p95-fill" style={{ height: `${(policy.p95 / benchmark.chartMax) * 100}%` }} /></div></div><strong className="bar-label">{policy.label}</strong></div>)}
        </div>
        <div className="result-table-wrap"><table className="result-table"><thead><tr><th>Policy</th><th>Mean wait</th><th>P95 wait</th><th>Worst observed*</th><th>Scenario throughput**</th></tr></thead><tbody>{benchmark.policies.map((policy) => <tr key={policy.key} className={policy.key === '15m' ? 'recommended-row' : ''}><td><strong>{policy.label}</strong>{policy.key === '15m' && <span className="table-tag">Lowest modelled queue</span>}</td><td>{policy.mean.toFixed(2)} min</td><td>{policy.p95.toFixed(2)} min</td><td>{policy.worstObserved.toFixed(2)} min</td><td>{policy.throughput.toFixed(3)} / hour</td></tr>)}</tbody></table></div>
        <div className="tradeoff-note"><strong>Appointment trade-off:</strong> The 15-minute scenario has a 16.15-minute mean booking lead and a 17.78-minute mean time from the generated unplanned-arrival reference to service start, versus 8.84 minutes for FCFS. The on-site waiting reduction applies only after the scheduled check-in; the appointment must reach the farmer before travel.</div>
        <p className="chart-footnote">* Largest wait observed across the 30 simulated replications. ** Completed synthetic episodes per assumed market-open hour; scenario throughput, not actual centre throughput. P95−P5 is a distributional wait-spread proxy only (P5 = 0 in these runs), not a demographic or subgroup fairness result.</p>
      </section>
      <div className="assumption-grid">
        <div className="panel assumption-card"><p className="eyebrow">SYNTHETIC EVENT GENERATION</p><h3>How the farmer-level test stream was created</h3><ul><li><strong>{benchmark.synthetic.farmerEvents.toLocaleString('en-IN')}</strong> generated farmer visit events</li><li><strong>{benchmark.synthetic.lotSizeTonnes.toFixed(1)} tonnes</strong> assumed lot-size conversion threshold</li><li><strong>{benchmark.synthetic.serviceMeanMinutes} min</strong> mean synthetic service time; CV {benchmark.synthetic.serviceCv}</li><li><strong>{benchmark.synthetic.bays}</strong> assumed parallel service bays</li><li><strong>{benchmark.synthetic.window}</strong> arrivals · {benchmark.synthetic.intradayProfile}</li></ul></div>
        <div className="panel assumption-card"><p className="eyebrow">IMPORTANT INTERPRETATION</p><h3>What this result does — and does not — say</h3><p>It tests how policies behave under a fixed, India-grounded demand profile and stated assumptions. It does not prove that an actual Punjab procurement centre will reduce waiting time by the same percentage.</p><p>Capacity, crop eligibility, actual lot sizes, staff availability and service durations require field validation before deployment.</p></div>
      </div>
      <div className="source-citation"><strong>Source & provenance</strong><p>{benchmark.source.publisher}. “Commodity Analysis”, potato wholesale arrivals, Punjab, November 2021. <a href={benchmark.source.repositoryUrl} target="_blank" rel="noreferrer">Source repository ↗</a> · <a href={benchmark.source.rawUrl} target="_blank" rel="noreferrer">Original source file ↗</a></p><small>The inspected upstream repository did not include an explicit licence file. Attribution is retained; redistribution permission should be confirmed before publishing the cleaned source CSV.</small></div>
    </>
  )
}

function SourceStat({ value, label }: { value: string; label: string }) {
  return <div className="source-stat"><strong>{value}</strong><span>{label}</span></div>
}

function OperationalUnavailable() {
  return (
    <div className="operational-empty-layout">
      <section className="operational-empty panel"><span className="empty-illustration">⌁</span><p className="eyebrow">OPERATIONAL EVIDENCE</p><h2>No verified centre observations available</h2><p>Live waiting-time metrics are intentionally unavailable. The project has not received authorized check-in, service-start or completion records from an operational procurement centre.</p><div className="operational-stat-grid"><div><strong>—</strong><span>Mean wait</span></div><div><strong>—</strong><span>Worst observed wait</span></div><div><strong>—</strong><span>Throughput</span></div><div><strong>—</strong><span>Fairness spread</span></div></div></section>
      <aside className="panel operational-gates"><p className="eyebrow">REQUIRED BEFORE LIVE USE</p><h3>Operational readiness gates</h3>{['Centre participation and authority', 'Crop and season eligibility', 'Operating calendar and closures', 'Verified bay capacity and staffing', 'Service event and duration evidence', 'Approved booking and late-arrival rules', 'Privacy-reviewed data collection'].map((item, index) => <div className="gate-item" key={item}><span>{index + 1}</span><p>{item}</p><b>Pending</b></div>)}</aside>
    </div>
  )
}

export default App
