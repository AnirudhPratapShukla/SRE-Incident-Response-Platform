import React, { useEffect, useMemo, useState } from 'react'
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  Archive,
  ArrowRight,
  Bot,
  Check,
  CheckCircle2,
  ChevronRight,
  Cloud,
  CloudCog,
  Database,
  ExternalLink,
  Gauge,
  GitBranch,
  Globe2,
  HeartPulse,
  History,
  Layers3,
  LayoutDashboard,
  Loader2,
  LockKeyhole,
  Menu,
  MessageSquareText,
  Network,
  Play,
  RefreshCw,
  Search,
  Server,
  ShieldCheck,
  Sparkles,
  TerminalSquare,
  Ticket,
  UserCheck,
  X,
  XCircle,
  Zap,
} from 'lucide-react'
import { api, getApiUrl, setApiUrl } from './lib/api'

const DEMO_INCIDENT = {
  status: 'approval_required',
  thread_id: 'demo-thread-order-api',
  service: 'order-api',
  incident: 'The order-api service is returning HTTP 500 errors and requests are timing out.',
  incident_source: 'Manual Demo',
  aws_region: 'us-east-1',
  jira_issue_key: 'SRE-DEMO-42',
  jira_issue_url: 'https://shuklaanirudhpratap.atlassian.net/browse/SRE-42',
  jira_status: 'IN REVIEW',
  root_cause: 'Database connection pool exhaustion is causing request threads to wait until timeout, producing HTTP 500 responses.',
  supporting_evidence: 'Historical incident similarity: 83.4%. Current error rate: 35%. Latency: 4.8s. CPU: 92%. MCP context: EC2 fleet queried successfully.',
  impact: 'Order creation requests are failing and customer-facing latency is elevated.',
  safety_status: 'APPROVED',
  safety_recommendation: 'Controlled reboot is permitted only after explicit human approval.',
  risk_level: 'MEDIUM',
  approval: null,
  recommendation: 'Reboot the affected EC2 instance and verify recovery.',
  remediation_action: '',
  remediation_instance_id: '',
  execution_status: 'WAITING FOR HUMAN APPROVAL',
  verification_status: 'PENDING',
  verification_message: '',
  rollback_plan: 'If recovery is not observed, stop further automated action and investigate connection-pool configuration.',
  remediation_simulation_mode: true,
}

const NAV = [
  ['overview', 'Overview', LayoutDashboard],
  ['incidents', 'Incidents', AlertCircle],
  ['investigation', 'AI Investigation', Bot],
  ['remediation', 'Remediation', Zap],
  ['cloudwatch', 'CloudWatch', Cloud],
]

const WORKFLOW = [
  ['Monitoring', Activity],
  ['Logs', TerminalSquare],
  ['Infrastructure', Server],
  ['MCP AWS', CloudCog],
  ['RAG', Layers3],
  ['RCA', Search],
  ['Safety', ShieldCheck],
  ['Human Approval', UserCheck],
  ['Remediation', Zap],
  ['Verification', CheckCircle2],
]

