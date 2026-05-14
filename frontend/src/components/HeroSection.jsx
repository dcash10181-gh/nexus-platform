import React, { useState, useEffect } from 'react'
import { Play, Info, Star, Clock, Brain } from 'lucide-react'

export default function HeroSection({ featured, onPlay, onInfo }) {
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setLoaded(true), 100)
    return () => clearTimeout(t)
  }, [])

  const c = featured
  const dna = c?.dna || {}
  const pacingLabel = dna.pacing < 0.35 ? 'Slow Burn' : dna.pacing < 0.6 ? 'Measured' : dna.pacing < 0.8 ? 'Propulsive' : 'Relentless'

  return (
    <section className="relative h-[88vh] min-h-[560px] overflow-hidden">
      {/* Backdrop */}
      <div className="absolute inset-0">
        <img
          src={c?.backdrop_url}
          alt=""
          className={`w-full h-full object-cover object-center transition-all duration-1000 ${
            loaded ? 'scale-100 opacity-100' : 'scale-105 opacity-0'
          }`}
          onError={e => { e.target.style.display = 'none' }}
        />
        {/* Gradient overlays */}
        <div className="absolute inset-0"
          style={{ background: 'linear-gradient(to right, rgba(8,8,15,0.95) 30%, rgba(8,8,15,0.4) 60%, transparent 80%)' }} />
        <div className="absolute inset-0"
          style={{ background: 'linear-gradient(to top, rgba(8,8,15,1) 0%, transparent 50%)' }} />
        {/* Cyan vignette left edge */}
        <div className="absolute left-0 top-0 bottom-0 w-1"
          style={{ background: 'linear-gradient(to right, rgba(0,212,255,0.3), transparent)' }} />
      </div>

      {/* Content */}
      <div className={`relative z-10 flex flex-col justify-end h-full px-6 md:px-10 lg:px-16 pb-20 pt-24 transition-all duration-700 ${
        loaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      }`}>

        {/* AI PICK badge */}
        <div className="flex items-center gap-2 mb-4">
          <span className="badge badge-cyan">
            <Brain size={10} /> AI CURATED
          </span>
          <span className="badge badge-magenta">{c?.kind?.toUpperCase()}</span>
        </div>

        {/* Title */}
        <h1 className="font-display text-5xl md:text-7xl font-800 text-nexus-text leading-none tracking-tight mb-3">
          {c?.title}
        </h1>

        {/* Meta row */}
        <div className="flex items-center gap-4 mb-4 text-sm text-nexus-subtext">
          <span className="flex items-center gap-1 text-nexus-amber">
            <Star size={12} fill="currentColor" /> {c?.rating?.toFixed(1)}
          </span>
          <span>{c?.year}</span>
          {dna.runtime_min && (
            <span className="flex items-center gap-1">
              <Clock size={12} /> {dna.runtime_min}m
            </span>
          )}
          <span className="text-nexus-cyan font-mono text-xs">{pacingLabel}</span>
          {c?.genres?.slice(0, 3).map(g => (
            <span key={g} className="text-nexus-subtext">{g}</span>
          ))}
        </div>

        {/* Synopsis */}
        <p className="max-w-xl text-nexus-subtext text-base leading-relaxed mb-6 line-clamp-3">
          {c?.synopsis}
        </p>

        {/* DNA mini-bar */}
        {dna.tension_curve?.length > 0 && (
          <div className="flex items-end gap-[2px] mb-6 h-8 w-40">
            {dna.tension_curve.map((v, i) => (
              <div key={i}
                className="flex-1 rounded-sm bg-nexus-cyan opacity-80 transition-all duration-500"
                style={{ height: `${v * 100}%`, animationDelay: `${i * 80}ms` }}
              />
            ))}
            <span className="ml-2 text-nexus-subtext text-xs font-mono self-end">tension</span>
          </div>
        )}

        {/* CTA buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={onPlay}
            className="flex items-center gap-2 px-7 py-3 rounded-xl font-display font-600 text-base
              bg-nexus-cyan text-nexus-bg hover:bg-nexus-cyan-dim
              transition-all duration-200 hover:scale-105 active:scale-95 glow-box-cyan"
          >
            <Play size={18} fill="currentColor" /> Watch Now
          </button>
          <button
            onClick={onInfo}
            className="flex items-center gap-2 px-6 py-3 rounded-xl font-display font-600 text-base
              text-nexus-text bg-white/10 hover:bg-white/15 border border-white/10
              transition-all duration-200 hover:scale-105 active:scale-95"
          >
            <Info size={18} /> Content DNA
          </button>
        </div>

        {/* AI reasoning ribbon */}
        <div className="mt-6 flex items-center gap-2 text-xs text-nexus-subtext">
          <Brain size={12} className="text-nexus-cyan" />
          <span className="font-mono">NEXUS matched this because you completed</span>
          <span className="text-nexus-text font-mono">Inception + 3 Denis Villeneuve titles</span>
        </div>
      </div>
    </section>
  )
}
