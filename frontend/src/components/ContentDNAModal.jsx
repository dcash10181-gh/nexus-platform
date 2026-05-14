/* ContentDNAModal.jsx — Full Content DNA fingerprint visualization */
import React from 'react'
import { X, Star, Clock, Zap, Music, Eye, Tag, Play } from 'lucide-react'

export function ContentDNAModal({ content, onClose }) {
  const dna = content?.dna || {}
  const curve = dna.tension_curve || []

  const maxY = 80
  const points = curve.map((v, i) => `${(i / (curve.length - 1)) * 220},${maxY - v * maxY}`).join(' ')

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-nexus-bg/85 backdrop-blur-md" onClick={onClose} />

      <div className="relative w-full max-w-2xl bg-nexus-surface border border-nexus-border rounded-2xl
        shadow-2xl overflow-hidden animate-fade-up">

        {/* Backdrop strip */}
        <div className="relative h-40 overflow-hidden">
          <img src={content?.backdrop_url} alt="" className="w-full h-full object-cover object-top" />
          <div className="absolute inset-0" style={{ background: 'linear-gradient(to bottom, transparent 20%, #0f0f1a 100%)' }} />
          <div className="absolute inset-0" style={{ background: 'linear-gradient(to right, rgba(8,8,15,0.6), transparent)' }} />
          <button onClick={onClose}
            className="absolute top-3 right-3 p-1.5 rounded-lg bg-nexus-bg/70 text-nexus-subtext hover:text-nexus-text transition-colors">
            <X size={16} />
          </button>
          {/* Title overlay */}
          <div className="absolute bottom-4 left-5">
            <h2 className="font-display font-700 text-2xl text-nexus-text">{content?.title}</h2>
            <div className="flex items-center gap-3 mt-1 text-xs text-nexus-subtext">
              <span className="flex items-center gap-1 text-nexus-amber"><Star size={10} fill="currentColor" /> {content?.rating?.toFixed(1)}</span>
              <span>{content?.year}</span>
              <span className="text-nexus-cyan font-mono">{content?.kind?.toUpperCase()}</span>
            </div>
          </div>
        </div>

        <div className="px-5 pb-5 grid grid-cols-2 gap-4 mt-2">
          {/* Left col */}
          <div className="space-y-4">
            {/* Tension Curve */}
            <div className="bg-nexus-card border border-nexus-border/60 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <Zap size={13} className="text-nexus-amber" />
                <span className="text-xs font-mono text-nexus-subtext uppercase tracking-wider">Tension Curve</span>
              </div>
              <svg viewBox="0 0 230 90" className="w-full">
                <defs>
                  <linearGradient id="tcGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#00d4ff" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#00d4ff" stopOpacity="0" />
                  </linearGradient>
                </defs>
                {curve.length > 1 && (
                  <>
                    <polygon
                      points={`0,${maxY} ${points} ${220},${maxY}`}
                      fill="url(#tcGrad)"
                    />
                    <polyline
                      points={points}
                      fill="none"
                      stroke="#00d4ff"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="spark-path"
                    />
                  </>
                )}
              </svg>
              <div className="flex justify-between text-[10px] font-mono text-nexus-muted mt-1">
                <span>ACT 1</span><span>ACT 2</span><span>ACT 3</span>
              </div>
            </div>

            {/* Pacing */}
            <div className="bg-nexus-card border border-nexus-border/60 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-nexus-subtext uppercase tracking-wider flex items-center gap-1.5">
                  <Clock size={12} className="text-nexus-cyan" /> Pacing
                </span>
                <span className="font-mono text-xs text-nexus-cyan">{Math.round((dna.pacing || 0) * 100)}%</span>
              </div>
              <div className="h-2 bg-nexus-border rounded-full overflow-hidden">
                <div className="h-full dna-bar rounded-full" style={{ width: `${(dna.pacing || 0) * 100}%` }} />
              </div>
              <div className="flex justify-between text-[9px] font-mono text-nexus-muted mt-1">
                <span>SLOW BURN</span><span>RELENTLESS</span>
              </div>
            </div>

            {/* Audio mood */}
            <div className="bg-nexus-card border border-nexus-border/60 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Music size={12} className="text-nexus-magenta" />
                <span className="text-xs font-mono text-nexus-subtext uppercase tracking-wider">Audio Mood</span>
              </div>
              <div className="badge badge-magenta text-sm">{dna.audio_mood || 'atmospheric'}</div>
            </div>
          </div>

          {/* Right col */}
          <div className="space-y-4">
            {/* Visual style */}
            <div className="bg-nexus-card border border-nexus-border/60 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Eye size={12} className="text-nexus-green" />
                <span className="text-xs font-mono text-nexus-subtext uppercase tracking-wider">Visual Style</span>
              </div>
              <div className="badge badge-green">{(dna.visual_style || 'cinematic').replace(/_/g, ' ')}</div>
            </div>

            {/* Thematic tags */}
            <div className="bg-nexus-card border border-nexus-border/60 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <Tag size={12} className="text-nexus-amber" />
                <span className="text-xs font-mono text-nexus-subtext uppercase tracking-wider">Thematic DNA</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {(dna.thematic_tags || []).map(tag => (
                  <span key={tag} className="badge badge-amber" style={{ fontSize: 10 }}>{tag}</span>
                ))}
              </div>
            </div>

            {/* Runtime */}
            <div className="bg-nexus-card border border-nexus-border/60 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Clock size={12} className="text-nexus-cyan" />
                <span className="text-xs font-mono text-nexus-subtext uppercase tracking-wider">Runtime</span>
              </div>
              <span className="font-display font-700 text-2xl text-nexus-text">{dna.runtime_min || '–'}</span>
              <span className="text-nexus-subtext text-sm ml-1">min</span>
              <p className="text-[10px] font-mono text-nexus-muted mt-1">
                {content?.kind === 'series' ? 'per episode' : 'total'}
              </p>
            </div>

            {/* Cast */}
            <div className="bg-nexus-card border border-nexus-border/60 rounded-xl p-4">
              <div className="text-xs font-mono text-nexus-subtext uppercase tracking-wider mb-2">Cast</div>
              <div className="space-y-1">
                {(content?.cast || []).slice(0, 3).map(name => (
                  <div key={name} className="text-nexus-text text-xs">{name}</div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Footer CTA */}
        <div className="px-5 pb-5">
          <button className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-display font-600 text-sm
            bg-nexus-cyan text-nexus-bg hover:bg-nexus-cyan-dim glow-box-cyan
            transition-all duration-200 hover:scale-[1.01] active:scale-[0.99]">
            <Play size={16} fill="currentColor" /> Watch {content?.title}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ContentDNAModal
