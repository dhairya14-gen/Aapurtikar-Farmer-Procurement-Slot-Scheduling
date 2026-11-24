import { useEffect, useMemo, useState, type ReactNode } from 'react'
import {
  apiPaths,
  getApi,
  type ApiHealth,
  type Loadable,
} from './api'
import { benchmark } from './researchData'

type Page = 'home' | 'farmer' | 'slots' | 'staff' | 'analytics'
type Crop = 'Paddy (Dhan)' | 'Wheat'

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
  const [crop, setCrop] = useState<Crop>('Paddy (Dhan)')
  const [visitDate, setVisitDate] = useState('')
  const [analyticsTab, setAnalyticsTab] = useState<'simulation' | 'operational'>('simulation')

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
          <div><span className="banner-pulse" /> ACADEMIC PROTOTYPE <b>·</b> SMART INDIA HACKATHON 2026 <b>·</b> KAPURTHALA, PUNJAB (PROPOSED)</div>
          <div className="banner-gates"><span>BOOKING DISABLED</span><span>NO LIVE QUEUE</span></div>
        </div>
        <ApiStatusBar health={health} />

        {page === 'home' && <Home navigate={navigate} />}
        {page === 'farmer' && <FarmerPortal navigate={navigate} crop={crop} setCrop={setCrop} visitDate={visitDate} setVisitDate={setVisitDate} />}
        {page === 'slots' && <SlotPreview crop={crop} visitDate={visitDate} />}
        {page === 'staff' && <CentreDesk navigate={navigate} />}
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

function FarmerPortal({ navigate, crop, setCrop, visitDate, setVisitDate }: { navigate: (page: Page) => void; crop: Crop; setCrop: (crop: Crop) => void; visitDate: string; setVisitDate: (date: string) => void }) {
  const [language, setLanguage] = useState<'English' | 'हिन्दी'>('English')
  return (
    <div className="page-content">
      <SectionHeading eyebrow="FARMER PORTAL · DEMONSTRATION VIEW" title="Plan a procurement visit" intro="A guided preview of the farmer journey. This prototype does not create an account, store personal details or reserve an arrival slot." action={<span className="view-tag">MOBILE-FRIENDLY VIEW</span>} />
      <div className="farmer-layout">
        <section className="phone-shell">
          <div className="phone-top"><span className="phone-camera" /><span> Aapurtikar <b>●</b></span><span>10:24</span></div>
          <div className="phone-content">
            <div className="phone-brand"><span className="phone-mark">अ</span><span><strong>Aapurtikar</strong><small>Farmer procurement portal</small></span><button className="language-toggle" onClick={() => setLanguage(language === 'English' ? 'हिन्दी' : 'English')}>{language === 'English' ? 'हिंदी' : 'EN'}</button></div>
            <div className="phone-hero"><span className="phone-hero-icon">🌾</span><p className="eyebrow">WELCOME FARMER</p><h2>{language === 'English' ? 'Your visit, better planned.' : 'आपकी यात्रा, बेहतर योजना।'}</h2><p>{language === 'English' ? 'Check the proposed centre and project crop scope before planning a visit.' : 'यात्रा की योजना से पहले प्रस्तावित केंद्र और फसल की जानकारी देखें।'}</p></div>
            <div className="phone-field-group"><label htmlFor="centre-choice">Proposed procurement centre</label><div className="phone-select static-select"><span>⌖</span><div><strong>CMS Kapurthala · New Dana Mandi</strong><small>Kapurthala, Punjab · Unverified</small></div></div></div>
            <div className="phone-field-group"><label htmlFor="crop-choice">Select crop (project scope)</label><select id="crop-choice" value={crop} onChange={(event) => setCrop(event.target.value as Crop)}><option>Paddy (Dhan)</option><option>Wheat</option></select><small className="field-hint">Centre-specific crop eligibility has not been authorized.</small></div>
            <div className="phone-field-group"><label htmlFor="visit-date">Preferred visit date (preview only)</label><input id="visit-date" type="date" value={visitDate} onChange={(event) => setVisitDate(event.target.value)} /></div>
            <div className="phone-status"><span className="status-icon">i</span><div><strong>Booking is not open</strong><small>Centre participation and operating capacity are still unverified.</small></div></div>
            <button className="button button-primary full-width" onClick={() => navigate('slots')}>Continue to slot preview <span>→</span></button>
            <p className="phone-legal">Academic prototype · No reservation will be created</p>
          </div>
          <div className="phone-home-indicator" />
        </section>
        <div className="farmer-explainer">
          <div className="explainer-card"><span className="explainer-number">01</span><div><h3>Find a proposed centre</h3><p>The current academic candidate is CMS Kapurthala, New Dana Mandi. It is not confirmed as a participating procurement centre.</p><span className="status-pill status-amber">Verification pending</span></div></div>
          <div className="explainer-card"><span className="explainer-number">02</span><div><h3>Check project crop scope</h3><p>Paddy and wheat are the crops covered by the project scope. Official procurement-season eligibility has not been supplied.</p><span className="status-pill status-amber">Eligibility unverified</span></div></div>
          <div className="explainer-card"><span className="explainer-number">03</span><div><h3>Preview the slot journey</h3><p>The next screen explains where appointment slots would appear after centre hours, capacity, staffing and rules are approved.</p><span className="status-pill status-muted">Preview only</span></div></div>
          <div className="notice notice-green"><strong>Why is booking disabled?</strong><p>We have no centre authorization or verified operating capacity. The prototype intentionally avoids accepting farmer bookings or displaying invented live waiting times.</p></div>
        </div>
      </div>
    </div>
  )
}

