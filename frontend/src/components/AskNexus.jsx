import React, { useState, useRef, useEffect } from 'react'
import { X, Send, Sparkles, Brain, Loader, Mic } from 'lucide-react'

const MOCK_RESPONSES = [
  {
    trigger: ['rainy', 'cozy', 'slow'],
    reply: "For a rainy evening, I'd lean toward **Blade Runner 2049** — Deakins' rain-soaked cinematography is exactly what you're after. Or if you want something shorter, **Dark** has that same atmospheric dread perfect for a stormy Tuesday.",
    suggestions: ['blade-runner-2049', 'dark-s1-2017'],
  },
  {
    trigger: ['funny', 'comedy', 'light'],
    reply: "Something warm but not vapid? **The Bear** is technically a drama but the dark comedy hits hard, and episodes are just 30 minutes. **Succession** also rewards multiple watches once you accept it's a comedy about people who deserve each other.",
    suggestions: ['the-bear-s1-2022', 'succession-s4-2023'],
  },
  {
    trigger: ['mind', 'twist', 'complex', 'inception'],
    reply: "The mind-bending tier: **Dark** is the most architecturally complex thing I can recommend — three seasons, four timelines, zero filler. If you want film-length, **Blade Runner 2049** rewards every rewatch differently.",
    suggestions: ['dark-s1-2017', 'blade-runner-2049'],
  },
  {
    trigger: ['action', 'epic', 'fantasy', 'game of thrones'],
    reply: "**Shōgun** is the prestige epic you've been looking for since Game of Thrones ended. **Dune: Part Two** is also essential if you want scope — Villeneuve's best film yet.",
    suggestions: ['shogun-2024', 'dune-part-two-2024'],
  },
  {
    trigger: ['work', 'office', 'corporate'],
    reply: "For workplace tension that feels viscerally real: **Severance** for psychological horror about modern work, **The Bear** for a kitchen that operates like a startup on fire, and **Succession** for corporate power at its most Shakespearean.",
    suggestions: ['severance-s1-2022', 'the-bear-s1-2022'],
  },
]

const DEFAULT_RESPONSE = {
  reply: "Based on your history, I'd suggest **Severance** — it matches your psychological sci-fi pattern almost perfectly. The sterile geometric aesthetic connects directly to your Blade Runner completion. Or tell me more about your mood tonight?",
  suggestions: ['severance-s1-2022', 'dark-s1-2017'],
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
      text: "Hey — I'm NEXUS. Tell me your mood, a vibe, or something you've loved. I'll find exactly what you need right now.",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 300)
    }
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

    // Try real API, fall back to mock
    let reply = ''
    let suggestions = []
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

    if (!reply) {
      await new Promise(r => setTimeout(r, 800 + Math.random() * 600))
      const mock = getBotResponse(userMsg)
      reply = mock.reply
      suggestions = mock.suggestions
    }

    setLoading(false)
    setMessages(prev => [...prev, { role: 'assistant', text: reply, suggestions }])
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center md:items-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-nexus-bg/80 backdrop-blur-md" onClick={onClose} />

      {/* Panel */}
      <div className="relative w-full max-w-lg bg-nexus-surface border border-nexus-border rounded-2xl
        shadow-2xl flex flex-col overflow-hidden animate-fade-up"
        style={{ maxHeight: '80vh' }}>

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
                {/* Parse **bold** */}
                {m.text.split(/(\*\*[^*]+\*\*)/).map((part, j) =>
                  part.startsWith('**') ? (
                    <strong key={j} className="text-nexus-text font-medium">{part.slice(2, -2)}</strong>
                  ) : part
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
            "Rainy evening, slow burn",
            "Mind-bending like Inception",
            "Short, intense, under 40 min",
            "Something my whole family can watch",
          ].map((p, i) => (
            <button key={i}
              className="text-xs px-3 py-1.5 rounded-full bg-nexus-border/40 text-nexus-subtext
                hover:bg-nexus-cyan/10 hover:text-nexus-cyan border border-nexus-border/60 hover:border-nexus-cyan/30
                transition-all duration-150"
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
              placeholder="Describe your mood, a vibe, a feeling…"
              className="flex-1 bg-transparent text-nexus-text text-sm placeholder-nexus-muted outline-none"
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              className="p-1.5 rounded-lg text-nexus-cyan hover:bg-nexus-cyan/10 disabled:opacity-30 transition-all"
            >
              <Send size={14} />
            </button>
          </div>
          <p className="text-[10px] font-mono text-nexus-muted text-center mt-2">
            NEXUS uses context from your entire viewing history · MCP-orchestrated
          </p>
        </div>
      </div>
    </div>
  )
}
