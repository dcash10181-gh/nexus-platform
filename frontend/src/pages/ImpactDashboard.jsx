import React, { useState, useEffect } from 'react'
import {
  TrendingUp, Users, Clock, Target, DollarSign, Activity,
  Zap, ArrowUpRight, ArrowDownRight, BarChart3, Brain
} from 'lucide-react'

// Animated counter
function useCountUp(target, duration = 1400) {
  const [val, setVal] = useState(0)
  useEffect(() => {
    let start = null
    const step = (ts) => {
      if (!start) start = ts
      const p = Math.min((ts - start) / duration, 1)
      const eased = 1 - Math.pow(1 - p, 3)
      setVal(target * eased)
      if (p < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }, [target, duration])
  return val
}

function MetricCard({ icon, label, value, suffix, prefix, delta, deltaUp, sub, accent }) {
  const animated = useCountUp(value)
  const display = Number.isInteger(value) ? Math.round(animated) : animated.toFixed(1)
  return (
    <div className="bg-nexus-surface border border-nexus-border rounded-2xl p-6 relative overflow-hidden group hover:border-nexus-cyan/30 transition-all">
      <div className="absolute top-0 right-0 w-32 h-32 rounded-full opacity-[0.06] blur-2xl transition-opacity group-hover:opacity-[0.12]"
        style={{ background: accent }} />
      <div className="flex items-center justify-between mb-4 relative">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `${accent}18`, color: accent }}>
          {icon}
        </div>
        {delta && (
          <div className={`flex items-center gap-1 text-xs font-mono px-2 py-1 rounded-full ${
            deltaUp ? 'text-nexus-green bg-nexus-green/10' : 'text-nexus-magenta bg-nexus-magenta/10'
          }`}>
            {deltaUp ? <ArrowUpRight size={11} /> : <ArrowDownRight size={11} />}{delta}
          </div>
        )}
      </div>
      <div className="font-display font-700 text-3xl text-nexus-text relative">
        {prefix}{display}{suffix}
      </div>
      <div className="text-nexus-subtext text-sm mt-1 relative">{label}</div>
      {sub && <div className="text-nexus-muted text-xs mt-2 font-mono relative">{sub}</div>}
    </div>
  )
}

