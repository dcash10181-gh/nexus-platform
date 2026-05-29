import React, { useState, useEffect, useCallback } from 'react'
import { HashRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import HeroSection from './components/HeroSection.jsx'
import ContentRow from './components/ContentRow.jsx'
import AskNexus from './components/AskNexus.jsx'
import ProactiveAlert from './components/ProactiveAlert.jsx'
import ExplainabilityPanel from './components/ExplainabilityPanel.jsx'
import ContentDNAModal from './components/ContentDNAModal.jsx'
import BrowsePage from './pages/BrowsePage.jsx'
import ImpactDashboard from './pages/ImpactDashboard.jsx'
import AdminDashboard from './pages/AdminDashboard.jsx'

const MOCK_CONTENT = [
  { id:'severance-s1-2022', title:'Severance', year:2022, kind:'series', synopsis:'A team of office workers have their memories surgically divided between work and personal lives.', genres:['Sci-Fi','Thriller','Drama'], rating:8.7, poster_url:'https://image.tmdb.org/t/p/w500/b6tsr7PFYK9LKA7q7UjOlFOkwLQ.jpg', backdrop_url:'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1400&q=80', cast:['Adam Scott','Patricia Arquette','John Turturro'], dna:{pacing:0.45,tension_curve:[0.2,0.35,0.6,0.75,0.9,0.95],visual_style:'sterile geometric',audio_mood:'unnerving',thematic_tags:['identity','corporate dystopia','memory'],runtime_min:50}, signals:[{name:'Semantic match',weight:0.91,detail:'Strong thematic alignment with psychological sci-fi',icon:'brain'},{name:'Genre affinity',weight:0.88,detail:'Matches your Sci-Fi and Thriller preference',icon:'film'}] },
  { id:'the-bear-s1-2022', title:'The Bear', year:2022, kind:'series', synopsis:"A rising chef returns to run his late brother's chaotic Chicago sandwich shop.", genres:['Drama','Comedy'], rating:8.7, poster_url:'https://image.tmdb.org/t/p/w500/sHFlbKS3WLqMnp9t2ghADIJFnuQ.jpg', backdrop_url:'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1400&q=80', cast:['Jeremy Allen White','Ayo Edebiri'], dna:{pacing:0.88,tension_curve:[0.5,0.7,0.8,0.9,0.95,0.85],visual_style:'handheld naturalistic',audio_mood:'intense',thematic_tags:['grief','ambition','family'],runtime_min:30}, signals:[{name:'Completion predictor',weight:0.94,detail:'Users with your profile finish 96% of episodes',icon:'trending-up'}] },
  { id:'blade-runner-2049', title:'Blade Runner 2049', year:2017, kind:'film', synopsis:'A young blade runner discovers a long-buried secret, leading him to track down former blade runner Rick Deckard.', genres:['Sci-Fi','Drama','Thriller'], rating:8.0, poster_url:'https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg', backdrop_url:'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=1400&q=80', cast:['Ryan Gosling','Harrison Ford'], dna:{pacing:0.28,tension_curve:[0.2,0.3,0.4,0.55,0.7,0.8],visual_style:'neo noir cinematic',audio_mood:'melancholic atmospheric',thematic_tags:['AI consciousness','identity','memory'],runtime_min:164}, signals:[{name:'Semantic match',weight:0.93,detail:'Deep alignment with cerebral sci-fi',icon:'brain'},{name:'Visual DNA',weight:0.89,detail:"Deakins cinematography — you've rated similar styles 9/10",icon:'eye'}] },
  { id:'dune-part-two-2024', title:'Dune: Part Two', year:2024, kind:'film', synopsis:'Paul Atreides unites with the Fremen and seeks revenge against the conspirators who destroyed his family.', genres:['Sci-Fi','Adventure','Drama'], rating:8.5, poster_url:'https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg', backdrop_url:'https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=1400&q=80', cast:['Timothée Chalamet','Zendaya'], dna:{pacing:0.65,tension_curve:[0.3,0.5,0.7,0.8,0.9,0.95],visual_style:'epic cinematic',audio_mood:'grand ominous',thematic_tags:['prophecy','colonialism','ecology'],runtime_min:167}, signals:[{name:'Recent release',weight:0.79,detail:'Released 2024 — trending',icon:'trending-up'}] },
  { id:'dark-s1-2017', title:'Dark', year:2017, kind:'series', synopsis:'A mystery spanning four generations in a German town. Time, family, and apocalypse intertwined.', genres:['Sci-Fi','Mystery','Thriller'], rating:8.8, poster_url:'https://image.tmdb.org/t/p/w500/apbrbWs8M9lyOpJYU5WXrpFbk1Z.jpg', backdrop_url:'https://images.unsplash.com/photo-1475274047050-1d0c0975c63e?w=1400&q=80', cast:['Louis Hofmann','Oliver Masucci'], dna:{pacing:0.4,tension_curve:[0.25,0.45,0.6,0.75,0.85,0.9],visual_style:'dark european',audio_mood:'eerie atmospheric',thematic_tags:['time travel','determinism','cycles'],runtime_min:52}, signals:[{name:'Semantic match',weight:0.95,detail:'Highest semantic overlap with Severance and Inception',icon:'brain'}] },
  { id:'shogun-2024', title:'Shōgun', year:2024, kind:'limited', synopsis:'Feudal Japan. A European sailor. A lord seeking power. Possibly the best prestige TV of 2024.', genres:['Drama','History','Action'], rating:8.8, poster_url:'https://image.tmdb.org/t/p/w500/7O4iVfOMQmdCSxhOg1WnzG1AgYT.jpg', backdrop_url:'https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=1400&q=80', cast:['Hiroyuki Sanada','Cosmo Jarvis'], dna:{pacing:0.48,tension_curve:[0.25,0.45,0.6,0.75,0.85,0.9],visual_style:'epic period',audio_mood:'ceremonial tense',thematic_tags:['honor','war','culture clash'],runtime_min:58}, signals:[{name:'Completion predictor',weight:0.92,detail:'94% of users with your profile watched the full season',icon:'trending-up'}] },
  { id:'succession-s4-2023', title:'Succession', year:2018, kind:'series', synopsis:'The Roy family controls the world\'s largest media empire. What they do to each other is worse than anything they do to outsiders.', genres:['Drama','Comedy'], rating:8.9, poster_url:'https://image.tmdb.org/t/p/w500/e2X8g1RBKSNmFEOdnMxIMH4zwbF.jpg', backdrop_url:'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=1400&q=80', cast:['Brian Cox','Jeremy Strong','Sarah Snook'], dna:{pacing:0.55,tension_curve:[0.4,0.55,0.65,0.75,0.85,0.95],visual_style:'prestige naturalistic',audio_mood:'tense sardonic',thematic_tags:['power','betrayal','capitalism'],runtime_min:58}, signals:[{name:'Cultural moment',weight:0.95,detail:'Most discussed drama of the decade',icon:'trending-up'}] },
  { id:'breaking-bad-s1-2008', title:'Breaking Bad', year:2008, kind:'series', synopsis:'A chemistry teacher diagnosed with cancer turns to cooking methamphetamine to secure his family\'s future.', genres:['Crime','Drama','Thriller'], rating:9.5, poster_url:'https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg', backdrop_url:'https://images.unsplash.com/photo-1509909756405-be0199881695?w=1400&q=80', cast:['Bryan Cranston','Aaron Paul'], dna:{pacing:0.62,tension_curve:[0.2,0.45,0.65,0.8,0.92,0.98],visual_style:'desert neo western',audio_mood:'tense percussive',thematic_tags:['transformation','pride','family','consequences'],runtime_min:48}, signals:[{name:'Semantic match',weight:0.92,detail:'Tightest character arc on television',icon:'brain'}] },
  { id:'the-wire-s1-2002', title:'The Wire', year:2002, kind:'series', synopsis:'The Baltimore drug trade and the police who surveil it, told from both sides with documentary-level authenticity.', genres:['Crime','Drama'], rating:9.3, poster_url:'https://image.tmdb.org/t/p/w500/4lCqDTOoHhLkUvDe5kmqLOv0pK7.jpg', backdrop_url:'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1400&q=80', cast:['Dominic West','Idris Elba','Michael K. Williams'], dna:{pacing:0.45,tension_curve:[0.3,0.5,0.65,0.75,0.82,0.88],visual_style:'gritty documentary',audio_mood:'urban sparse',thematic_tags:['institutional failure','drug trade','surveillance'],runtime_min:58}, signals:[{name:'Semantic match',weight:0.9,detail:'Gold standard for crime drama',icon:'brain'}] },
  { id:'chernobyl-2019', title:'Chernobyl', year:2019, kind:'limited', synopsis:'The true story of the 1986 nuclear disaster and the men and women who sacrificed to contain it.', genres:['Drama','History','Thriller'], rating:9.4, poster_url:'https://image.tmdb.org/t/p/w500/hlLXt2tOPT6RRnjiUmoxyG1LTFi.jpg', backdrop_url:'https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=1400&q=80', cast:['Jared Harris','Stellan Skarsgård'], dna:{pacing:0.55,tension_curve:[0.4,0.6,0.75,0.88,0.95,0.9],visual_style:'soviet grey',audio_mood:'industrial dread',thematic_tags:['nuclear disaster','Soviet Union','truth','sacrifice'],runtime_min:65}, signals:[{name:'Semantic match',weight:0.88,detail:'Most precisely researched limited series ever made',icon:'brain'}] },
  { id:'the-last-of-us-s1-2023', title:'The Last of Us', year:2023, kind:'series', synopsis:'After a global catastrophe, a hardened survivor and a teenage girl make a dangerous journey across a post-apocalyptic America.', genres:['Drama','Sci-Fi','Horror'], rating:8.8, poster_url:'https://image.tmdb.org/t/p/w500/uKvVjHNqB5VmOrdxqAt2F7J78ED.jpg', backdrop_url:'https://images.unsplash.com/photo-1476357471311-43c0db9fb2b4?w=1400&q=80', cast:['Pedro Pascal','Bella Ramsey'], dna:{pacing:0.52,tension_curve:[0.3,0.55,0.65,0.75,0.85,0.9],visual_style:'naturalistic bleak',audio_mood:'melancholic haunting',thematic_tags:['survival','fatherhood','grief','humanity'],runtime_min:55}, signals:[{name:'Semantic match',weight:0.87,detail:'Bar for post-apocalyptic storytelling',icon:'brain'}] },
  { id:'fleabag-s1-2016', title:'Fleabag', year:2016, kind:'series', synopsis:'A young woman navigates modern life in London with painfully sharp wit, breaking the fourth wall.', genres:['Comedy','Drama'], rating:8.7, poster_url:'https://image.tmdb.org/t/p/w500/7SMxfbXNB29JWDxiDMp7eKmLMOb.jpg', backdrop_url:'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=1400&q=80', cast:['Phoebe Waller-Bridge'], dna:{pacing:0.7,tension_curve:[0.3,0.5,0.62,0.72,0.8,0.82],visual_style:'direct address london',audio_mood:'witty sparse',thematic_tags:['grief','women','fourth wall','sex','guilt'],runtime_min:25}, signals:[{name:'Genre affinity',weight:0.88,detail:'Perfect for Comedy-Drama fans',icon:'film'}] },
  { id:'squid-game-s1-2021', title:'Squid Game', year:2021, kind:'series', synopsis:'Hundreds of cash-strapped contestants accept an invitation to compete in children\'s games for a massive prize. Losers are eliminated — permanently.', genres:['Thriller','Drama','Sci-Fi'], rating:8.0, poster_url:'https://image.tmdb.org/t/p/w500/dDlEmu3EZ0Pgg93K2SVNLCjCSvE.jpg', backdrop_url:'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=1400&q=80', cast:['Lee Jung-jae','Park Hae-soo'], dna:{pacing:0.75,tension_curve:[0.4,0.62,0.78,0.88,0.94,0.9],visual_style:'pastel brutal',audio_mood:'folk horror blend',thematic_tags:['class warfare','survival','debt','Korea'],runtime_min:55}, signals:[{name:'Semantic match',weight:0.85,detail:'Global phenomenon with sharp class satire',icon:'brain'}] },
  { id:'parasite-2019', title:'Parasite', year:2019, kind:'film', synopsis:'A poor family schemes to become employed by a wealthy family by infiltrating their household.', genres:['Drama','Thriller','Comedy'], rating:8.5, poster_url:'https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg', backdrop_url:'https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=1400&q=80', cast:['Song Kang-ho','Choi Woo-shik'], dna:{pacing:0.72,tension_curve:[0.3,0.5,0.6,0.8,0.95,0.9],visual_style:'precise geometric',audio_mood:'playful to terrifying',thematic_tags:['class inequality','deception','survival','Korean society'],runtime_min:132}, signals:[{name:'Semantic match',weight:0.89,detail:'Genre-defying masterpiece',icon:'brain'}] },
  { id:'mad-max-fury-road-2015', title:'Mad Max: Fury Road', year:2015, kind:'film', synopsis:'In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in a high-octane road war.', genres:['Action','Sci-Fi','Adventure'], rating:8.1, poster_url:'https://image.tmdb.org/t/p/w500/kqjL17yufvn9OVLyXYpvtyrFfak.jpg', backdrop_url:'https://images.unsplash.com/photo-1509909756405-be0199881695?w=1400&q=80', cast:['Tom Hardy','Charlize Theron'], dna:{pacing:0.97,tension_curve:[0.6,0.8,0.9,0.95,0.97,0.99],visual_style:'post apocalyptic saturated',audio_mood:'electric guitar percussion',thematic_tags:['feminism','survival','chase','dystopia'],runtime_min:120}, signals:[{name:'Semantic match',weight:0.91,detail:'Greatest action film of the 21st century',icon:'brain'}] },
  { id:'ted-lasso-s1-2020', title:'Ted Lasso', year:2020, kind:'series', synopsis:'An American football coach hired to manage an English soccer team despite knowing nothing about the sport.', genres:['Comedy','Drama'], rating:8.8, poster_url:'https://image.tmdb.org/t/p/w500/3gMIGxFMIQh06j4MsBQ96VjuVlD.jpg', backdrop_url:'https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1400&q=80', cast:['Jason Sudeikis','Hannah Waddingham'], dna:{pacing:0.55,tension_curve:[0.3,0.45,0.55,0.6,0.65,0.7],visual_style:'warm british',audio_mood:'uplifting folk pop',thematic_tags:['kindness','football','mental health','belief'],runtime_min:45}, signals:[{name:'Genre affinity',weight:0.87,detail:'Perfect feel-good series',icon:'film'}] },
  { id:'arcane-s1-2021', title:'Arcane', year:2021, kind:'series', synopsis:'Set in the utopian Piltover and the oppressed underground of Zaun, following the origins of two legendary champions.', genres:['Animation','Action','Fantasy'], rating:9.0, poster_url:'https://image.tmdb.org/t/p/w500/fqldf2t8ztc9aiwn3k6mlX3tvRT.jpg', backdrop_url:'https://images.unsplash.com/photo-1509909756405-be0199881695?w=1400&q=80', cast:['Hailee Steinfeld','Ella Purnell'], dna:{pacing:0.7,tension_curve:[0.35,0.55,0.72,0.85,0.92,0.95],visual_style:'painterly animation',audio_mood:'indie orchestral hybrid',thematic_tags:['sisters','class','revolution','technology'],runtime_min:42}, signals:[{name:'Semantic match',weight:0.9,detail:'Best animated series ever made',icon:'brain'}] },
  { id:'oppenheimer-2023', title:'Oppenheimer', year:2023, kind:'film', synopsis:'The story of J. Robert Oppenheimer and his role in the development of the atomic bomb.', genres:['Drama','History','Thriller'], rating:8.9, poster_url:'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg', backdrop_url:'https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=1400&q=80', cast:['Cillian Murphy','Emily Blunt','Matt Damon'], dna:{pacing:0.62,tension_curve:[0.3,0.5,0.6,0.75,0.9,0.8],visual_style:'epic prestige',audio_mood:'intense cerebral',thematic_tags:['nuclear age','moral responsibility','genius','Cold War'],runtime_min:180}, signals:[{name:'Semantic match',weight:0.88,detail:'Nolan at his most ambitious',icon:'brain'}] },
]

const PROACTIVE_REC = { title:'Perfect for tonight', content:MOCK_CONTENT[0], reasoning:"It's Friday evening. Severance matches your slow-burn psychological pattern exactly.", push_notification:{ body:"Severance is calling your name tonight ✦" } }

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
        return <BrowsePage title="Browse All" subtitle="Complete catalog · 81 titles" items={MOCK_CONTENT} onCardClick={handleCardClick} onDNAClick={handleShowDNA} showGenreFilter />
      default:
        return <HomePage items={MOCK_CONTENT} onCardClick={handleCardClick} onDNAClick={handleShowDNA} myListIds={myListIds} toggleMyList={toggleMyList} />
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

      <AskNexus isOpen={showAskNexus} onClose={() => setShowAskNexus(false)} onContentSelect={(item) => { setSelectedContent(item); setShowDNA(true); setShowAskNexus(false) }} allContent={MOCK_CONTENT} />

      {showProactive && currentPage === 'home' && (
        <ProactiveAlert recommendation={PROACTIVE_REC} onDismiss={() => setShowProactive(false)} onViewContent={() => { setSelectedContent(PROACTIVE_REC.content); setShowDNA(true); setShowProactive(false) }} />
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

function HomePage({ items, onCardClick, onDNAClick }) {
  const featured = items[2] // Blade Runner as hero
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
