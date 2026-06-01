import React, { useState, useEffect, useCallback } from 'react'
import { HashRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import HeroSection from './components/HeroSection.jsx'
import ContentRow from './components/ContentRow.jsx'
import AskNexus from './components/AskNexus.jsx'
import MOCK_CONTENT from './data/catalog.js'
import ProactiveAlert from './components/ProactiveAlert.jsx'
import ExplainabilityPanel from './components/ExplainabilityPanel.jsx'
import ContentDNAModal from './components/ContentDNAModal.jsx'
import BrowsePage from './pages/BrowsePage.jsx'
import ImpactDashboard from './pages/ImpactDashboard.jsx'
import AdminDashboard from './pages/AdminDashboard.jsx'

// Proactive recommendation. Anchored to a single real catalog title looked up
// by id (NOT a positional index — index drift was how the copy and content got
// out of sync: the text said "Severance" while content was MOCK_CONTENT[0] = The
// Wire). Copy is written to match THIS title's actual DNA (Mindhunter is a
// genuine slow-burn psychological thriller), so the card never lies.
const PROACTIVE_TITLE = MOCK_CONTENT.find(c => c.id === 'mindhunter-s1-2017') || MOCK_CONTENT[0]
const PROACTIVE_REC = {
  title: 'Perfect for tonight',
  content: PROACTIVE_TITLE,
  reasoning: `It's Friday evening. ${PROACTIVE_TITLE.title} matches your slow-burn psychological pattern exactly.`,
  push_notification: { body: `${PROACTIVE_TITLE.title} is calling your name tonight ✦` },
}

// Saved list state (persisted in sessionStorage for demo)
function getMyList() {
  try { return JSON.parse(sessionStorage.getItem('nexus_mylist') || '[]') } catch { return [] }
}
function saveMyList(ids) {
  try { sessionStorage.setItem('nexus_mylist', JSON.stringify(ids)) } catch {}
}

export default function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="*" element={<MainApp />} />
      </Routes>
    </HashRouter>
  )
}

