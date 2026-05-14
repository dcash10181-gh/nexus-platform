import React, { useState, useEffect, useCallback } from 'react'
import { Key, Users, Database, Shield, RefreshCw, Plus, CheckCircle, AlertCircle, Copy, Server, Activity } from 'lucide-react'

const ADMIN_HEADER = 'nexus-admin-dev' // Replace with env var in production

async function adminFetch(path, opts = {}) {
  return fetch(`/api/v1/admin${path}`, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      'X-Nexus-Admin': ADMIN_HEADER,
      ...opts.headers,
    },
  })
}

// ── Stat Card ─────────────────────────────────────────────────────────────
function StatCard({ icon: Icon, label, value, color = 'cyan', sub }) {
  const colors = {
    cyan: 'text-nexus-cyan border-nexus-cyan/20 bg-nexus-cyan/5',
    magenta: 'text-nexus-magenta border-nexus-magenta/20 bg-nexus-magenta/5',
    green: 'text-nexus-green border-nexus-green/20 bg-nexus-green/5',
    amber: 'text-nexus-amber border-nexus-amber/20 bg-nexus-amber/5',
  }
  return (
    <div className={`border rounded-xl p-4 ${colors[color]}`}>
      <div className="flex items-center gap-2 mb-2">
        <Icon size={14} className="opacity-80" />
        <span className="text-xs font-mono opacity-70 uppercase tracking-wider">{label}</span>
      </div>
      <div className="font-display font-700 text-2xl">{value ?? '—'}</div>
      {sub && <div className="text-xs opacity-60 mt-1">{sub}</div>}
    </div>
  )
}