function App() {
  const [page, setPage] = useState('overview')
  const [incident, setIncident] = useState(() => loadStoredIncident())
  const [incidents, setIncidents] = useState(() => {
    const saved = localStorage.getItem('sre_incidents')
    return saved ? JSON.parse(saved) : []
  })
  const [apiHealthy, setApiHealthy] = useState(false)
  const [checking, setChecking] = useState(false)
  const [demoMode, setDemoMode] = useState(false)
  const [showCreate, setShowCreate] = useState(false)
  const [toast, setToast] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    if (incident) localStorage.setItem('sre_active_incident', JSON.stringify(incident))
    else localStorage.removeItem('sre_active_incident')
  }, [incident])

  useEffect(() => {
    localStorage.setItem('sre_incidents', JSON.stringify(incidents.slice(0, 20)))
  }, [incidents])

  useEffect(() => {
    checkHealth()
  }, [])

  useEffect(() => {
    if (!toast) return
    const timer = setTimeout(() => setToast(null), 4200)
    return () => clearTimeout(timer)
  }, [toast])

  const active = incident || DEMO_INCIDENT
  const isApproval = active?.status === 'approval_required'
  const completed = active?.verification_status === 'VERIFIED'
  const liveData = incident && !demoMode

  const stats = useMemo(() => ({
    active: incident && incident.status !== 'completed' ? 1 : 0,
    approval: incident?.status === 'approval_required' ? 1 : 0,
    verified: incident?.verification_status === 'VERIFIED' ? 1 : 0,
    risk: incident?.risk_level || '€”',
  }), [incident])

  async function checkHealth() {
    setChecking(true)
    try {
      await api.health()
      setApiHealthy(true)
    } catch {
      setApiHealthy(false)
    } finally {
      setChecking(false)
    }
  }

  function loadDemo() {
    setDemoMode(true)
    setIncident(DEMO_INCIDENT)
    setPage('overview')
    setToast({ type: 'success', message: 'Demo incident loaded €” no backend action was executed.' })
  }

  function clearIncident() {
    setIncident(null)
    setDemoMode(false)
    setToast({ type: 'info', message: 'Active incident cleared from the dashboard.' })
  }

  function saveIncident(result, source = 'Live') {
    setDemoMode(false)
    setIncident(result)
    setIncidents((items) => [{ ...result, source }, ...items.filter((x) => x.thread_id !== result.thread_id)])
    setPage('overview')
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="brand">
          <div className="brand-mark"><SirenIcon /></div>
          <div>
            <strong>SRE Command</strong>
            <span>Incident Response</span>
          </div>
          <button className="mobile-close" onClick={() => setSidebarOpen(false)}><X size={18} /></button>
        </div>

        <div className="environment-pill">
          <span className={`pulse-dot ${apiHealthy ? 'green' : 'amber'}`} />
          <span>{apiHealthy ? 'LIVE BACKEND' : 'BACKEND OFFLINE'}</span>
          <span className="env-region">us-east-1</span>
        </div>

        <nav className="nav-list">
          {NAV.map(([key, label, Icon]) => (
            <button
              key={key}
              className={`nav-item ${page === key ? 'active' : ''}`}
              onClick={() => { setPage(key); setSidebarOpen(false) }}
            >
              <Icon size={18} />
              <span>{label}</span>
              {key === 'remediation' && isApproval && <span className="nav-alert">1</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-section-title">SYSTEM</div>
        <button className="nav-item" onClick={checkHealth}>
          <HeartPulse size={18} />
          <span>Health Check</span>
          {checking && <Loader2 size={14} className="spin" />}
        </button>
        <button className="nav-item" onClick={clearIncident}>
          <Archive size={18} />
          <span>Clear Workspace</span>
        </button>

        <div className="sidebar-footer">
          <div className="agent-orb"><Sparkles size={16} /></div>
          <div>
            <span>AI Ops Engine</span>
            <small>LangGraph + RAG + MCP</small>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setSidebarOpen(true)}><Menu size={22} /></button>
          <div className="breadcrumb"><span>Operations</span><ChevronRight size={14} /><strong>{pageLabel(page)}</strong></div>
          <div className="top-actions">
            <div className="api-status" onClick={checkHealth} title="Click to refresh API health">
              <span className={`status-dot ${apiHealthy ? 'green' : 'red'}`} />
              {apiHealthy ? 'API Connected' : 'API Offline'}
            </div>
            <button className="icon-btn" onClick={checkHealth} title="Refresh health"><RefreshCw size={17} className={checking ? 'spin' : ''} /></button>
            <button className="avatar">AS</button>
          </div>
        </header>

        <div className="content">
          {page === 'overview' && <OverviewPage active={active} incident={incident} stats={stats} demoMode={demoMode} onCreate={() => setShowCreate(true)} onDemo={loadDemo} onNavigate={setPage} />}
          {page === 'incidents' && <IncidentsPage incidents={incidents} active={incident} onSelect={(item) => { setIncident(item); setDemoMode(false); setPage('overview') }} onCreate={() => setShowCreate(true)} />}
          {page === 'investigation' && <InvestigationPage active={active} demoMode={demoMode} />}
          {page === 'remediation' && <RemediationPage active={active} liveData={liveData} demoMode={demoMode} onResult={saveIncident} onToast={setToast} />}
          {page === 'cloudwatch' && <CloudWatchPage onResult={saveIncident} onToast={setToast} />}
        </div>
      </main>

      {showCreate && <CreateIncidentModal onClose={() => setShowCreate(false)} onResult={saveIncident} onToast={setToast} />}
      {toast && <Toast toast={toast} onClose={() => setToast(null)} />}
    </div>
  )
}

function OverviewPage({ active, incident, stats, demoMode, onCreate, onDemo, onNavigate }) {
  const workflowState = getWorkflowState(active)
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow"><span className="eyebrow-dot" /> OPERATIONS CONTROL PLANE</div>
          <h1>Incident Command Center</h1>
          <p>Detect, investigate, approve and recover from production incidents.</p>
        </div>
        <div className="heading-actions">
          <button className="btn ghost" onClick={onDemo}><Play size={16} /> Load Demo</button>
          <button className="btn primary" onClick={onCreate}><Zap size={16} /> New Incident</button>
        </div>
      </div>

      {demoMode && <div className="demo-banner"><Sparkles size={17} /><div><strong>Demo preview active</strong><span>This scenario is local UI data. No AWS infrastructure or remediation API was touched.</span></div><button onClick={() => onNavigate('remediation')}>Open approval <ArrowRight size={15} /></button></div>}

      <section className="metric-grid">
        <MetricCard label="Active Incidents" value={stats.active} detail={stats.active ? '1 requires attention' : 'No active incident'} icon={AlertCircle} tone="red" />
        <MetricCard label="Human Approval" value={stats.approval} detail={stats.approval ? 'Action awaiting review' : 'No pending approval'} icon={UserCheck} tone="violet" />
        <MetricCard label="Verified Recoveries" value={stats.verified} detail={stats.verified ? 'Recovery confirmed' : 'No completed run'} icon={CheckCircle2} tone="green" />
        <MetricCard label="Current Risk" value={stats.risk} detail={stats.risk === 'MEDIUM' ? 'Controlled action' : 'Awaiting analysis'} icon={ShieldCheck} tone="amber" />
      </section>

      <section className="hero-grid">
        <div className="panel incident-hero">
          <PanelTitle icon={AlertTriangle} title="Active Incident" action={incident ? <button className="text-btn" onClick={() => onNavigate('investigation')}>Open investigation <ArrowRight size={14} /></button> : null} />
          {active ? <>
            <div className="incident-title-row">
              <div><span className="severity-badge">SEV-2</span><h2>{active.service || 'service'} <span>·</span> {active.incident_source || 'Manual'}</h2></div>
              <StatusBadge value={active.status === 'approval_required' ? 'IN REVIEW' : active.status} />
            </div>
            <p className="incident-description">{active.incident}</p>
            <div className="incident-meta">
              <Meta label="JIRA" value={active.jira_issue_key || 'Pending'} icon={Ticket} />
              <Meta label="REGION" value={active.aws_region || 'us-east-1'} icon={Globe2} />
              <Meta label="RISK" value={active.risk_level || '€”'} icon={ShieldCheck} />
              <Meta label="SOURCE" value={active.incident_source || 'Manual'} icon={Activity} />
            </div>
          </> : <EmptyState icon={CheckCircle2} title="No active incident" text="Start a live investigation or load the demo scenario." />}
        </div>

        <div className="panel health-panel">
          <PanelTitle icon={Gauge} title="System Health" action={<span className="live-label"><span className="pulse-dot green" /> LIVE</span>} />
          <div className="health-chart"><div className="chart-grid-lines" />{[30,44,38,62,54,68,59,78,70,86,73,91,80,94,88,96].map((v, i) => <div key={i} className="bar" style={{ height: `${v}%` }} />)}</div>
          <div className="health-values"><div><strong>99.98%</strong><span>Availability</span></div><div><strong>182ms</strong><span>P95 Latency</span></div><div><strong>0.4%</strong><span>Error Rate</span></div></div>
        </div>
      </section>

      <section className="panel workflow-panel">
        <PanelTitle icon={GitBranch} title="AI Investigation Pipeline" action={<span className="workflow-caption">CloudWatch †’ Jira †’ LangGraph †’ RAG †’ RCA †’ Safety †’ Approval †’ Remediation</span>} />
        <Workflow current={workflowState} />
      </section>

      <section className="lower-grid">
        <div className="panel">
          <PanelTitle icon={Bot} title="AI Root Cause Summary" action={active?.root_cause ? <button className="text-btn" onClick={() => onNavigate('investigation')}>View evidence <ArrowRight size={14} /></button> : null} />
          {active?.root_cause ? <div className="rca-preview"><div className="ai-badge"><Sparkles size={15} /> AI RCA</div><h3>{active.root_cause}</h3><p>{active.supporting_evidence || 'Evidence will appear after investigation.'}</p><div className="evidence-chips"><span><History size={13} /> RAG history</span><span><CloudCog size={13} /> MCP AWS</span><span><Activity size={13} /> Metrics</span></div></div> : <EmptyState icon={Bot} title="RCA not available" text="Start an incident to populate the investigation evidence." />}
        </div>
        <div className="panel">
          <PanelTitle icon={ShieldCheck} title="Safety Gate" />
          <div className="safety-card"><div className={`safety-icon ${active?.safety_status === 'APPROVED' ? 'ok' : 'pending'}`}>{active?.safety_status === 'APPROVED' ? <Check size={20} /> : <LockKeyhole size={19} />}</div><div><strong>{active?.safety_status || 'PENDING'}</strong><span>{active?.safety_recommendation || 'Safety analysis will run with the workflow.'}</span></div></div><div className="risk-row"><span>Risk level</span><RiskBadge value={active?.risk_level || '€”'} /></div></div>
      </section>
    </>
  )
}

function InvestigationPage({ active, demoMode }) {
  return (
    <>
      <PageIntro eyebrow="AI OPS" title="Investigation & Evidence" text="Follow the agent chain from raw signals to an evidence-backed root cause." />
      <div className="investigation-grid">
        <div className="panel timeline-panel"><PanelTitle icon={GitBranch} title="Agent Timeline" action={<span className="ai-badge"><Sparkles size={14} /> LangGraph</span>} /><DetailedWorkflow active={active} /></div>
        <div className="panel evidence-panel"><PanelTitle icon={Search} title="Root Cause Analysis" action={demoMode ? <span className="demo-chip">DEMO</span> : null} />{active?.root_cause ? <><div className="confidence"><div><span>AI confidence</span><strong>83.4%</strong></div><div className="confidence-track"><span /></div></div><div className="rca-block"><span className="label">ROOT CAUSE</span><h2>{active.root_cause}</h2></div><div className="rca-block"><span className="label">IMPACT</span><p>{active.impact || 'Impact assessment unavailable.'}</p></div><div className="rca-block"><span className="label">SUPPORTING EVIDENCE</span><p className="mono-text">{active.supporting_evidence || 'No evidence returned.'}</p></div></> : <EmptyState icon={Search} title="Waiting for investigation" text="Run an incident to populate the AI investigation." />}</div>
      </div>
      <div className="panel evidence-stream"><PanelTitle icon={Network} title="Evidence Sources" /><div className="source-grid"><SourceCard icon={Activity} title="Metrics" value="CPU 92% · Error rate 35% · Latency 4.8s" tone="blue" /><SourceCard icon={TerminalSquare} title="Application Logs" value="Database timeout / connection pool symptoms" tone="violet" /><SourceCard icon={History} title="RAG History" value="Historical similarity 83.4%" tone="amber" /><SourceCard icon={CloudCog} title="MCP AWS Context" value="EC2 + CloudWatch queried read-only" tone="green" /></div></div>
    </>
  )
}

function RemediationPage({ active, liveData, demoMode, onResult, onToast }) {
  const [action, setAction] = useState('reboot_ec2')
  const [instanceId, setInstanceId] = useState('i-0123456789abcdef0')
  const [simulation, setSimulation] = useState(true)
  const [busy, setBusy] = useState(false)

  const approve = async () => {
    if (!active?.thread_id || demoMode) {
      onToast({ type: 'success', message: 'Demo approval preview: remediation would run in SAFE DEMO SIMULATION mode.' })
      onResult({ ...DEMO_INCIDENT, status: 'completed', approval: 'yes', remediation_action: action, remediation_instance_id: instanceId, execution_status: 'EXECUTED - EC2 REBOOT VERIFIED THROUGH SAFE SIMULATION', verification_status: 'VERIFIED', verification_message: 'Safe demo simulation completed successfully. No AWS infrastructure was modified.', remediation_simulation_mode: true }, 'Demo')
      return
    }
    if (!instanceId.trim()) {
      onToast({ type: 'error', message: 'Enter an EC2 instance ID before approving.' })
      return
    }
    setBusy(true)
    try {
      const result = await api.approve(active.thread_id, { decision: 'yes', remediation_action: action, remediation_instance_id: instanceId.trim(), simulation_mode: simulation })
      onResult(result, 'Live')
      onToast({ type: 'success', message: 'Remediation workflow resumed successfully.' })
    } catch (error) {
      onToast({ type: 'error', message: error.message })
    } finally { setBusy(false) }
  }

  const reject = async () => {
    if (!active?.thread_id || demoMode) {
      onToast({ type: 'info', message: 'Demo rejection recorded locally.' })
      onResult({ ...DEMO_INCIDENT, status: 'completed', approval: 'no', execution_status: 'NOT EXECUTED', verification_status: 'PENDING' }, 'Demo')
      return
    }
    setBusy(true)
    try {
      const result = await api.approve(active.thread_id, { decision: 'no' })
      onResult(result, 'Live')
      onToast({ type: 'info', message: 'Remediation rejected. No action executed.' })
    } catch (error) { onToast({ type: 'error', message: error.message }) }
    finally { setBusy(false) }
  }

  const waiting = active?.status === 'approval_required'
  return (
    <>
      <PageIntro eyebrow="CONTROLLED ACTIONS" title="Human Approval & Remediation" text="No production action is executed without an explicit approval decision." />
      <div className="remediation-grid">
        <div className="panel approval-panel">
          <div className="approval-header"><div className="approval-lock"><LockKeyhole size={23} /></div><div><span className="label">GATED ACTION</span><h2>{waiting ? 'Remediation approval required' : active?.execution_status || 'No pending action'}</h2></div></div>
          <div className="approval-summary"><div><span>Service</span><strong>{active?.service || '€”'}</strong></div><div><span>Action</span><strong>EC2 Reboot</strong></div><div><span>Risk</span><RiskBadge value={active?.risk_level || 'MEDIUM'} /></div></div>
          <div className="form-section"><label>Target EC2 Instance ID</label><input value={instanceId} onChange={(e) => setInstanceId(e.target.value)} placeholder="i-0123456789abcdef0" disabled={!waiting || busy} /><small>For the current safe demo, a synthetic instance ID is sufficient.</small></div>
          <div className="simulation-toggle"><div className="toggle-copy"><Sparkles size={18} /><div><strong>Safe Demo Simulation</strong><span>No AWS infrastructure will be modified.</span></div></div><button className={`switch ${simulation ? 'on' : ''}`} onClick={() => setSimulation(!simulation)} disabled={!waiting || busy}><span /></button></div>
          {simulation && <div className="safe-callout"><ShieldCheck size={18} /><div><strong>SAFE DEMO MODE ENABLED</strong><span>Approval executes the remediation workflow through simulation only. Real EC2 reboot is not called.</span></div></div>}
          <div className="approval-actions"><button className="btn danger" onClick={reject} disabled={!waiting || busy}><XCircle size={17} /> Reject</button><button className="btn success" onClick={approve} disabled={!waiting || busy}>{busy ? <Loader2 size={17} className="spin" /> : <CheckCircle2 size={17} />} Approve & Execute</button></div>
        </div>
        <div className="panel remediation-result"><PanelTitle icon={Zap} title="Execution Result" />{active?.verification_status === 'VERIFIED' ? <div className="verified-state"><div className="verified-icon"><Check size={28} /></div><span className="label">RECOVERY VERIFIED</span><h2>Service recovery confirmed</h2><p>{active.verification_message || 'The controlled remediation and recovery verification completed successfully.'}</p><div className="result-pill"><CheckCircle2 size={15} /> {active.execution_status}</div></div> : <div className="waiting-state"><div className="radar"><span /><span /><span /></div><h3>{waiting ? 'Awaiting operator decision' : 'No remediation result yet'}</h3><p>Review the RCA, safety gate and target before executing the controlled action.</p></div>}<div className="rollback"><span className="label">ROLLBACK PLAN</span><p>{active?.rollback_plan || 'Rollback guidance will be generated with the remediation plan.'}</p></div></div>
      </div>
      {liveData && <div className="demo-warning"><AlertTriangle size={17} /><span>Live backend connected. Safe Demo Simulation is the default; switching it off can trigger the real controlled remediation path.</span></div>}
    </>
  )
}

function CloudWatchPage({ onResult, onToast }) {
  const [region, setRegion] = useState('us-east-1')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)

  async function scan() {
    setBusy(true)
    try {
      const data = await api.cloudwatchScan(region)
      setResult(data)
      if (data.incidents?.length) {
        const first = data.incidents[0]
        onResult({ ...first, aws_region: region }, 'CloudWatch')
        onToast({ type: 'success', message: `${data.incidents.length} incident(s) detected from CloudWatch.` })
      } else {
        onToast({ type: 'info', message: 'CloudWatch scan completed €” no active incidents detected.' })
      }
    } catch (error) { onToast({ type: 'error', message: error.message }) }
    finally { setBusy(false) }
  }

  return (
    <>
      <PageIntro eyebrow="AWS OBSERVABILITY" title="CloudWatch Signal Center" text="Scan AWS alarms and hand detected incidents to the incident-response workflow." />
      <div className="cloud-grid">
        <div className="panel scan-panel"><PanelTitle icon={Cloud} title="Incident Detection" /><div className="aws-visual"><div className="aws-ring"><Cloud size={38} /></div><div><span className="label">AWS REGION</span><h2>{region}</h2><p>Read-only CloudWatch discovery</p></div></div><div className="form-section"><label>Region</label><select value={region} onChange={(e) => setRegion(e.target.value)}><option>us-east-1</option><option>us-east-2</option><option>us-west-2</option><option>eu-west-1</option><option>ap-south-1</option></select></div><button className="btn primary wide" onClick={scan} disabled={busy}>{busy ? <Loader2 size={17} className="spin" /> : <Cloud size={17} />} Scan CloudWatch</button></div>
        <div className="panel cloud-result"><PanelTitle icon={Activity} title="Latest Scan" />{result ? <div className="scan-result"><div className={`scan-status ${result.incidents_detected ? 'alert' : 'ok'}`}>{result.incidents_detected ? <AlertCircle size={21} /> : <CheckCircle2 size={21} />}<div><strong>{result.incidents_detected ? `${result.incidents_detected} incident(s) detected` : 'No active incidents'}</strong><span>Region: {result.region}</span></div></div><pre>{JSON.stringify(result, null, 2)}</pre></div> : <EmptyState icon={CloudCog} title="No scan yet" text="Run a CloudWatch scan to populate the signal center." />}</div>
      </div>
    </>
  )
}