function MainApp() {
  const [currentPage, setCurrentPage]         = useState('home')
  const [selectedContent, setSelectedContent] = useState(null)
  const [showDNA, setShowDNA]                 = useState(false)
  const [showAskNexus, setShowAskNexus]       = useState(false)
  const [showProactive, setShowProactive]     = useState(false)
  const [apiConnected, setApiConnected]       = useState(false)
  const [myListIds, setMyListIds]             = useState(getMyList)

  useEffect(() => { const t = setTimeout(() => setShowProactive(true), 4000); return () => clearTimeout(t) }, [])
  useEffect(() => { fetch('/api/health').then(r => r.ok && setApiConnected(true)).catch(() => {}) }, [])

  const handleCardClick = useCallback((item) => { setSelectedContent(item); setShowDNA(false) }, [])
  const handleShowDNA   = useCallback((item, e) => { e?.stopPropagation(); setSelectedContent(item); setShowDNA(true) }, [])

  const toggleMyList = (id) => {
    setMyListIds(prev => {
      const updated = prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
      saveMyList(updated)
      return updated
    })
  }

  const myListItems = MOCK_CONTENT.filter(c => myListIds.includes(c.id))

  const series    = MOCK_CONTENT.filter(c => c.kind === 'series' || c.kind === 'limited')
  const films     = MOCK_CONTENT.filter(c => c.kind === 'film')
  const newAndHot = [...MOCK_CONTENT].filter(c => c.year >= 2021).sort((a,b) => b.year - a.year)

  const renderPage = () => {
    switch (currentPage) {
      case 'series':
        return <BrowsePage title="Series" subtitle="Long-form storytelling · All series and limited runs" items={series} onCardClick={handleCardClick} onDNAClick={handleShowDNA} showGenreFilter />
      case 'films':
        return <BrowsePage title="Films" subtitle="Cinema · Feature films across all genres" items={films} onCardClick={handleCardClick} onDNAClick={handleShowDNA} showGenreFilter />
      case 'new-hot':
        return <BrowsePage title="New & Hot" subtitle="Released 2021 and later · Sorted by year" items={newAndHot} onCardClick={handleCardClick} onDNAClick={handleShowDNA} showGenreFilter />
      case 'my-list':
        return <BrowsePage title="My List" subtitle="Titles you've saved" items={myListItems} onCardClick={handleCardClick} onDNAClick={handleShowDNA} emptyMessage="Your list is empty — browse titles and save them here." />
      case 'impact':
        return <ImpactDashboard />
      case 'browse':
        return <BrowsePage title="Browse All" subtitle="Complete catalog · 98 titles" items={MOCK_CONTENT} onCardClick={handleCardClick} onDNAClick={handleShowDNA} showGenreFilter />
      default:
        // Pass the active selection so the hero reflects whatever the user
        // picked (via Ask Nexus, a card, or the proactive alert). Falls back
        // to the default featured title when nothing is selected.
        return <HomePage items={MOCK_CONTENT} selectedContent={selectedContent} onCardClick={handleCardClick} onDNAClick={handleShowDNA} myListIds={myListIds} toggleMyList={toggleMyList} />
    }
  }

  return (
    <div className="min-h-screen bg-nexus-bg relative overflow-x-hidden">
      {/* Ambient blobs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full opacity-[0.04]" style={{ background:'radial-gradient(circle, #00d4ff 0%, transparent 70%)' }} />
        <div className="absolute bottom-[-10%] right-[-5%] w-[500px] h-[500px] rounded-full opacity-[0.03]" style={{ background:'radial-gradient(circle, #ff0080 0%, transparent 70%)' }} />
      </div>

      <Navbar onAskNexus={() => setShowAskNexus(true)} apiConnected={apiConnected} currentPage={currentPage} onNavigate={setCurrentPage} />

      <main className="relative z-10">{renderPage()}</main>

      <AskNexus isOpen={showAskNexus} onClose={() => setShowAskNexus(false)} onContentSelect={(item) => {
        // "Open it" means: surface the title on the main page, ready to watch.
        // Select it (drives the hero via HomePage) and close the chat. We do
        // NOT force the DNA modal here — that contradicted the "Opening X now"
        // copy and was the source of the stale-hero confusion. Jump home so the
        // hero is visible even if the user was on a sub-page.
        setSelectedContent(item)
        setShowDNA(false)
        setCurrentPage('home')
        setShowAskNexus(false)
      }} allContent={MOCK_CONTENT} />

      {showProactive && currentPage === 'home' && (
        <ProactiveAlert recommendation={PROACTIVE_REC} onDismiss={() => setShowProactive(false)} onViewContent={() => {
          // "Watch now" = land on the title's hero, consistent with Ask Nexus
          // "open it". Don't force the DNA modal (the button doesn't say "DNA").
          setSelectedContent(PROACTIVE_REC.content)
          setShowDNA(false)
          setShowProactive(false)
        }} />
      )}

      {selectedContent && showDNA && (
        <ContentDNAModal content={selectedContent} onClose={() => setShowDNA(false)} />
      )}

      {selectedContent && !showDNA && (
        <ExplainabilityPanel content={selectedContent} onClose={() => setSelectedContent(null)} onViewDNA={() => setShowDNA(true)} />
      )}
    </div>
  )
}

function HomePage({ items, selectedContent, onCardClick, onDNAClick }) {
  // The hero shows the active selection when one exists; otherwise the
  // default featured title (items[2]). This is what binds an Ask Nexus
  // "open it" action to the main page instead of leaving it on the default.
  const featured = selectedContent || items[2]
  const aiCurated = items.slice(0, 8)
  const slowBurn  = items.filter(c => (c.dna?.pacing||1) < 0.5)
  const highTension = items.filter(c => (c.dna?.pacing||0) >= 0.7)
  const international = items.filter(c => ['squid-game-s1-2021','parasite-2019','dark-s1-2017','money-heist-s1-2017','kingdom-s1-2019','shogun-2024'].includes(c.id))

  return (
    <>
      <HeroSection featured={featured} onPlay={() => onCardClick(featured)} onInfo={() => onDNAClick(featured)} />
      <div className="px-6 md:px-10 lg:px-16 pb-24 space-y-12 mt-8">
        <ContentRow title="Recommended for You" subtitle="Powered by your semantic profile" items={aiCurated} onCardClick={onCardClick} onDNAClick={onDNAClick} badge="AI CURATED" />
        <ContentRow title="Slow Burn Masterpieces" subtitle="Pacing ≤ 0.5 · Atmospheric · Rewatchable" items={slowBurn} onCardClick={onCardClick} onDNAClick={onDNAClick} badge="DNA MATCH" />
        <ContentRow title="High-Tension" subtitle="Pacing ≥ 0.7 · Drama-forward" items={highTension} onCardClick={onCardClick} onDNAClick={onDNAClick} badge="INTENSE" />
        <ContentRow title="International Excellence" subtitle="Best of global cinema and television" items={international} onCardClick={onCardClick} onDNAClick={onDNAClick} badge="WORLD" />
      </div>
    </>
  )
}
