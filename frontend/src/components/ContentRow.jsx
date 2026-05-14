import React, { useRef } from 'react'
import { ChevronLeft, ChevronRight, Star, Dna, Brain, Eye, TrendingUp, Film } from 'lucide-react'

// ── Icon map for Signal icons ─────────────────────────────────────────────
const SIGNAL_ICONS = { brain: Brain, eye: Eye, 'trending-up': TrendingUp, film: Film }

// ── Content Card ──────────────────────────────────────────────────────────
function ContentCard({ item, onClick, onDNAClick, index }) {
  const dna = item.dna || {}
  const topSignal = item.signals?.[0]
  const TopIcon = topSignal ? (SIGNAL_ICONS[topSignal.icon] || Brain) : Brain

  return (
    <div
      className="content-card flex-none w-48 md:w-52 cursor-pointer group relative"
      style={{ animationDelay: `${index * 50}ms` }}
      onClick={() => onClick(item)}
    >
      {/* Poster */}
      <div className="relative aspect-[2/3] rounded-xl overflow-hidden bg-nexus-card border border-nexus-border/60">
        <img
          src={item.poster_url}
          alt={item.title}
          className="w-full h-full object-cover"
          loading="lazy"
          onError={e => { e.target.src = `https://placehold.co/500x750/141420/00d4ff?text=${encodeURIComponent(item.title)}` }}
        />

        {/* Hover overlay */}
        <div className="absolute inset-0 bg-nexus-bg/0 group-hover:bg-nexus-bg/40 transition-all duration-200" />

        {/* DNA button */}
        <button
          className="absolute bottom-2 right-2 p-1.5 rounded-lg bg-nexus-bg/80 text-nexus-cyan
            opacity-0 group-hover:opacity-100 transition-all duration-200
            hover:bg-nexus-cyan hover:text-nexus-bg border border-nexus-cyan/30"
          onClick={e => onDNAClick(item, e)}
          title="View Content DNA"
        >
          <Dna size={13} />
        </button>

        {/* Top signal badge */}
        {topSignal && (
          <div className="absolute top-2 left-2 flex items-center gap-1 px-1.5 py-0.5 rounded-md
            bg-nexus-bg/90 text-nexus-cyan text-[10px] font-mono border border-nexus-cyan/20
            opacity-0 group-hover:opacity-100 transition-all duration-200">
            <TopIcon size={9} />
            <span>{Math.round(topSignal.weight * 100)}%</span>
          </div>
        )}

        {/* Rating */}
        <div className="absolute top-2 right-2 flex items-center gap-0.5 px-1.5 py-0.5 rounded-md
          bg-nexus-bg/80 text-nexus-amber text-[10px] font-mono">
          <Star size={9} fill="currentColor" />
          {item.rating?.toFixed(1)}
        </div>
      </div>

      {/* Info below poster */}
      <div className="mt-2.5 px-0.5">
        <h3 className="font-display text-sm font-600 text-nexus-text leading-tight truncate">
          {item.title}
        </h3>
        <div className="flex items-center justify-between mt-1">
          <span className="text-nexus-subtext text-xs">{item.year}</span>
          {/* Pacing micro-bar */}
          <div className="flex items-center gap-1">
            <div className="w-12 h-1 bg-nexus-border rounded-full overflow-hidden">
              <div className="h-full dna-bar rounded-full" style={{ width: `${(dna.pacing || 0.5) * 100}%` }} />
            </div>
            <span className="text-[10px] font-mono text-nexus-muted">pace</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Content Row ───────────────────────────────────────────────────────────
export default function ContentRow({ title, subtitle, items, onCardClick, onDNAClick, badge }) {
  const rowRef = useRef(null)

  const scroll = (dir) => {
    rowRef.current?.scrollBy({ left: dir * 260, behavior: 'smooth' })
  }

  if (!items?.length) return null

  return (
    <section>
      {/* Row header */}
      <div className="flex items-end justify-between mb-4">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="font-display text-xl font-600 text-nexus-text">{title}</h2>
            {badge && <span className={`badge ${badge === 'NEW' ? 'badge-magenta' : badge === 'DNA MATCH' ? 'badge-green' : 'badge-cyan'}`}>{badge}</span>}
          </div>
          {subtitle && <p className="text-nexus-subtext text-xs mt-0.5 font-mono">{subtitle}</p>}
        </div>
        <div className="flex gap-1">
          <button onClick={() => scroll(-1)}
            className="p-1.5 rounded-lg bg-nexus-surface border border-nexus-border/60 text-nexus-subtext
              hover:text-nexus-cyan hover:border-nexus-cyan/30 transition-colors">
            <ChevronLeft size={16} />
          </button>
          <button onClick={() => scroll(1)}
            className="p-1.5 rounded-lg bg-nexus-surface border border-nexus-border/60 text-nexus-subtext
              hover:text-nexus-cyan hover:border-nexus-cyan/30 transition-colors">
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Row scroll container */}
      <div
        ref={rowRef}
        className="flex gap-3 overflow-x-auto pb-3 -mb-3 scrollbar-hide"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {items.map((item, i) => (
          <ContentCard
            key={item.id}
            item={item}
            onClick={onCardClick}
            onDNAClick={onDNAClick}
            index={i}
          />
        ))}
      </div>
    </section>
  )
}