function SlotPreview({ crop, visitDate }: { crop: Crop; visitDate: string }) {
  const formattedDate = useMemo(() => {
    if (!visitDate) return 'Date not selected'
    const value = new Date(`${visitDate}T00:00:00`)
    return value.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
  }, [visitDate])
  return (
    <div className="page-content">
      <SectionHeading eyebrow="FUTURE BOOKING FLOW · PREVIEW ONLY" title="Choose an arrival slot" intro="This screen demonstrates the intended slot-selection step. The options are not available for booking because the centre has not supplied verified capacity or operating hours." />
      <div className="slot-progress"><span className="progress-done">1 <b>Centre & crop</b></span><i /><span className="progress-current">2 <b>Slot preview</b></span><i /><span>3 <b>Confirmation</b></span></div>
      <div className="slot-layout">
        <section className="panel slot-panel">
          <div className="panel-heading"><div><p className="eyebrow">YOUR VISIT DETAILS</p><h2>Proposed visit information</h2></div><span className="round-icon">02</span></div>
          <div className="visit-summary"><div><small>PROCUREMENT CENTRE</small><strong>CMS Kapurthala · New Dana Mandi</strong><span>Kapurthala, Punjab · Proposed / unverified</span></div><div><small>CROP</small><strong>{crop}</strong><span>Project scope only · eligibility unverified</span></div><div><small>PREFERRED DATE</small><strong>{formattedDate}</strong><span>Preview input, not a saved visit</span></div></div>
          <div className="slot-list-heading"><div><p className="eyebrow">ARRIVAL WINDOWS</p><h2>Slots are not published</h2></div><span className="status-pill status-muted">Capacity not configured</span></div>
          {['09:00 – 10:00', '10:00 – 11:00', '11:00 – 12:00'].map((slot) => <div className="slot-option disabled-slot" key={slot}><span className="radio-faux" /><strong>{slot}</strong><span className="slot-unavailable">Not published</span></div>)}
          <div className="notice"><strong>No appointment has been allocated.</strong><p>These rows are placeholders to illustrate the future layout. No live slot inventory or capacity is queried.</p></div>
        </section>
        <aside className="slot-aside">
          <div className="panel slot-summary-card"><p className="eyebrow">BOOKING SUMMARY</p><div className="summary-lock">▣</div><h2>Booking disabled</h2><p className="muted">An authorized centre must confirm participation, crop eligibility, operating calendar, bays, staffing and allocation rules before bookings can open.</p><button className="button button-disabled full-width" disabled>Confirm booking</button><div className="summary-checks"><span><b>✓</b> Project scope displayed</span><span><b>–</b> Centre authorization pending</span><span><b>–</b> Slot capacity unavailable</span></div></div>
          <div className="panel mini-info"><strong>Live wait estimate</strong><span className="status-pill status-muted">Disabled</span><p>Wait times in the Analytics section are offline simulation results, not a live estimate for this centre.</p></div>
        </aside>
      </div>
    </div>
  )
}

