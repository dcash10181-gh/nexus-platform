import React, { useState, useEffect, useCallback } from 'react'
import { HashRouter, Routes, Route } from 'react-router-dom'
import AdminDashboard from './pages/AdminDashboard.jsx'
import Navbar from './components/Navbar.jsx'
import HeroSection from './components/HeroSection.jsx'
import ContentRow from './components/ContentRow.jsx'
import AskNexus from './components/AskNexus.jsx'
import ProactiveAlert from './components/ProactiveAlert.jsx'
import ExplainabilityPanel from './components/ExplainabilityPanel.jsx'
import ContentDNAModal from './components/ContentDNAModal.jsx'

// ── Mock catalog — identical structure to API response ─────────────────────
const MOCK_CONTENT = [
  {
    id: 'severance-s1-2022', title: 'Severance', year: 2022, kind: 'series',
    synopsis: 'A team of office workers have their memories surgically divided between work and personal lives — until one seeks to merge both.',
    genres: ['Sci-Fi', 'Thriller', 'Drama'], rating: 8.7,
    poster_url: 'https://image.tmdb.org/t/p/w500/b6tsr7PFYK9LKA7q7UjOlFOkwLQ.jpg',
    backdrop_url: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1400&q=80',
    cast: ['Adam Scott', 'Patricia Arquette', 'John Turturro'],
    dna: { pacing: 0.45, tension_curve: [0.2,0.35,0.6,0.75,0.9,0.95], visual_style: 'sterile geometric', audio_mood: 'unnerving', thematic_tags: ['identity','corporate dystopia','memory'], runtime_min: 50 },
    signals: [
      { name: 'Semantic match', weight: 0.91, detail: 'Strong thematic alignment with psychological sci-fi in your history', icon: 'brain' },
      { name: 'Genre affinity', weight: 0.88, detail: 'Matches your consistent preference for Sci-Fi and Thriller', icon: 'film' },
      { name: 'Visual DNA', weight: 0.76, detail: 'Cinematography: sterile geometric — similar to your Blade Runner watch', icon: 'eye' },
      { name: 'Director pattern', weight: 0.65, detail: 'Ben Stiller directing style aligns with 3 of your favorites', icon: 'trending-up' },
    ],
  },
  {
    id: 'the-bear-s1-2022', title: 'The Bear', year: 2022, kind: 'series',
    synopsis: 'A rising chef leaves haute cuisine to run his late brother\'s chaotic Chicago sandwich shop. Every episode is a controlled explosion.',
    genres: ['Drama', 'Comedy'], rating: 8.7,
    poster_url: 'https://image.tmdb.org/t/p/w500/sHFlbKS3WLqMnp9t2ghADIJFnuQ.jpg',
    backdrop_url: 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1400&q=80',
    cast: ['Jeremy Allen White', 'Ayo Edebiri', 'Ebon Moss-Bachrach'],
    dna: { pacing: 0.88, tension_curve: [0.5,0.7,0.8,0.9,0.95,0.85], visual_style: 'handheld naturalistic', audio_mood: 'intense', thematic_tags: ['grief','ambition','family'], runtime_min: 30 },
    signals: [
      { name: 'Semantic match', weight: 0.87, detail: 'Narrative intensity matches your completion of Succession and Beef', icon: 'brain' },
      { name: 'Completion predictor', weight: 0.94, detail: 'Users with your profile finish 96% of episodes', icon: 'trending-up' },
    ],
  },
  {
    id: 'blade-runner-2049', title: 'Blade Runner 2049', year: 2017, kind: 'film',
    synopsis: 'A young blade runner discovers a long-buried secret, leading him to track down former blade runner Rick Deckard through a breathtaking neo-noir future.',
    genres: ['Sci-Fi', 'Drama', 'Thriller'], rating: 8.0,
    poster_url: 'https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg',
    backdrop_url: 'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=1400&q=80',
    cast: ['Ryan Gosling', 'Harrison Ford', 'Ana de Armas'],
    dna: { pacing: 0.28, tension_curve: [0.2,0.3,0.4,0.55,0.7,0.8], visual_style: 'neo noir cinematic', audio_mood: 'melancholic atmospheric', thematic_tags: ['AI consciousness','identity','memory'], runtime_min: 164 },
    signals: [
      { name: 'Semantic match', weight: 0.93, detail: 'Deep alignment with your taste for cerebral sci-fi and AI themes', icon: 'brain' },
      { name: 'Visual DNA', weight: 0.89, detail: 'Deakins cinematography — you\'ve rated similar visual styles 9/10', icon: 'eye' },
      { name: 'Director affinity', weight: 0.82, detail: 'Denis Villeneuve directed 2 of your all-time favorites', icon: 'film' },
    ],
  },
  {
    id: 'dune-part-two-2024', title: 'Dune: Part Two', year: 2024, kind: 'film',
    synopsis: 'Paul Atreides unites with the Fremen and seeks revenge. The second chapter of an epic that will define a generation of sci-fi cinema.',
    genres: ['Sci-Fi', 'Adventure', 'Drama'], rating: 8.5,
    poster_url: 'https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg',
    backdrop_url: 'https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=1400&q=80',
    cast: ['Timothée Chalamet', 'Zendaya', 'Austin Butler'],
    dna: { pacing: 0.65, tension_curve: [0.3,0.5,0.7,0.8,0.9,0.95], visual_style: 'epic cinematic', audio_mood: 'grand ominous', thematic_tags: ['prophecy','colonialism','ecology'], runtime_min: 167 },
    signals: [
      { name: 'Semantic match', weight: 0.88, detail: 'Epic scope matches your viewing of Shogun and Game of Thrones', icon: 'brain' },
      { name: 'Recent release', weight: 0.79, detail: 'Released 2024 — trending and culturally dominant', icon: 'trending-up' },
    ],
  },
  {
    id: 'dark-s1-2017', title: 'Dark', year: 2017, kind: 'series',
    synopsis: 'A mystery spanning four generations in a German town. Time, family, and apocalypse intertwined in a puzzle that rewards every rewatch.',
    genres: ['Sci-Fi', 'Mystery', 'Thriller'], rating: 8.8,
    poster_url: 'https://image.tmdb.org/t/p/w500/apbrbWs8M9lyOpJYU5WXrpFbk1Z.jpg',
    backdrop_url: 'https://images.unsplash.com/photo-1475274047050-1d0c0975c63e?w=1400&q=80',
    cast: ['Louis Hofmann', 'Oliver Masucci', 'Lisa Vicari'],
    dna: { pacing: 0.4, tension_curve: [0.25,0.45,0.6,0.75,0.85,0.9], visual_style: 'dark european', audio_mood: 'eerie atmospheric', thematic_tags: ['time travel','determinism','cycles'], runtime_min: 52 },
    signals: [
      { name: 'Semantic match', weight: 0.95, detail: 'Highest semantic overlap with Severance and Inception in your history', icon: 'brain' },
      { name: 'Genre affinity', weight: 0.91, detail: 'Perfect match for Sci-Fi + Mystery combination you favour', icon: 'film' },
    ],
  },
  {
    id: 'shogun-2024', title: 'Shōgun', year: 2024, kind: 'limited',
    synopsis: 'Feudal Japan. A European sailor. A lord seeking power. A translator caught between worlds. Possibly the best prestige TV of 2024.',
    genres: ['Drama', 'History', 'Action'], rating: 8.8,
    poster_url: 'https://image.tmdb.org/t/p/w500/7O4iVfOMQmdCSxhOg1WnzG1AgYT.jpg',
    backdrop_url: 'https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=1400&q=80',
    cast: ['Hiroyuki Sanada', 'Cosmo Jarvis', 'Anna Sawai'],
    dna: { pacing: 0.48, tension_curve: [0.25,0.45,0.6,0.75,0.85,0.9], visual_style: 'epic period', audio_mood: 'ceremonial tense', thematic_tags: ['honor','war','culture clash'], runtime_min: 58 },
    signals: [
      { name: 'Semantic match', weight: 0.85, detail: 'Shares narrative DNA with your Succession and House of Dragon history', icon: 'brain' },
      { name: 'Completion predictor', weight: 0.92, detail: '94% of users with your profile watched the full season', icon: 'trending-up' },
    ],
  },
  {
    id: 'succession-s4-2023', title: 'Succession', year: 2018, kind: 'series',
    synopsis: 'The Roy family controls the world\'s largest media empire. What they do to each other is worse than anything they do to outsiders.',
    genres: ['Drama', 'Comedy'], rating: 8.9,
    poster_url: 'https://image.tmdb.org/t/p/w500/e2X8g1RBKSNmFEOdnMxIMH4zwbF.jpg',
    backdrop_url: 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=1400&q=80',
    cast: ['Brian Cox', 'Jeremy Strong', 'Sarah Snook'],
    dna: { pacing: 0.55, tension_curve: [0.4,0.55,0.65,0.75,0.85,0.95], visual_style: 'prestige naturalistic', audio_mood: 'tense sardonic', thematic_tags: ['power','betrayal','capitalism'], runtime_min: 58 },
    signals: [
      { name: 'Semantic match', weight: 0.89, detail: 'Power dynamics and family dysfunction align with your Drama preferences', icon: 'brain' },
      { name: 'Cultural moment', weight: 0.95, detail: 'Most discussed drama of the decade — referenced in 40 of your genre peers', icon: 'trending-up' },
    ],
  },
  {
    id: 'silo-s1-2023', title: 'Silo', year: 2023, kind: 'series',
    synopsis: 'Thousands live underground in a massive silo in a ruined future. One engineer discovers the world they were told about may not exist.',
    genres: ['Sci-Fi', 'Drama', 'Thriller'], rating: 8.1,
    poster_url: 'https://image.tmdb.org/t/p/w500/xy4JFAy0vMvvfHOuboq4OLa3XnI.jpg',
    backdrop_url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1400&q=80',
    cast: ['Rebecca Ferguson', 'Tim Robbins', 'Common'],
    dna: { pacing: 0.5, tension_curve: [0.3,0.45,0.6,0.75,0.85,0.9], visual_style: 'gritty industrial', audio_mood: 'ominous claustrophobic', thematic_tags: ['dystopia','truth','rebellion'], runtime_min: 55 },
    signals: [
      { name: 'Semantic match', weight: 0.88, detail: 'Strongest connection to Severance in your watch history', icon: 'brain' },
      { name: 'Visual DNA', weight: 0.72, detail: 'Industrial aesthetic matches 4 of your recent completions', icon: 'eye' },
    ],
  },
]

