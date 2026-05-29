import React, { useState, useRef, useEffect, useCallback } from 'react'
import { X, Send, Sparkles, Brain, Loader, Mic, MicOff, Volume2, VolumeX } from 'lucide-react'

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
const speechSupported = !!SpeechRecognition

const MOCK_RESPONSES = [
  { trigger: ['wire','breaking bad','sopranos','crime drama','intense crime','mob','cartel','drug','gangster','crime'], reply: "For intense crime drama, **The Wire** is the gold standard. **Breaking Bad** is the tightest character arc on television. **The Sopranos** invented the template. All three reward patience.", suggestions: ['the-wire-s1-2002','breaking-bad-s1-2008','the-sopranos-s1-1999'], primary: { id: 'the-wire-s1-2002', title: 'The Wire' } },
  { trigger: ['thriller','suspense','tension','edge of seat','mindhunter','gone girl','nightcrawler'], reply: "**Mindhunter** builds dread through conversation alone. **Gone Girl** is Fincher at his most precise. **Nightcrawler** gives you a protagonist so unsettling you feel complicit.", suggestions: ['mindhunter-s1-2017','gone-girl-2014','nightcrawler-2014'], primary: { id: 'mindhunter-s1-2017', title: 'Mindhunter' } },
  { trigger: ['horror','scary','frightening','disturbing','creepy','midsommar','hereditary'], reply: "**Hereditary** is the most disturbing family horror in years. **Midsommar** does horror in full sunlight. **Get Out** wraps its scares in something smarter.", suggestions: ['hereditary-2018','midsommar-2019','get-out-2017'], primary: { id: 'hereditary-2018', title: 'Hereditary' } },
  { trigger: ['comedy','funny','laugh','light','lighthearted','feel good','feel-good','warm','uplifting'], reply: "**Fleabag** is the sharpest comedy-drama of the decade. **Ted Lasso** is radical optimism as entertainment. **The Good Place** hides genuine philosophy in a sitcom.", suggestions: ['fleabag-s1-2016','ted-lasso-s1-2020','the-good-place-s1-2016'], primary: { id: 'fleabag-s1-2016', title: 'Fleabag' } },
  { trigger: ['international','foreign','subtitles','korean','spanish','french','german','squid game','money heist'], reply: "**Squid Game** earns every bit of its reputation. **Money Heist** is pure propulsive entertainment. **Parasite** and **Dark** are the two best arguments for subtitles.", suggestions: ['squid-game-s1-2021','money-heist-s1-2017','parasite-2019'], primary: { id: 'squid-game-s1-2021', title: 'Squid Game' } },
  { trigger: ['sci-fi','science fiction','futuristic','space','ai','artificial intelligence','robot','technology'], reply: "**Severance** for corporate body horror. **Mr. Robot** for hacker paranoia that gets the tech right. **Ex Machina** for AI consciousness in 108 tight minutes.", suggestions: ['severance-s1-2022','mr-robot-s1-2015','ex-machina-2014'], primary: { id: 'severance-s1-2022', title: 'Severance' } },
  { trigger: ['rainy','cozy','quiet','slow','slow burn','atmospheric','meditative','melancholic'], reply: "**Blade Runner 2049** is the most beautiful film of the decade. **Aftersun** for something smaller and devastating. **Past Lives** will wreck you in the best way.", suggestions: ['blade-runner-2049','aftersun-2022','past-lives-2023'], primary: { id: 'blade-runner-2049', title: 'Blade Runner 2049' } },
  { trigger: ['mind','mindbending','mind-bending','twist','complex','puzzle','inception','confusing','layers'], reply: "**Dark** is the most complex thing on television — three seasons, four timelines. **Inception** for film-length. **Arrival** reframes everything in its final act.", suggestions: ['dark-s1-2017','inception-2010','arrival-2016'], primary: { id: 'dark-s1-2017', title: 'Dark' } },
  { trigger: ['action','epic','spectacle','blockbuster','explosive'], reply: "**Mad Max: Fury Road** is the greatest action film of the 21st century. **Dune: Part Two** for scope. **Mission Impossible Fallout** for practical stunt craft.", suggestions: ['mad-max-fury-road-2015','dune-part-two-2024','mission-impossible-fallout-2018'], primary: { id: 'mad-max-fury-road-2015', title: 'Mad Max: Fury Road' } },
  { trigger: ['fantasy','medieval','dragons','game of thrones','magic'], reply: "**House of the Dragon** recovered the prestige fantasy crown. **Shogun** is equally epic but grounded in real history. **Arcane** is the best animated fantasy series ever made.", suggestions: ['house-of-dragon-s1-2022','shogun-2024','arcane-s1-2021'], primary: { id: 'house-of-dragon-s1-2022', title: 'House of the Dragon' } },
  { trigger: ['work','office','corporate','business','power','politics'], reply: "**Severance** for the existential horror of work. **Succession** for corporate power at Shakespearean scale. **The Bear** if you want the kitchen as a pressure cooker.", suggestions: ['severance-s1-2022','succession-s4-2023','the-bear-s1-2022'], primary: { id: 'succession-s4-2023', title: 'Succession' } },
  { trigger: ['true crime','investigation','detective','mystery','murder','serial killer','police'], reply: "**Mindhunter** for FBI profiling done right. **True Detective: Night Country** for arctic noir. **Slow Horses** for British intelligence.", suggestions: ['mindhunter-s1-2017','true-detective-s4-2024','slow-horses-s1-2022'], primary: { id: 'mindhunter-s1-2017', title: 'Mindhunter' } },
  { trigger: ['animation','animated','anime','cartoon','miyazaki'], reply: "**Arcane** proves animation can be the most emotionally devastating format. **Spirited Away** is Miyazaki's masterpiece — no age limit.", suggestions: ['arcane-s1-2021','spirited-away-2001'], primary: { id: 'arcane-s1-2021', title: 'Arcane' } },
  { trigger: ['documentary','real','true story','based on','real events'], reply: "**Chernobyl** is the most precisely researched limited series ever made. **Icarus** starts as a cycling experiment and becomes a geopolitical thriller.", suggestions: ['chernobyl-2019','icarus-2017'], primary: { id: 'chernobyl-2019', title: 'Chernobyl' } },
  { trigger: ['romance','love','relationship','heartbreak','dating'], reply: "**Past Lives** is the most achingly precise love story in years. **Normal People** is rawer and Irish. **Eternal Sunshine** wraps sci-fi around heartbreak.", suggestions: ['past-lives-2023','normal-people-2020','eternal-sunshine-2004'], primary: { id: 'past-lives-2023', title: 'Past Lives' } },
  { trigger: ['short','quick','30 minutes','mini','limited','brief'], reply: "Under 30 minutes: **Fleabag** (25 min), **Atlanta** (25 min), **The Good Place** (22 min). Limited series under 6 episodes: **Chernobyl**, **Shogun**, **Station Eleven**.", suggestions: ['fleabag-s1-2016','atlanta-s1-2016','chernobyl-2019'], primary: { id: 'fleabag-s1-2016', title: 'Fleabag' } },
  { trigger: ['classic','old','older','90s','2000s','timeless','all time'], reply: "**The Shawshank Redemption** remains the most beloved film for a reason. **Pulp Fiction** still hits. **The Sopranos** invented modern prestige TV in 1999.", suggestions: ['the-shawshank-redemption-1994','pulp-fiction-1994','the-sopranos-s1-1999'], primary: { id: 'the-shawshank-redemption-1994', title: 'The Shawshank Redemption' } },
  { trigger: ['post apocalyptic','apocalypse','survival','zombie','pandemic'], reply: "**The Last of Us** is the bar for post-apocalyptic storytelling. **Station Eleven** is about what we preserve rather than what we lose. **Kingdom** is the best zombie series ever made.", suggestions: ['the-last-of-us-s1-2023','station-eleven-2021','kingdom-s1-2019'], primary: { id: 'the-last-of-us-s1-2023', title: 'The Last of Us' } },
]

