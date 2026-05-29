import React, { useState } from 'react'
import { Star, Clock, Dna } from 'lucide-react'

const GENRE_FILTERS = ['All','Drama','Sci-Fi','Thriller','Comedy','Crime','Horror','Action','Romance','Fantasy','Animation','History','Documentary']

function ContentCard({ item, onClick, onDNAClick }) {
  const dna = item.dna || {}
  return (
    <div className="content-card cursor-pointer group" onClick={() => onClick(item)}>
      <div className="relative aspect-[2/3] rounded-xl overflow-hidden bg-nexus-card border border-nexus-border/60">
        <img src={item.poster_url} alt={item.title} className="w-full h-full object-cover" loading="lazy"
          onError={e => { e.target.src = `https://placehold.co/500x750/141420/00d4ff?text=${encodeURIComponent(item.title)}` }} />
        <div className="absolute inset-0 bg-nexus-bg/0 group-hover:bg-nexus-bg/40 transition-all duration-200" />
        <button className="absolute bottom-2 right-2 p-1.5 rounded-lg bg-nexus-bg/80 text-nexus-cyan opacity-0 group-hover:opacity-100 transition-all hover:bg-nexus-cyan hover:text-nexus-bg border border-nexus-cyan/30"
          onClick={e => { e.stopPropagation(); onDNAClick(item, e) }} title="Content DNA"><Dna size={12} /></button>
        <div className="absolute top-2 right-2 flex items-center gap-0.5 px-1.5 py-0.5 rounded-md bg-nexus-bg/80 text-nexus-amber text-[10px] font-mono">
          <Star size={9} fill="currentColor" />{item.rating?.toFixed(1)}
        </div>
      </div>
      <div className="mt-2 px-0.5">
        <h3 className="font-display text-sm font-600 text-nexus-text leading-tight truncate">{item.title}</h3>
        <div className="flex items-center justify-between mt-1">
          <span className="text-nexus-subtext text-xs">{item.year}</span>
          <div className="flex items-center gap-1">
            <div className="w-10 h-1 bg-nexus-border rounded-full overflow-hidden">
              <div className="h-full rounded-full" style={{ width: `${(dna.pacing||0.5)*100}%`, background: 'linear-gradient(90deg,#00d4ff,#00a3c4)' }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function BrowsePage({ title, subtitle, items, onCardClick, onDNAClick, showGenreFilter = false, emptyMessage }) {
  const [activeGenre, setActiveGenre] = useState('All')
  const [sortBy, setSortBy] = useState('rating')

  let filtered = activeGenre === 'All' ? items : items.filter(i => i.genres?.includes(activeGenre))

  filtered = [...filtered].sort((a, b) => {
    if (sortBy === 'rating') return (b.rating || 0) - (a.rating || 0)
    if (sortBy === 'year')   return (b.year || 0) - (a.year || 0)
    if (sortBy === 'title')  return a.title.localeCompare(b.title)
    return 0
  })

  return (
    <div className="pt-20 px-6 md:px-10 lg:px-16 pb-24 min-h-screen">
      {/* Page header */}
      <div className="mb-8">
        <h1 className="font-display font-700 text-4xl text-nexus-text">{title}</h1>
        {subtitle && <p className="text-nexus-subtext text-sm mt-1 font-mono">{subtitle}</p>}
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between mb-6 gap-4 flex-wrap">
        {showGenreFilter && (
          <div className="flex gap-2 flex-wrap">
            {GENRE_FILTERS.map(g => (
              <button key={g} onClick={() => setActiveGenre(g)}
                className={`text-xs px-3 py-1.5 rounded-full border transition-all ${
                  activeGenre === g
                    ? 'bg-nexus-cyan/15 text-nexus-cyan border-nexus-cyan/30'
                    : 'bg-nexus-surface text-nexus-subtext border-nexus-border/60 hover:border-nexus-cyan/20 hover:text-nexus-text'
                }`}>{g}</button>
            ))}
          </div>
        )}
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-nexus-muted text-xs font-mono">Sort:</span>
          {['rating','year','title'].map(s => (
            <button key={s} onClick={() => setSortBy(s)}
              className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
                sortBy === s ? 'bg-nexus-surface text-nexus-cyan border-nexus-cyan/30' : 'text-nexus-subtext border-nexus-border/40 hover:text-nexus-text'
              }`}>{s.charAt(0).toUpperCase()+s.slice(1)}</button>
          ))}
        </div>
      </div>

      {/* Count */}
      <p className="text-nexus-muted text-xs font-mono mb-6">{filtered.length} titles</p>

      {/* Grid */}
      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <p className="text-nexus-subtext text-lg">{emptyMessage || 'No titles found.'}</p>
          <p className="text-nexus-muted text-sm mt-2">Try a different filter or add titles to your list.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {filtered.map((item, i) => (
            <ContentCard key={item.id} item={item} onClick={onCardClick} onDNAClick={onDNAClick} />
          ))}
        </div>
      )}
    </div>
  )
}