// Simple SVG bar comparison
function ComparisonBar({ label, nexus, baseline, unit }) {
  const max = Math.max(nexus, baseline) * 1.15
  return (
    <div className="mb-5">
      <div className="flex justify-between items-baseline mb-2">
        <span className="text-nexus-text text-sm">{label}</span>
        <span className="text-nexus-cyan font-mono text-sm font-medium">+{Math.round((nexus/baseline - 1) * 100)}%</span>
      </div>
      <div className="space-y-1.5">
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-mono text-nexus-cyan w-16 flex-none">NEXUS</span>
          <div className="flex-1 h-6 bg-nexus-card rounded-md overflow-hidden">
            <div className="h-full rounded-md flex items-center justify-end px-2 transition-all duration-1000"
              style={{ width: `${(nexus/max)*100}%`, background: 'linear-gradient(90deg, #00d4ff, #0091b8)' }}>
              <span className="text-[10px] font-mono text-nexus-bg font-bold">{nexus}{unit}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-mono text-nexus-muted w-16 flex-none">Industry</span>
          <div className="flex-1 h-6 bg-nexus-card rounded-md overflow-hidden">
            <div className="h-full rounded-md flex items-center justify-end px-2 bg-nexus-border transition-all duration-1000"
              style={{ width: `${(baseline/max)*100}%` }}>
              <span className="text-[10px] font-mono text-nexus-subtext">{baseline}{unit}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ImpactDashboard() {
  return (
    <div className="pt-20 px-6 md:px-10 lg:px-16 pb-24 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 text-nexus-cyan text-xs font-mono mb-2">
          <Activity size={12} /> LIVE PLATFORM ANALYTICS · TRAILING 90 DAYS
        </div>
        <h1 className="font-display font-700 text-4xl text-nexus-text">Business Impact</h1>
        <p className="text-nexus-subtext text-sm mt-1">
          Measured lift versus the customer's previous recommendation system. Aggregated across pilot deployment.
        </p>
      </div>

      {/* Hero metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <MetricCard icon={<Clock size={18} />} label="Avg. watch time per session" value={47} suffix=" min"
          delta="+34%" deltaUp sub="vs 35 min baseline" accent="#00d4ff" />
        <MetricCard icon={<Target size={18} />} label="Recommendation click-through" value={31.4} suffix="%"
          delta="+218%" deltaUp sub="3.2× industry average" accent="#ff0080" />
        <MetricCard icon={<Users size={18} />} label="30-day retention" value={84} suffix="%"
          delta="+23%" deltaUp sub="vs 68% baseline" accent="#00ff94" />
        <MetricCard icon={<Zap size={18} />} label="Content completion rate" value={73} suffix="%"
          delta="+41%" deltaUp sub="finished what they started" accent="#ffb800" />
      </div>

      {/* Two columns: comparison + revenue */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
        {/* Comparison */}
        <div className="bg-nexus-surface border border-nexus-border rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-6">
            <BarChart3 size={16} className="text-nexus-cyan" />
            <h2 className="font-display font-600 text-nexus-text">NEXUS vs. Industry Standard</h2>
          </div>
          <ComparisonBar label="Engagement rate" nexus={31} baseline={10} unit="%" />
          <ComparisonBar label="Watch time / session" nexus={47} baseline={35} unit="m" />
          <ComparisonBar label="Discovery rate (new titles)" nexus={62} baseline={28} unit="%" />
          <ComparisonBar label="Session frequency / week" nexus={5} baseline={3} unit="x" />
        </div>

        {/* Revenue impact */}
        <div className="bg-nexus-surface border border-nexus-border rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-40 h-40 rounded-full opacity-[0.06] blur-3xl"
            style={{ background: '#00ff94' }} />
          <div className="flex items-center gap-2 mb-6 relative">
            <DollarSign size={16} className="text-nexus-green" />
            <h2 className="font-display font-600 text-nexus-text">Projected Annual Revenue Impact</h2>
          </div>
          <div className="relative space-y-5">
            <div>
              <div className="text-nexus-subtext text-sm">Churn reduction value</div>
              <div className="font-display font-700 text-2xl text-nexus-green">$8.4M</div>
              <div className="text-nexus-muted text-xs font-mono">23% fewer cancellations · 2M subscriber base</div>
            </div>
            <div>
              <div className="text-nexus-subtext text-sm">Increased engagement → ad revenue</div>
              <div className="font-display font-700 text-2xl text-nexus-green">$5.1M</div>
              <div className="text-nexus-muted text-xs font-mono">+34% watch time on ad-supported tier</div>
            </div>
            <div className="pt-4 border-t border-nexus-border">
              <div className="text-nexus-subtext text-sm">Total projected annual impact</div>
              <div className="font-display font-700 text-4xl text-nexus-text">$13.5M</div>
              <div className="text-nexus-cyan text-xs font-mono mt-1">54× return on $250K annual license</div>
            </div>
          </div>
        </div>
      </div>

      {/* Technical performance strip */}
      <div className="bg-nexus-surface border border-nexus-border rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-6">
          <Brain size={16} className="text-nexus-cyan" />
          <h2 className="font-display font-600 text-nexus-text">Technical Performance</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <div className="font-display font-700 text-2xl text-nexus-text">47<span className="text-base text-nexus-subtext">ms</span></div>
            <div className="text-nexus-subtext text-xs mt-1">p95 recommendation latency</div>
          </div>
          <div>
            <div className="font-display font-700 text-2xl text-nexus-text">12K<span className="text-base text-nexus-subtext">/s</span></div>
            <div className="text-nexus-subtext text-xs mt-1">peak requests handled</div>
          </div>
          <div>
            <div className="font-display font-700 text-2xl text-nexus-text">99.97<span className="text-base text-nexus-subtext">%</span></div>
            <div className="text-nexus-subtext text-xs mt-1">uptime SLA achieved</div>
          </div>
          <div>
            <div className="font-display font-700 text-2xl text-nexus-text">0<span className="text-base text-nexus-subtext"> keys</span></div>
            <div className="text-nexus-subtext text-xs mt-1">PII sent to third parties</div>
          </div>
        </div>
      </div>

      <p className="text-nexus-muted text-[10px] font-mono text-center mt-8">
        Figures illustrative of pilot deployment outcomes · Methodology available under NDA
      </p>
    </div>
  )
}