const YES_WORDS = ['yes','yeah','yep','sure','ok','okay','open','show','let me see','absolutely','definitely','go ahead','show me','yes please']
const NO_WORDS  = ['no','nope','nah','not really','pass','skip','never mind','nevermind','no thanks']

const DEFAULT_RESPONSE = { reply: "Tell me more — what kind of mood are you in? Something intense, slow and atmospheric, or funny? A film or a series?", suggestions: [], primary: null }

function getBotResponse(msg) {
  const lower = msg.toLowerCase()
  for (const r of MOCK_RESPONSES) {
    if (r.trigger.some(t => lower.includes(t))) return r
  }
  return DEFAULT_RESPONSE
}

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const utter = new SpeechSynthesisUtterance(text.replace(/\*\*/g,'').replace(/\n/g,' '))
  utter.rate = 1.05
  const voices = window.speechSynthesis.getVoices()
  const pref = voices.find(v => v.name.includes('Samantha') || v.name.includes('Google US English') || v.name.includes('Alex'))
  if (pref) utter.voice = pref
  window.speechSynthesis.speak(utter)
}

export default function AskNexus({ isOpen, onClose, onContentSelect, allContent = [] }) {
  const [messages, setMessages]             = useState([{ role: 'assistant', text: speechSupported ? "Hey — I'm NEXUS. Tell me your mood, or tap the mic and just speak." : "Hey — I'm NEXUS. Tell me your mood, a vibe, or a genre." }])
  const [input, setInput]                   = useState('')
  const [loading, setLoading]               = useState(false)
  const [listening, setListening]           = useState(false)
  const [voiceReply, setVoiceReply]         = useState(false)
  const [transcript, setTranscript]         = useState('')
  const [noSpeech, setNoSpeech]             = useState(false)
  const [awaitingConfirm, setAwaitingConfirm] = useState(false)
  const [pendingTitle, setPendingTitle]     = useState(null)

  const bottomRef       = useRef(null)
  const inputRef        = useRef(null)
  const recognizer      = useRef(null)
  const autoSubmitTimer = useRef(null)

  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 300)
    return () => { stopListening(); window.speechSynthesis?.cancel(); clearTimeout(autoSubmitTimer.current) }
  }, [isOpen])

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const stopListening = useCallback(() => {
    clearTimeout(autoSubmitTimer.current)
    recognizer.current?.stop()
    setListening(false)
    setTranscript('')
  }, [])

  const startListening = useCallback(() => {
    if (!speechSupported) return
    setNoSpeech(false); setTranscript('')
    const rec = new SpeechRecognition()
    rec.continuous = false; rec.interimResults = true; rec.lang = 'en-US'
    rec.onstart = () => setListening(true)
    rec.onresult = (e) => {
      let interim = '', final = ''
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) final += e.results[i][0].transcript
        else interim += e.results[i][0].transcript
      }
      setTranscript(final || interim)
      if (final) {
        setInput(final)
        clearTimeout(autoSubmitTimer.current)
        // Auto-submit after 1.2 second pause — natural speech end detection
        autoSubmitTimer.current = setTimeout(() => {
          handleSend(final)
          stopListening()
        }, 1200)
      }
    }
    rec.onerror = (e) => { setListening(false); if (e.error === 'no-speech') setNoSpeech(true) }
    rec.onend   = () => { setListening(false); setTranscript('') }
    recognizer.current = rec
    rec.start()
  }, [stopListening])

  const handleSend = useCallback(async (overrideText) => {
    const userMsg = (overrideText || input).trim()
    if (!userMsg || loading) return
    setInput(''); setTranscript('')
    setMessages(prev => [...prev, { role: 'user', text: userMsg }])
    setLoading(true)
    const lower = userMsg.toLowerCase()

    // Handle yes/no confirmation response
    if (awaitingConfirm && pendingTitle) {
      setAwaitingConfirm(false)
      if (YES_WORDS.some(w => lower.includes(w))) {
        const item = allContent.find(c => c.id === pendingTitle.id)
        if (item && onContentSelect) onContentSelect(item)
        const reply = `Opening **${pendingTitle.title}** now. Enjoy!`
        setLoading(false)
        setMessages(prev => [...prev, { role: 'assistant', text: reply }])
        if (voiceReply) speak(reply)
        setPendingTitle(null)
        return
      }
      if (NO_WORDS.some(w => lower.includes(w))) {
        const reply = "No problem! What else can I find for you?"
        setLoading(false)
        setMessages(prev => [...prev, { role: 'assistant', text: reply }])
        if (voiceReply) speak(reply)
        setPendingTitle(null)
        return
      }
      setPendingTitle(null)
    }

    // Normal query
    let reply = '', suggestions = [], primary = null
    try {
      const res = await fetch('/api/v1/conversations/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: 'demo-user', message: userMsg, session_id: 'nexus-ui' }) })
      if (res.ok) { const d = await res.json(); reply = d.reply; suggestions = d.content_suggestions?.map(s => s.id) || [] }
    } catch {}

    if (!reply) {
      await new Promise(r => setTimeout(r, 500 + Math.random() * 300))
      const mock = getBotResponse(userMsg)
      reply = mock.reply; suggestions = mock.suggestions || []; primary = mock.primary || null
    }

    setLoading(false)
    setMessages(prev => [...prev, { role: 'assistant', text: reply, suggestions }])
    if (voiceReply) speak(reply)

    if (primary) {
      setPendingTitle(primary)
      setTimeout(() => {
        const confirmMsg = `Would you like to open **${primary.title}**?`
        setMessages(prev => [...prev, { role: 'assistant', text: confirmMsg, isConfirm: true }])
        if (voiceReply) speak(`Would you like to open ${primary.title}?`)
        setAwaitingConfirm(true)
      }, 800)
    }
  }, [input, loading, awaitingConfirm, pendingTitle, allContent, onContentSelect, voiceReply])

  const handleKey = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center md:items-center p-4">
      <div className="absolute inset-0 bg-nexus-bg/80 backdrop-blur-md" onClick={onClose} />
      <div className="relative w-full max-w-lg bg-nexus-surface border border-nexus-border rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-fade-up" style={{ maxHeight: '84vh' }}>

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-nexus-border">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, rgba(0,212,255,0.2), rgba(255,0,128,0.15))' }}>
              <Sparkles size={16} className="text-nexus-cyan" />
            </div>
            <div>
              <div className="font-display font-600 text-nexus-text text-sm">Ask NEXUS</div>
              <div className="text-[10px] font-mono text-nexus-cyan flex items-center gap-1.5">
                Conversational Discovery {speechSupported && <span className="text-nexus-green">· Voice Ready</span>}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {window.speechSynthesis && (
              <button onClick={() => { setVoiceReply(v => !v); window.speechSynthesis.cancel() }} title={voiceReply ? 'Mute' : 'Read aloud'}
                className={`p-1.5 rounded-lg transition-colors ${voiceReply ? 'text-nexus-cyan bg-nexus-cyan/10 border border-nexus-cyan/30' : 'text-nexus-subtext hover:bg-nexus-border/50'}`}>
                {voiceReply ? <Volume2 size={15} /> : <VolumeX size={15} />}
              </button>
            )}
            <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-nexus-border/50 text-nexus-subtext transition-colors"><X size={16} /></button>
          </div>
        </div>

        {/* Listening indicator */}
        {listening && (
          <div className="px-5 py-2.5 bg-nexus-cyan/5 border-b border-nexus-cyan/20 flex items-center gap-3">
            <div className="flex gap-[3px] items-end h-4 flex-none">
              {[0.4,0.7,1,0.8,0.5].map((h,i) => (
                <div key={i} className="w-[3px] bg-nexus-cyan rounded-full animate-pulse" style={{ height: `${h*100}%`, animationDelay: `${i*0.12}s` }} />
              ))}
            </div>
            <span className="text-nexus-cyan text-xs font-mono truncate flex-1">{transcript || 'Listening… speak now'}</span>
            <span className="text-nexus-muted text-[10px] font-mono flex-none">auto-sends on pause</span>
          </div>
        )}
        {noSpeech && (
          <div className="px-5 py-2 bg-nexus-amber/5 border-b border-nexus-amber/20">
            <p className="text-nexus-amber text-xs">No speech detected — try again or type your request.</p>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-xl px-4 py-3 text-sm leading-relaxed ${m.isConfirm ? 'bg-nexus-cyan/10 border border-nexus-cyan/25 text-nexus-text' : m.role === 'user' ? 'nexus-chat-bubble-user text-nexus-text' : 'nexus-chat-bubble-ai text-nexus-subtext'}`}>
                {m.text.split(/(\*\*[^*]+\*\*)/).map((part, j) => part.startsWith('**') ? <strong key={j} className="text-nexus-text font-medium">{part.slice(2,-2)}</strong> : part)}
                {m.isConfirm && (
                  <div className="flex gap-2 mt-3">
                    <button onClick={() => handleSend('yes')} className="px-4 py-1.5 rounded-lg bg-nexus-cyan text-nexus-bg text-xs font-medium hover:bg-nexus-cyan-dim transition-colors">Yes, open it</button>
                    <button onClick={() => handleSend('no')} className="px-4 py-1.5 rounded-lg bg-nexus-border/50 text-nexus-subtext text-xs font-medium hover:bg-nexus-border transition-colors">No thanks</button>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="nexus-chat-bubble-ai rounded-xl px-4 py-3"><Loader size={14} className="text-nexus-cyan animate-spin" /></div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Suggested prompts */}
        {!awaitingConfirm && (
          <div className="px-5 pb-3 flex gap-2 flex-wrap">
            {["Intense crime drama","Slow burn atmospheric","Something funny","Best international","Horror that scares me","Mind-bending sci-fi"].map((p,i) => (
              <button key={i} className="text-xs px-3 py-1.5 rounded-full bg-nexus-border/40 text-nexus-subtext hover:bg-nexus-cyan/10 hover:text-nexus-cyan border border-nexus-border/60 hover:border-nexus-cyan/30 transition-all" onClick={() => handleSend(p)}>{p}</button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="px-4 pb-4">
          <div className={`flex items-center gap-2 bg-nexus-card border rounded-xl px-4 py-2.5 transition-colors ${listening ? 'border-nexus-magenta/50' : awaitingConfirm ? 'border-nexus-cyan/50' : 'border-nexus-border'}`}>
            <Brain size={14} className="text-nexus-cyan flex-none" />
            <input ref={inputRef} value={listening ? (transcript||'') : input} onChange={e => { if (!listening) setInput(e.target.value) }} onKeyDown={handleKey}
              placeholder={listening ? 'Speak now — auto-sends on pause…' : awaitingConfirm ? 'Say or type "yes" / "no"…' : 'Intense crime drama, slow burn sci-fi…'}
              className="flex-1 bg-transparent text-nexus-text text-sm placeholder-nexus-muted outline-none" readOnly={listening} />
            {speechSupported && (
              <button onClick={() => listening ? stopListening() : startListening()} title={listening ? 'Stop' : 'Speak'}
                className={`p-1.5 rounded-lg transition-all flex-none ${listening ? 'text-nexus-magenta bg-nexus-magenta/10 border border-nexus-magenta/30 animate-pulse' : 'text-nexus-subtext hover:text-nexus-cyan hover:bg-nexus-cyan/10'}`}>
                {listening ? <MicOff size={14} /> : <Mic size={14} />}
              </button>
            )}
            <button onClick={() => handleSend()} disabled={(!input.trim()&&!transcript)||loading}
              className="p-1.5 rounded-lg text-nexus-cyan hover:bg-nexus-cyan/10 disabled:opacity-30 transition-all flex-none">
              <Send size={14} />
            </button>
          </div>
          <p className="text-[10px] font-mono text-nexus-muted text-center mt-2">
            {speechSupported ? 'Pause to auto-send · 🔊 for voice responses · 81 titles' : 'Chrome / Safari for voice input · 81 titles'}
          </p>
        </div>
      </div>
    </div>
  )
}
