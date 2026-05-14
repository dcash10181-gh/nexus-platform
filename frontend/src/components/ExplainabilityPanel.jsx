import React from 'react'
import { X, Brain, Eye, TrendingUp, Film, Sliders, Dna } from 'lucide-react'

const ICON_MAP = { brain: Brain, eye: Eye, 'trending-up': TrendingUp, film: Film }

export default function ExplainabilityPanel({ content, onClose, onViewDNA }) {
  const signals = content?.signals || []

  return (
    <div className="fixed right-0 top-0 bottom-0 z-40 flex items-center">
      {/* Panel */}
      <div className="w-80 h-full bg-nexus-surface border-l border-nexus-border flex flex-col
        shadow-2xl animate-fade-up overflow-y-auto">

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-nexus-border">
          <div>
            <div className="font-display font-600 text-nexus-text text-sm">Why this?</div>
            <div className="text-[10px] font-mono text-nexus-cyan">Explainability Panel</div>
          </div>
          <button onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-nexus-border/50 text-nexus-subtext transition-colors">
            <X size={15} />
          </button>
        </div>

        {/* Content title */}
        <div className="px-5 py-4 border-b border-nexus-border/50">
          <div className="flex gap-3 items-start">
            <img
              src={content?.poster_url}
              alt=""
              className="w-12 h-[72px] rounded-lg object-cover flex-none"
              onError={e => e.target.style.display = 'none'}
            />
            <div>
              <h3 className="font-display font-600 text-nexus-text text-sm leading-tight">{content?.title}</h3>
              <p className="text-nexus-subtext text-xs mt-0.5">{content?.year} · {content?.kind}</p>
              <div className="flex gap-1 mt-1.5 flex-wrap">
                {content?.genres?.slice(0,3).map(g => (
                  <span key={g} className="badge badge-cyan" style={{ fontSize: 9 }}>{g}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Match Score */}
        <div className="px-5 py-4 border-b border-nexus-border/50">
          <div className="flex items-center justify-between mb-1">
            <span className="text-nexus-subtext text-xs font-mono">NEXUS MATCH SCORE</span>
            <span className="font-display font-700 text-2xl text-nexus-cyan glow-cyan">
              {signals.length > 0 ? Math.round(signals[0].weight * 100) : 91}%
            </span>
          </div>
          <div className="h-1.5 bg-nexus-border rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{
                width: `${signals.length > 0 ? signals[0].weight * 100 : 91}%`,
                background: 'linear-gradient(90deg, #00d4ff, #00a3c4)',
              }}
            />
          </div>
          <p className="text-[10px] font-mono text-nexus-muted mt-1.5">
            Based on {signals.length} active signals from your profile
          </p>
        </div>

        {/* Signals */}
        <div className="px-5 py-4 flex-1">
          <div className="flex items-center gap-2 mb-3">
            <Brain size={12} className="text-nexus-cyan" />
            <span className="text-nexus-subtext text-xs font-mono uppercase tracking-wider">Active Signals</span>
          </div>

          <div className="space-y-3">
            {signals.map((signal, i) => {
              const Icon = ICON_MAP[signal.icon] || Brain
              return (
                <div key={i} className="bg-nexus-card border border-nexus-border/60 rounded-xl p-3 animate-fade-up"
                  style={{ animationDelay: `${i * 80}ms` }}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Icon size={12} className="text-nexus-cyan" />
                      <span className="text-nexus-text text-xs font-medium">{signal.name}</span>
                    </div>
                    <span className="font-mono text-xs text-nexus-cyan">{Math.round(signal.weight * 100)}%</span>
                  </div>
                  {/* Signal bar */}
                  <div className="h-1 bg-nexus-border rounded-full overflow-hidden mb-2">
                    <div
                      className="h-full dna-bar rounded-full transition-all duration-700"
                      style={{ width: `${signal.weight * 100}%`, transitionDelay: `${i * 100}ms` }}
                    />
                  </div>
                  <p className="text-nexus-muted text-[11px] leading-relaxed">{signal.detail}</p>
                </div>
              )
            })}
          </div>
        </div>

        {/* Actions */}
        <div className="px-5 pb-5 border-t border-nexus-border/50 pt-4 space-y-2">
          <button
            onClick={onViewDNA}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium
              bg-nexus-cyan/10 text-nexus-cyan border border-nexus-cyan/20
              hover:bg-nexus-cyan/15 transition-all duration-150"
          >
            <Dna size={14} /> View Full Content DNA
          </button>
          <button
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium
              text-nexus-subtext bg-nexus-border/30 border border-nexus-border/60
              hover:bg-nexus-border/50 transition-all duration-150"
          >
            <Sliders size={14} /> Adjust Signal Weights
          </button>
        </div>
      </div>
    </div>
  )
}
