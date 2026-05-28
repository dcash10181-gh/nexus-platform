import React, { useState, useRef, useEffect } from 'react'
import { X, Send, Sparkles, Brain, Loader } from 'lucide-react'

// ── Comprehensive mock responses keyed by trigger words ─────────────────
const MOCK_RESPONSES = [
  {
    trigger: ['wire', 'breaking bad', 'sopranos', 'crime drama', 'intense crime', 'prestige crime', 'mob', 'cartel', 'drug', 'gangster'],
    reply: "For intense crime drama, **The Wire** is the gold standard — it makes every other crime show feel shallow. **Breaking Bad** is the tightest character arc on television. If you want older school, **The Sopranos** invented the template. All three reward patience heavily.",
    suggestions: ['the-wire-s1-2002', 'breaking-bad-s1-2008', 'the-sopranos-s1-1999'],
  },
  {
    trigger: ['thriller', 'suspense', 'tension', 'edge of seat', 'edge-of-seat', 'mindhunter', 'gone girl', 'nightcrawler'],
    reply: "For pure sustained tension: **Mindhunter** builds dread through conversation, never action. **Gone Girl** is Fincher at his most precise. **Nightcrawler** gives you a protagonist so unsettling you feel complicit just watching.",
    suggestions: ['mindhunter-s1-2017', 'gone-girl-2014', 'nightcrawler-2014'],
  },
  {
    trigger: ['horror', 'scary', 'frightening', 'disturbing', 'creepy', 'midsommar', 'hereditary'],
    reply: "**Hereditary** is the most genuinely disturbing family horror in years. **Midsommar** does something rarer — horror in full sunlight. **Get Out** wraps its scares in something smarter. All three stay with you.",
    suggestions: ['hereditary-2018', 'midsommar-2019', 'get-out-2017'],
  },
  {
    trigger: ['comedy', 'funny', 'laugh', 'light', 'lighthearted', 'feel good', 'feel-good', 'warm', 'uplifting'],
    reply: "**Fleabag** is the sharpest comedy-drama of the decade — just 12 episodes, endlessly rewatchable. **Ted Lasso** is radical optimism as entertainment. **The Good Place** hides genuine philosophy in a sitcom costume.",
    suggestions: ['fleabag-s1-2016', 'ted-lasso-s1-2020', 'the-good-place-s1-2016'],
  },
  {
    trigger: ['international', 'foreign', 'subtitles', 'korean', 'spanish', 'french', 'german', 'squid game', 'money heist'],
    reply: "**Squid Game** earns every bit of its reputation — the satire is sharper than the violence. **Money Heist** is pure propulsive entertainment. **Parasite** and **Dark** are the two best arguments for watching with subtitles.",
    suggestions: ['squid-game-s1-2021', 'money-heist-s1-2017', 'parasite-2019'],
  },
  {
    trigger: ['sci-fi', 'science fiction', 'futuristic', 'space', 'ai', 'artificial intelligence', 'robot', 'technology'],
    reply: "**Severance** for corporate body horror. **Mr. Robot** for hacker paranoia that actually gets the technology right. **Ex Machina** for AI consciousness in 108 tight minutes. **Her** if you want something quieter and more devastating.",
    suggestions: ['severance-s1-2022', 'mr-robot-s1-2015', 'ex-machina-2014'],
  },
  {
    trigger: ['rainy', 'cozy', 'quiet', 'slow', 'slow burn', 'atmospheric', 'meditative', 'melancholic'],
    reply: "For a slow, atmospheric evening: **Blade Runner 2049** is the most beautiful film of the decade — 164 minutes that feel like 90. **Aftersun** for something smaller and devastating. **Past Lives** if you want to end the night wrecked in the best way.",
    suggestions: ['blade-runner-2049', 'aftersun-2022', 'past-lives-2023'],
  },
  {
    trigger: ['mind', 'mindbending', 'mind-bending', 'twist', 'complex', 'puzzle', 'inception', 'confusing', 'layers'],
    reply: "**Dark** is the most architecturally complex thing on television — three seasons, four timelines, zero wasted scenes. **Inception** if you want film-length. **Arrival** reframes everything you saw in its final act.",
    suggestions: ['dark-s1-2017', 'inception-2010', 'arrival-2016'],
  },
  {
    trigger: ['action', 'epic', 'spectacle', 'blockbuster', 'big', 'explosive'],
    reply: "**Mad Max: Fury Road** is the greatest action film of the 21st century — practical, relentless, and somehow feminist. **Dune: Part Two** for scope. **Mission Impossible Fallout** for technical craft.",
    suggestions: ['mad-max-fury-road-2015', 'dune-part-two-2024', 'mission-impossible-fallout-2018'],
  },
  {
    trigger: ['fantasy', 'medieval', 'dragons', 'game of thrones', 'house of dragon', 'magic', 'world building'],
    reply: "**House of the Dragon** recovered the prestige fantasy crown. **Shogun** is equally epic but grounded in real history. **Arcane** is the best animated fantasy series ever made — don't skip it because it's animated.",
    suggestions: ['house-of-dragon-s1-2022', 'shogun-2024', 'arcane-s1-2021'],
  },
  {
    trigger: ['work', 'office', 'corporate', 'business', 'power', 'politics', 'workplace'],
    reply: "**Severance** for the existential horror of work. **Succession** for corporate power at Shakespearean scale. **The Bear** if you want the kitchen as a pressure cooker — episodes so intense they're exhausting.",
    suggestions: ['severance-s1-2022', 'succession-s4-2023', 'the-bear-s1-2022'],
  },
  {
    trigger: ['true crime', 'investigation', 'detective', 'mystery', 'murder', 'serial killer', 'police'],
    reply: "**Mindhunter** for FBI profiling done right. **True Detective: Night Country** for arctic noir atmosphere. **Slow Horses** for British intelligence with Gary Oldman at his most disheveled.",
    suggestions: ['mindhunter-s1-2017', 'true-detective-s4-2024', 'slow-horses-s1-2022'],
  },
  {
    trigger: ['animation', 'animated', 'anime', 'cartoon', 'miyazaki', 'studio ghibli'],
    reply: "**Arcane** proves animation can be the most emotionally devastating format. **Spirited Away** is Miyazaki's masterpiece — there is no age limit on it.",
    suggestions: ['arcane-s1-2021', 'spirited-away-2001'],
  },
  {
    trigger: ['documentary', 'real', 'true story', 'based on', 'real events'],
    reply: "**Chernobyl** is the most precisely researched limited series ever made. **Icarus** starts as a cycling experiment and accidentally becomes a geopolitical thriller. **The Act of Killing** is unlike anything else ever filmed.",
    suggestions: ['chernobyl-2019', 'icarus-2017', 'the-act-of-killing-2012'],
  },
  {
    trigger: ['romance', 'love', 'relationship', 'heartbreak', 'dating', 'couple'],
    reply: "**Past Lives** is the most achingly precise love story in years. **Her** asks whether the form of love matters as much as the feeling. **Normal People** if you want something rawer and Irish.",
    suggestions: ['past-lives-2023', 'her-2013', 'fallen-leaves-2023'],
  },
  {
    trigger: ['short', 'quick', 'episode', '30 minutes', 'mini', 'limited'],
    reply: "Under 30 minutes: **Fleabag** (25 min), **Atlanta** (25 min), **The Good Place** (22 min). For limited series under 6 episodes: **Chernobyl**, **Station Eleven**, **Shogun**.",
    suggestions: ['fleabag-s1-2016', 'atlanta-s1-2016', 'chernobyl-2019'],
  },
  {
    trigger: ['classic', 'old', 'older', '90s', '2000s', 'timeless', 'all time'],
    reply: "**The Shawshank Redemption** remains the most beloved film on any ranking for a reason. **Pulp Fiction** still hits. **The Sopranos** invented modern prestige TV in 1999.",
    suggestions: ['the-shawshank-redemption-1994', 'pulp-fiction-1994', 'the-sopranos-s1-1999'],
  },
  {
    trigger: ['post apocalyptic', 'apocalypse', 'survival', 'zombie', 'pandemic', 'end of world'],
    reply: "**The Last of Us** is the bar for post-apocalyptic storytelling. **Station Eleven** takes a gentler approach — about what we preserve rather than what we lose. **Kingdom** is the best zombie series ever made and it's Korean.",
    suggestions: ['the-last-of-us-s1-2023', 'station-eleven-2021', 'kingdom-s1-2019'],
  },
]

