import React, { useEffect, useState } from 'react'
import { X, Brain, Play, Star } from 'lucide-react'

export default function ProactiveAlert({ recommendation, onDismiss, onViewContent }) {
  const [visible, setVisible] = useState(false)
  const content = recommendation?.content

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 100)
    return () => clearTimeout(t)
  }, [])

  // Bottom-RIGHT, not left: the hero's Watch Now / Content DNA buttons live at
  // bottom-left, and a left-anchored toast overlapped that primary CTA.
  // Right-anchored is also the conventional spot for an agent nudge.
  return (
    <div className={`fixed bottom-6 right-6 z-50 max-w-sm transition-all duration-500 ${
      visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
    }`}>
      <div className="bg-nexus-surface border border-nexus-border rounded-2xl shadow-2xl overflow-hidden
        glow-box-cyan">

        {/* AI badge strip */}
        <div className="h-0.5" style={{ background: 'linear-gradient(90deg, #00d4ff, #ff0080, #00d4ff)' }} />

        <div className="p-4">
          <div className="flex items-start gap-3">
            {/* Poster thumbnail */}
            {content?.poster_url && (
              <img src={content.poster_url} alt=""
                className="w-12 h-[72px] rounded-lg object-cover flex-none"
                onError={e => e.target.style.display = 'none'} />
            )}

            <div className="flex-1 min-w-0">
              {/* Header */}
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-1.5">
                  <Brain size={11} className="text-nexus-cyan" />
                  <span className="text-[10px] font-mono text-nexus-cyan uppercase tracking-wider">
                    NEXUS Agent · Right now
                  </span>
                </div>
                <button onClick={onDismiss}
                  className="p-1 rounded hover:bg-nexus-border/50 text-nexus-subtext hover:text-nexus-text transition-colors">
                  <X size={12} />
                </button>
              </div>

              <p className="text-nexus-text text-sm font-display font-600 leading-tight truncate">
                {recommendation?.push_notification?.body || `Watch ${content?.title} tonight`}
              </p>

              {content && (
                <p className="text-nexus-subtext text-xs mt-0.5 truncate">
                  {content.title} · {content.year} ·{' '}
                  <span className="flex items-center gap-0.5 inline-flex text-nexus-amber">
                    <Star size={9} fill="currentColor" /> {content.rating?.toFixed(1)}
                  </span>
                </p>
              )}

              {/* Reasoning */}
              {recommendation?.reasoning && (
                <p className="text-[10px] text-nexus-muted mt-1.5 leading-relaxed italic line-clamp-2">
                  "{recommendation.reasoning}"
                </p>
              )}

              {/* Action */}
              <button
                onClick={onViewContent}
                className="mt-3 flex items-center gap-1.5 text-xs font-medium
                  px-3 py-1.5 rounded-lg bg-nexus-cyan/10 text-nexus-cyan
                  border border-nexus-cyan/20 hover:bg-nexus-cyan/15 transition-all"
              >
                <Play size={11} fill="currentColor" /> Watch now
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