function CentreDesk({ navigate }: { navigate: (page: Page) => void }) {
  return (
    <div className="page-content">
      <SectionHeading eyebrow="ADMINISTRATOR PORTAL · DESKTOP VIEW" title="Procurement centre desk" intro="A centre-side operations workspace preview. It separates the planned workflow from real operations, which are not connected in this academic prototype." action={<span className="view-tag">OPERATIONS NOT ENABLED</span>} />
      <div className="centre-dashboard">
        <aside className="admin-sidebar"><div className="admin-brand"><span>🌾</span><div><strong>Aapurtikar</strong><small>Centre management</small></div></div><div className="admin-nav-item active">▦ <span>Dashboard</span></div><div className="admin-nav-item">▣ <span>Bookings</span><em>Disabled</em></div><div className="admin-nav-item">☷ <span>Queue & operations</span></div><div className="admin-nav-item">⌖ <span>Centres & capacity</span></div><div className="admin-nav-item">◷ <span>Scheduling policy</span></div><div className="admin-nav-item" onClick={() => navigate('analytics')}>▥ <span>Analytics & evaluation</span></div></aside>
        <div className="admin-main">
          <div className="admin-topbar"><div><small>PROPOSED CENTRE</small><strong>CMS Kapurthala · New Dana Mandi</strong></div><span className="status-pill status-amber">Unverified candidate</span></div>
          <div className="admin-welcome"><div><p className="eyebrow">CENTRE OPERATIONS OVERVIEW</p><h2>Operations readiness</h2><p>Required authorizations and service configuration must be completed before operational use.</p></div><div className="welcome-mark">🌱</div></div>
          <div className="admin-kpis">
            <KpiCard title="Live bookings" value="—" label="No operational records" tone="blue" />
            <KpiCard title="Farmer check-ins" value="—" label="Live check-in not connected" tone="green" />
            <KpiCard title="Farmers served" value="—" label="Service events unavailable" tone="purple" />
            <KpiCard title="Average wait" value="—" label="Live estimate disabled" tone="orange" />
          </div>
          <div className="admin-content-grid">
            <section className="panel admin-chart-panel"><div className="panel-heading"><div><p className="eyebrow">WAITING TIME TREND</p><h3>Operational history</h3></div><span className="status-pill status-muted">No data</span></div><div className="no-chart-data"><span className="chart-placeholder">▥</span><strong>No operational observations yet</strong><p>Verified waiting time will appear after authorized check-ins and service-start events are recorded.</p></div></section>
            <section className="panel admin-queue-panel"><div className="panel-heading"><div><p className="eyebrow">LIVE QUEUE</p><h3>Queue status</h3></div><span className="status-pill status-muted">Not connected</span></div><div className="queue-row"><span>Currently waiting</span><strong>—</strong></div><div className="queue-row"><span>In service</span><strong>—</strong></div><div className="queue-row"><span>Next slot</span><strong>—</strong></div><div className="notice"><p>Queue details are unavailable because no live centre event feed is connected.</p></div></section>
          </div>
          <div className="panel policy-panel"><div><p className="eyebrow">SCHEDULING POLICY</p><h3>Baseline vs proposed policy</h3><p>The evaluation compares unmanaged first-come-first-served (FCFS) with staggered appointment slots using equivalent generated demand.</p></div><div className="policy-choice"><span className="policy-radio" /> Unmanaged FCFS <small>Baseline</small></div><div className="policy-choice selected"><span className="policy-radio" /> 15-minute staggered slots <small>Simulation candidate</small></div><button className="button button-secondary" onClick={() => navigate('analytics')}>View research results →</button></div>
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