function IncidentsPage({ incidents, active, onSelect, onCreate }) {
  return (
    <>
      <PageIntro eyebrow="INCIDENT OPERATIONS" title="Incident Queue" text="Recent investigations and their current workflow state." action={<button className="btn primary" onClick={onCreate}><Zap size={16} /> New Incident</button>} />
      <div className="panel incident-table"><div className="table-head"><span>INCIDENT</span><span>SERVICE</span><span>JIRA</span><span>STATUS</span><span>RISK</span><span /></div>{incidents.length === 0 ? <EmptyState icon={Archive} title="No incidents stored" text="Create an incident or load the demo from Overview." /> : incidents.map((item) => <button className={`table-row ${active?.thread_id === item.thread_id ? 'selected' : ''}`} key={item.thread_id} onClick={() => onSelect(item)}><div><span className="severity-dot" /> <strong>{item.incident || 'Incident'}</strong><small>{item.thread_id?.slice(0, 18)}</small></div><span>{item.service || '€”'}</span><span>{item.jira_issue_key || '€”'}</span><StatusBadge value={item.status === 'approval_required' ? 'IN REVIEW' : item.status} /><RiskBadge value={item.risk_level || '€”'} /><ChevronRight size={17} /></button>)}</div>
    </>
  )
}

function CreateIncidentModal({ onClose, onResult, onToast }) {
  const [service, setService] = useState('order-api')
  const [description, setDescription] = useState('The order-api service is returning HTTP 500 errors and requests are timing out.')
  const [busy, setBusy] = useState(false)
  const [apiUrl, setUrl] = useState(getApiUrl())

  async function submit(e) {
    e.preventDefault()
    if (!service.trim() || !description.trim()) return onToast({ type: 'error', message: 'Service and incident description are required.' })
    setBusy(true)
    setApiUrl(apiUrl)
    try {
      const result = await api.createIncident({ service: service.trim(), incident: description.trim() })
      onResult(result, 'Manual')
      onToast({ type: 'success', message: result.status === 'approval_required' ? 'Investigation reached the human approval gate.' : 'Incident workflow completed.' })
      onClose()
    } catch (error) { onToast({ type: 'error', message: error.message }) }
    finally { setBusy(false) }
  }

  return <div className="modal-backdrop"><div className="modal"><div className="modal-head"><div><span className="label">LIVE WORKFLOW</span><h2>Create Incident</h2></div><button className="icon-btn" onClick={onClose}><X size={18} /></button></div><form onSubmit={submit}><div className="form-section"><label>Service</label><input value={service} onChange={(e) => setService(e.target.value)} /></div><div className="form-section"><label>Incident Description</label><textarea rows="5" value={description} onChange={(e) => setDescription(e.target.value)} /></div><div className="modal-note"><Bot size={17} /><span>Submitting starts CloudWatch/Jira-compatible incident processing through the existing FastAPI + LangGraph backend.</span></div><div className="modal-actions"><button type="button" className="btn ghost" onClick={onClose}>Cancel</button><button className="btn primary" disabled={busy}>{busy ? <Loader2 size={17} className="spin" /> : <Play size={17} />} Start Investigation</button></div></form></div></div>
}