const DEFAULT_RESPONSE = {
  reply: "Tell me more — what kind of mood are you in? Something intense and plot-driven, or slower and atmospheric? A film tonight or a series to start?",
  suggestions: [],
}

function getBotResponse(message) {
  const lower = message.toLowerCase()
  for (const r of MOCK_RESPONSES) {
    if (r.trigger.some(t => lower.includes(t))) return r
  }
  return DEFAULT_RESPONSE
}

export default function AskNexus({ isOpen, onClose, onContentSelect }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "Hey — I'm NEXUS. Tell me your mood, a vibe, or a genre. I'll find exactly what you need right now.",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 300)
  }, [isOpen])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: userMsg }])
    setLoading(true)

    let reply = ''
    let suggestions = []

    // Try real API first
    try {
      const res = await fetch('/api/v1/conversations/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'demo-user', message: userMsg, session_id: 'nexus-ui' }),
      })
      if (res.ok) {
        const data = await res.json()
        reply = data.reply
        suggestions = data.content_suggestions?.map(s => s.id) || []
      }
    } catch {}

    // Fall back to comprehensive mock responses
    if (!reply) {
      await new Promise(r => setTimeout(r, 600 + Math.random() * 400))
      const mock = getBotResponse(userMsg)
      reply = mock.reply
      suggestions = mock.suggestions || []
    }

    setLoading(false)
    setMessages(prev => [...prev, { role: 'assistant', text: reply, suggestions }])
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center md:items-center p-4">
      <div className="absolute inset-0 bg-nexus-bg/80 backdrop-blur-md" onClick={onClose} />

      <div className="relative w-full max-w-lg bg-nexus-surface border border-nexus-border rounded-2xl
        shadow-2xl flex flex-col overflow-hidden animate-fade-up" style={{ maxHeight: '80vh' }}>

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-nexus-border">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, rgba(0,212,255,0.2), rgba(255,0,128,0.15))' }}>
              <Sparkles size={16} className="text-nexus-cyan" />
            </div>
            <div>
              <div className="font-display font-600 text-nexus-text text-sm">Ask NEXUS</div>
              <div className="text-[10px] font-mono text-nexus-cyan">Conversational Discovery · MCP-Powered</div>
            </div>
          </div>
          <button onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-nexus-border/50 text-nexus-subtext transition-colors">
            <X size={16} />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
                m.role === 'user' ? 'nexus-chat-bubble-user text-nexus-text' : 'nexus-chat-bubble-ai text-nexus-subtext'
              }`}>
                {m.text.split(/(\*\*[^*]+\*\*)/).map((part, j) =>
                  part.startsWith('**')
                    ? <strong key={j} className="text-nexus-text font-medium">{part.slice(2,-2)}</strong>
                    : part
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="nexus-chat-bubble-ai rounded-xl px-4 py-3">
                <Loader size={14} className="text-nexus-cyan animate-spin" />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Suggested prompts */}
        <div className="px-5 pb-3 flex gap-2 flex-wrap">
          {[
            "Intense crime drama",
            "Slow burn atmospheric",
            "Something funny tonight",
            "Best international series",
            "Horror that actually scares me",
            "Mind-bending like Inception",
          ].map((p, i) => (
            <button key={i}
              className="text-xs px-3 py-1.5 rounded-full bg-nexus-border/40 text-nexus-subtext
                hover:bg-nexus-cyan/10 hover:text-nexus-cyan border border-nexus-border/60
                hover:border-nexus-cyan/30 transition-all duration-150"
              onClick={() => { setInput(p); inputRef.current?.focus() }}>
              {p}
            </button>
          ))}
        </div>

        {/* Input */}
        <div className="px-4 pb-4">
          <div className="flex items-center gap-2 bg-nexus-card border border-nexus-border rounded-xl px-4 py-2.5">
            <Brain size={14} className="text-nexus-cyan flex-none" />
            <input
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Intense crime drama, slow burn sci-fi, feel-good comedy…"
              className="flex-1 bg-transparent text-nexus-text text-sm placeholder-nexus-muted outline-none"
            />
            <button onClick={sendMessage} disabled={!input.trim() || loading}
              className="p-1.5 rounded-lg text-nexus-cyan hover:bg-nexus-cyan/10 disabled:opacity-30 transition-all">
              <Send size={14} />
            </button>
          </div>
          <p className="text-[10px] font-mono text-nexus-muted text-center mt-2">
            NEXUS searches across 120+ titles · MCP-orchestrated
          </p>
        </div>
      </div>
    </div>
  )
}