// ── Key Generator ─────────────────────────────────────────────────────────
function KeyGenerator({ onGenerated }) {
  const [tenantId, setTenantId] = useState('')
  const [tier, setTier] = useState('trial')
  const [label, setLabel] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const generate = async () => {
    if (!tenantId.trim()) { setError('Tenant ID is required'); return }
    setLoading(true); setError('')
    try {
      const r = await adminFetch('/keys/generate', {
        method: 'POST',
        body: JSON.stringify({ tenant_id: tenantId.trim(), tier, label }),
      })
      const data = await r.json()
      if (!r.ok) { setError(data.detail || 'Failed'); return }
      onGenerated(data)
      setTenantId(''); setLabel('')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-nexus-card border border-nexus-border rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <Key size={14} className="text-nexus-cyan" />
        <h3 className="font-display font-600 text-nexus-text text-sm">Issue New API Key</h3>
      </div>

      <div className="space-y-3">
        <div>
          <label className="text-xs font-mono text-nexus-subtext mb-1 block">Tenant ID</label>
          <input
            value={tenantId}
            onChange={e => setTenantId(e.target.value.toLowerCase().replace(/[^a-z0-9-_]/g, ''))}
            placeholder="acme-streaming"
            className="w-full bg-nexus-surface border border-nexus-border rounded-lg px-3 py-2 text-sm text-nexus-text font-mono"
          />
        </div>

        <div>
          <label className="text-xs font-mono text-nexus-subtext mb-1 block">Tier</label>
          <select
            value={tier}
            onChange={e => setTier(e.target.value)}
            className="w-full bg-nexus-surface border border-nexus-border rounded-lg px-3 py-2 text-sm text-nexus-text"
          >
            <option value="trial">Trial — 30 days / 1,000 users</option>
            <option value="commercial">Commercial — Annual, unlimited</option>
            <option value="enterprise">Enterprise — Perpetual, unlimited</option>
          </select>
        </div>

        <div>
          <label className="text-xs font-mono text-nexus-subtext mb-1 block">Label (optional)</label>
          <input
            value={label}
            onChange={e => setLabel(e.target.value)}
            placeholder="Production key — ACME Corp"
            className="w-full bg-nexus-surface border border-nexus-border rounded-lg px-3 py-2 text-sm text-nexus-text"
          />
        </div>

        {error && <p className="text-nexus-magenta text-xs">{error}</p>}

        <button
          onClick={generate}
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium
            bg-nexus-cyan text-nexus-bg hover:bg-nexus-cyan-dim transition-all disabled:opacity-50"
        >
          <Plus size={14} />
          {loading ? 'Generating…' : 'Generate Key'}
        </button>
      </div>
    </div>
  )
}

// ── Generated Key Display ─────────────────────────────────────────────────
function GeneratedKey({ data, onDismiss }) {
  const [copied, setCopied] = useState(false)

  const copy = () => {
    navigator.clipboard.writeText(data.api_key)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-nexus-green/5 border border-nexus-green/30 rounded-xl p-5">
      <div className="flex items-center gap-2 mb-3">
        <CheckCircle size={14} className="text-nexus-green" />
        <span className="text-nexus-green text-sm font-medium">Key generated — copy now, it won't be shown again</span>
      </div>
      <div className="flex items-center gap-2 bg-nexus-card rounded-lg px-3 py-2 font-mono text-xs text-nexus-text">
        <span className="flex-1 truncate">{data.api_key}</span>
        <button onClick={copy} className="text-nexus-cyan hover:text-nexus-text transition-colors flex-none">
          {copied ? <CheckCircle size={13} /> : <Copy size={13} />}
        </button>
      </div>
      {data.warning && (
        <p className="text-nexus-amber text-xs mt-2 flex items-center gap-1">
          <AlertCircle size={11} /> {data.warning}
        </p>
      )}
      <button onClick={onDismiss} className="mt-3 text-xs text-nexus-subtext hover:text-nexus-text">
        Dismiss
      </button>
    </div>
  )
}

// ── Main Admin Dashboard ──────────────────────────────────────────────────
export default function AdminDashboard() {
  const [health, setHealth]       = useState(null)
  const [license, setLicense]     = useState(null)
  const [tenants, setTenants]     = useState([])
  const [newKey, setNewKey]       = useState(null)
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState('')

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [healthR, licenseR, tenantsR] = await Promise.all([
        adminFetch('/health/deep').then(r => r.json()),
        adminFetch('/license').then(r => r.json()),
        adminFetch('/tenants').then(r => r.json()),
      ])
      setHealth(healthR)
      setLicense(licenseR)
      setTenants(tenantsR.tenants || [])
    } catch (e) {
      setError('Could not load admin data. Check X-Nexus-Admin header.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  return (
    <div className="min-h-screen bg-nexus-bg p-6 md:p-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display font-700 text-3xl text-nexus-text">
            NEX<span className="text-nexus-cyan">US</span> Admin
          </h1>
          <p className="text-nexus-subtext text-sm mt-1 font-mono">Platform management console</p>
        </div>
        <button onClick={loadData} disabled={loading}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-nexus-surface border border-nexus-border
            text-nexus-subtext hover:text-nexus-text text-sm transition-colors">
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-nexus-magenta/10 border border-nexus-magenta/30 rounded-xl text-nexus-magenta text-sm">
          {error}
        </div>
      )}

      {/* License banner */}
      {license && (
        <div className={`mb-6 p-4 rounded-xl border flex items-center justify-between ${
          license.valid ? 'bg-nexus-green/5 border-nexus-green/20' : 'bg-nexus-magenta/5 border-nexus-magenta/20'
        }`}>
          <div className="flex items-center gap-2">
            <Shield size={14} className={license.valid ? 'text-nexus-green' : 'text-nexus-magenta'} />
            <span className="font-mono text-sm">
              <span className={license.valid ? 'text-nexus-green' : 'text-nexus-magenta'}>
                {license.tier.toUpperCase()}
              </span>
              {' · '}{license.licensee}
              {license.expires_at && (
                <span className="text-nexus-subtext ml-2">
                  expires {new Date(license.expires_at * 1000).toLocaleDateString()}
                </span>
              )}
            </span>
          </div>
          {license.ui_watermark && (
            <span className="badge badge-amber text-[10px]">Trial Mode</span>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left col — stats + health */}
        <div className="lg:col-span-2 space-y-6">
          {/* Service health */}
          {health && (
            <div className="bg-nexus-surface border border-nexus-border rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <Activity size={14} className="text-nexus-cyan" />
                <h3 className="font-display font-600 text-nexus-text text-sm">Service Health</h3>
                <span className={`badge text-[10px] ml-auto ${health.overall === 'ok' ? 'badge-green' : 'badge-magenta'}`}>
                  {health.overall?.toUpperCase()}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-3">
                {['qdrant', 'neo4j', 'llm'].map(svc => {
                  const s = health[svc] || {}
                  return (
                    <div key={svc} className={`rounded-lg p-3 border ${
                      s.status === 'ok' ? 'border-nexus-green/20 bg-nexus-green/5' : 'border-nexus-magenta/20 bg-nexus-magenta/5'
                    }`}>
                      <div className="flex items-center gap-1.5 mb-1">
                        <div className={`w-1.5 h-1.5 rounded-full ${s.status === 'ok' ? 'bg-nexus-green' : 'bg-nexus-magenta'}`} />
                        <span className="font-mono text-[11px] text-nexus-subtext uppercase">{svc}</span>
                      </div>
                      <div className="text-nexus-text text-xs">
                        {svc === 'qdrant' && s.vectors !== undefined && `${s.vectors} vectors`}
                        {svc === 'neo4j' && s.content_count !== undefined && `${s.content_count} nodes`}
                        {svc === 'llm' && s.provider && s.provider}
                        {s.status === 'error' && <span className="text-nexus-magenta">error</span>}
                      </div>
                    </div>
                  )
                })}
              </div>
              <p className="text-nexus-muted text-[10px] font-mono mt-3">
                Latency: {health.latency_ms}ms
              </p>
            </div>
          )}

          {/* Tenants table */}
          <div className="bg-nexus-surface border border-nexus-border rounded-xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <Users size={14} className="text-nexus-cyan" />
              <h3 className="font-display font-600 text-nexus-text text-sm">Tenants</h3>
              <span className="ml-auto text-nexus-subtext text-xs font-mono">{tenants.length} registered</span>
            </div>
            {tenants.length === 0 ? (
              <p className="text-nexus-muted text-sm text-center py-4">No tenants yet. Generate a key to create one.</p>
            ) : (
              <div className="space-y-2">
                {tenants.map(t => (
                  <div key={t.id} className="flex items-center justify-between py-2 border-b border-nexus-border/40 last:border-0">
                    <div>
                      <div className="font-mono text-sm text-nexus-text">{t.id}</div>
                      <div className="text-nexus-subtext text-xs">{t.name}</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`badge text-[10px] ${
                        t.tier === 'enterprise' ? 'badge-amber' :
                        t.tier === 'commercial' ? 'badge-cyan' : 'badge-green'
                      }`}>{t.tier}</span>
                      <div className="text-right">
                        <div className="text-nexus-subtext text-xs">{t.catalog_size} titles</div>
                        <div className="text-nexus-subtext text-xs">{t.user_count} users</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right col — key generator */}
        <div className="space-y-4">
          {newKey ? (
            <GeneratedKey data={newKey} onDismiss={() => { setNewKey(null); loadData() }} />
          ) : (
            <KeyGenerator onGenerated={data => { setNewKey(data); loadData() }} />
          )}

          {/* License stats */}
          {license && (
            <div className="grid grid-cols-2 gap-3">
              <StatCard icon={Server} label="Tenant Cap" value={license.tenant_cap}
                color="cyan" sub={`${tenants.length} used`} />
              <StatCard icon={Users} label="User Cap" value={license.user_cap ?? '∞'}
                color={license.is_trial ? 'amber' : 'green'} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