function DetailedWorkflow({ active }) {
  const state = getWorkflowState(active)
  return <div className="detailed-flow">{WORKFLOW.map(([label, Icon], i) => { const status = state[i] || 'pending'; return <div className={`flow-step ${status}`} key={label}><div className="flow-icon">{status === 'done' ? <Check size={15} /> : status === 'active' ? <Icon size={15} /> : <Icon size={15} />}</div><div><strong>{label}</strong><span>{status === 'done' ? 'Completed' : status === 'active' ? 'In progress' : 'Waiting'}</span></div>{i < WORKFLOW.length - 1 && <div className={`flow-line ${status === 'done' ? 'done' : ''}`} />}</div> })}</div>
}

function Workflow({ current }) {
  return <div className="workflow-track">{WORKFLOW.map(([label, Icon], i) => <React.Fragment key={label}><div className={`workflow-node ${current[i] || 'pending'}`}><div className="workflow-icon">{current[i] === 'done' ? <Check size={15} /> : <Icon size={15} />}</div><span>{label}</span></div>{i < WORKFLOW.length - 1 && <div className={`workflow-connector ${current[i] === 'done' ? 'done' : ''}`} />}</React.Fragment>)}</div>
}

function getWorkflowState(active) {
  if (!active) return WORKFLOW.map(() => 'pending')
  if (active.verification_status === 'VERIFIED') return WORKFLOW.map(() => 'done')
  if (active.status === 'approval_required') return ['done','done','done','done','done','done','done','active','pending','pending']
  if (active.execution_status?.startsWith('EXECUTED')) return ['done','done','done','done','done','done','done','done','done','done']
  return ['done','done','done','done','done','done','done','pending','pending','pending']
}