const PROACTIVE_REC = {
  title: 'Perfect for tonight',
  content: MOCK_CONTENT[0],
  reasoning: "It's Friday evening and you completed Silo last Tuesday. Severance matches your slow-burn psychological pattern exactly.",
  push_notification: { body: "Severance is calling your name tonight ✦" },
}

export default function App() {
  // State managed in MainApp component above

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
  const [selectedContent, setSelectedContent]   = React.useState(null)
  const [showDNA, setShowDNA]                   = React.useState(false)
  const [showAskNexus, setShowAskNexus]         = React.useState(false)
  const [showProactive, setShowProactive]        = React.useState(false)
  const [apiConnected, setApiConnected]          = React.useState(false)

  React.useEffect(() => {
    const t = setTimeout(() => setShowProactive(true), 4000)
    return () => clearTimeout(t)
  }, [])

  React.useEffect(() => {
    fetch('/api/health').then(r => r.ok && setApiConnected(true)).catch(() => {})
  }, [])

  const handleCardClick = React.useCallback((item) => { setSelectedContent(item) }, [])
  const handleShowDNA   = React.useCallback((item, e) => { e.stopPropagation(); setSelectedContent(item); setShowDNA(true) }, [])

  return (
    <div className="min-h-screen bg-nexus-bg relative overflow-x-hidden">
      {/* Ambient background blobs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full opacity-[0.04]"
          style={{ background: 'radial-gradient(circle, #00d4ff 0%, transparent 70%)' }} />
        <div className="absolute bottom-[-10%] right-[-5%] w-[500px] h-[500px] rounded-full opacity-[0.03]"
          style={{ background: 'radial-gradient(circle, #ff0080 0%, transparent 70%)' }} />
      </div>

      <Navbar
        onAskNexus={() => setShowAskNexus(true)}
        apiConnected={apiConnected}
      />

      <main className="relative z-10">
        {/* Hero */}
        <HeroSection
          featured={MOCK_CONTENT[2]}
          onPlay={() => handleCardClick(MOCK_CONTENT[2])}
          onInfo={() => { setSelectedContent(MOCK_CONTENT[2]); setShowDNA(true); }}
        />

        {/* Content rows */}
        <div className="px-6 md:px-10 lg:px-16 pb-24 space-y-12 mt-8">
          <ContentRow
            title="Recommended for You"
            subtitle="Powered by your semantic profile"
            items={MOCK_CONTENT}
            onCardClick={handleCardClick}
            onDNAClick={handleShowDNA}
            badge="AI CURATED"
          />
          <ContentRow
            title="Slow Burn Masterpieces"
            subtitle="Pacing ≤ 0.5 · Cinematic · Rewatchable"
            items={[...MOCK_CONTENT].filter(c => c.dna.pacing < 0.5)}
            onCardClick={handleCardClick}
            onDNAClick={handleShowDNA}
            badge="DNA MATCH"
          />
          <ContentRow
            title="High-Tension Releases"
            subtitle="Pacing ≥ 0.7 · Drama-forward · 2022–2024"
            items={[...MOCK_CONTENT].filter(c => c.dna.pacing >= 0.7)}
            onCardClick={handleCardClick}
            onDNAClick={handleShowDNA}
            badge="NEW"
          />
        </div>
      </main>

      {/* Ask Nexus — conversational discovery overlay */}
      <AskNexus
        isOpen={showAskNexus}
        onClose={() => setShowAskNexus(false)}
        onContentSelect={handleCardClick}
      />

      {/* Proactive agent alert */}
      {showProactive && (
        <ProactiveAlert
          recommendation={PROACTIVE_REC}
          onDismiss={() => setShowProactive(false)}
          onViewContent={() => {
            setSelectedContent(PROACTIVE_REC.content)
            setShowDNA(true)
            setShowProactive(false)
          }}
        />
      )}

      {/* Explainability + Content DNA modal */}
      {selectedContent && showDNA && (
        <ContentDNAModal
          content={selectedContent}
          onClose={() => { setShowDNA(false); setSelectedContent(null); }}
        />
      )}

      {/* Explainability side-panel (click any card) */}
      {selectedContent && !showDNA && (
        <ExplainabilityPanel
          content={selectedContent}
          onClose={() => setSelectedContent(null)}
          onViewDNA={() => setShowDNA(true)}
        />
      )}
    </div>
  )
}
