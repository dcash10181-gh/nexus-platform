import React, { useState, useEffect } from 'react'
import { Bell, Sparkles, ChevronDown, Wifi, WifiOff } from 'lucide-react'

const NAV_ITEMS = [
  { label: 'Home',      page: 'home' },
  { label: 'Series',    page: 'series' },
  { label: 'Films',     page: 'films' },
  { label: 'New & Hot', page: 'new-hot' },
  { label: 'My List',   page: 'my-list' },
  { label: 'Browse',    page: 'browse' },
  { label: 'Impact',    page: 'impact' },
]

export default function Navbar({ onAskNexus, apiConnected, currentPage = 'home', onNavigate }) {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', fn)
    return () => window.removeEventListener('scroll', fn)
  }, [])

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled ? 'bg-nexus-bg/95 backdrop-blur-md border-b border-nexus-border/50' : 'bg-transparent'
    }`}>
      <div className="px-6 md:px-10 lg:px-16 h-16 flex items-center justify-between">

        {/* Logo */}
        <div className="flex items-center gap-8">
          <button onClick={() => onNavigate?.('home')} className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-md flex items-center justify-center relative overflow-hidden"
              style={{ background: 'linear-gradient(135deg, #00d4ff 0%, #0074a8 100%)' }}>
              <span className="font-display font-800 text-white text-sm tracking-tighter">N</span>
            </div>
            <span className="font-display font-700 text-nexus-text text-xl tracking-tight">
              NEX<span className="text-nexus-cyan">US</span>
            </span>
          </button>

          {/* Nav links */}
          <div className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map(({ label, page, icon }) => (
              <button key={page} onClick={() => onNavigate?.(page)}
                className={`flex items-center text-sm px-3 py-1.5 rounded-lg transition-all duration-150 ${
                  currentPage === page
                    ? 'text-nexus-cyan bg-nexus-cyan/10'
                    : 'text-nexus-subtext hover:text-nexus-text hover:bg-white/5'
                }`}>
                {label}{icon}
              </button>
            ))}
          </div>
        </div>

        {/* Right controls */}
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-1.5 text-xs font-mono px-2.5 py-1 rounded-full ${
            apiConnected ? 'text-nexus-green bg-nexus-green/10 border border-nexus-green/20' : 'text-nexus-muted bg-white/5 border border-white/10'
          }`}>
            {apiConnected ? <Wifi size={10} /> : <WifiOff size={10} />}
            {apiConnected ? 'LIVE' : 'DEMO'}
          </div>

          <button onClick={onAskNexus}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 text-nexus-bg bg-nexus-cyan hover:bg-nexus-cyan-dim glow-box-cyan hover:scale-105 active:scale-95">
            <Sparkles size={14} />
            Ask Nexus
          </button>

          <button className="p-2 rounded-lg hover:bg-white/5 transition-colors text-nexus-subtext hover:text-nexus-text">
            <Bell size={18} />
          </button>

          <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-display font-600 text-nexus-bg"
            style={{ background: 'linear-gradient(135deg, #00d4ff, #ff0080)' }}>
            DC
          </div>
        </div>
      </div>

      {/* Mobile nav */}
      <div className="md:hidden flex gap-1 px-4 pb-2 overflow-x-auto">
        {NAV_ITEMS.map(({ label, page }) => (
          <button key={page} onClick={() => onNavigate?.(page)}
            className={`flex-none text-xs px-3 py-1.5 rounded-full transition-all ${
              currentPage === page ? 'text-nexus-cyan bg-nexus-cyan/10 border border-nexus-cyan/20' : 'text-nexus-subtext border border-nexus-border/40'
            }`}>{label}</button>
        ))}
      </div>
    </nav>
  )
}