function MetricCard({ label, value, detail, icon: Icon, tone }) { return <div className={`metric-card ${tone}`}><div className="metric-top"><span>{label}</span><div className="metric-icon"><Icon size={17} /></div></div><strong>{value}</strong><small>{detail}</small></div> }
function PanelTitle({ icon: Icon, title, action }) { return <div className="panel-title"><div><Icon size={17} /><h3>{title}</h3></div>{action}</div> }
function PageIntro({ eyebrow, title, text, action }) { return <div className="page-heading compact"><div><div className="eyebrow"><span className="eyebrow-dot" /> {eyebrow}</div><h1>{title}</h1><p>{text}</p></div>{action}</div> }
function StatusBadge({ value }) { const s = String(value || 'UNKNOWN').toUpperCase(); const cls = s.includes('REVIEW') || s.includes('APPROVAL') ? 'review' : s.includes('DONE') || s.includes('COMPLETE') ? 'done' : s.includes('ERROR') || s.includes('FAIL') ? 'fail' : 'neutral'; return <span className={`status-badge ${cls}`}><span />{s.replaceAll('_', ' ')}</span> }
function RiskBadge({ value }) { const v = String(value || '€”').toUpperCase(); return <span className={`risk-badge ${v.toLowerCase()}`}>{v}</span> }
function Meta({ label, value, icon: Icon }) { return <div className="meta"><Icon size={14} /><div><span>{label}</span><strong>{value}</strong></div></div> }
function EmptyState({ icon: Icon, title, text }) { return <div className="empty-state"><div className="empty-icon"><Icon size={22} /></div><h3>{title}</h3><p>{text}</p></div> }
function SourceCard({ icon: Icon, title, value, tone }) { return <div className={`source-card ${tone}`}><div className="source-icon"><Icon size={18} /></div><div><strong>{title}</strong><span>{value}</span></div></div> }
function Toast({ toast, onClose }) { return <div className={`toast ${toast.type}`}><div>{toast.type === 'success' ? <CheckCircle2 size={18} /> : toast.type === 'error' ? <AlertCircle size={18} /> : <Activity size={18} />}<span>{toast.message}</span></div><button onClick={onClose}><X size={15} /></button></div> }
function pageLabel(page) { return NAV.find((x) => x[0] === page)?.[1] || 'Overview' }
function loadStoredIncident() { try { const saved = localStorage.getItem('sre_active_incident'); return saved ? JSON.parse(saved) : null } catch { return null } }
function SirenIcon() { return <div className="siren-icon"><Zap size={19} /></div> }

export default App
