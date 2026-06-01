// matchEngine.js
// Computes a NEXUS match score and the per-signal breakdown that backs it,
// by comparing a title's DNA against a user taste profile. This replaces the
// hardcoded "91% / 0 active signals" fallback that previously appeared whenever
// a title had no precomputed `signals` array (which was every title).
//
// Design notes:
// - Pure functions, no React, no side effects -> trivially unit-testable.
// - Every signal is derived ONLY from fields that exist on all 98 catalog
//   titles (pacing, thematic_tags, genres, visual_style, audio_mood), so the
//   panel never falls back to a fabricated number.
// - The overall score is a weighted blend of signal strengths, squashed into a
//   believable 0.60–0.97 band. We deliberately avoid 100% (reads as fake) and
//   avoid a flat constant (the original bug).

// --- Mock user taste profile -------------------------------------------------
// This is a DEMO profile. It is honest to label it as such: the scoring math
// below is real, the inputs are a representative persona. In production this
// object would be assembled from watch history / explicit ratings.
export const DEMO_USER_PROFILE = {
  // Genres the user gravitates toward, weighted 0..1 by strength of preference.
  genreAffinity: {
    Drama: 0.9, Thriller: 0.8, 'Sci-Fi': 0.85, Crime: 0.75,
    Mystery: 0.7, History: 0.5, Horror: 0.4, Comedy: 0.45,
  },
  // Preferred pacing on the same 0..1 scale catalog DNA uses. This persona
  // skews slow-burn/measured (matches the "slow-burn psychological" copy).
  preferredPacing: 0.45,
  // Themes that resonate, weighted 0..1.
  resonantThemes: {
    identity: 0.9, memory: 0.85, surveillance: 0.8, 'institutional failure': 0.8,
    grief: 0.75, ambition: 0.7, isolation: 0.7, transformation: 0.65,
    class: 0.6, survival: 0.55, family: 0.5,
  },
  // Style keywords the user responds to (matched against visual_style + audio_mood).
  styleKeywords: ['atmospheric', 'documentary', 'tense', 'noir', 'sparse', 'neo', 'psychological', 'slow'],
}

// --- Helpers -----------------------------------------------------------------

// Jaccard-ish weighted overlap: sum of profile weights for matched keys,
// normalized by the best achievable given how many tags the title has.
function weightedOverlap(items, weightMap) {
  if (!items || items.length === 0) return 0
  let got = 0
  let best = 0
  // Normalize against the strongest `items.length` preferences the user has,
  // so a 3-tag title isn't penalized for not covering the whole profile.
  const topWeights = Object.values(weightMap).sort((a, b) => b - a).slice(0, items.length)
  best = topWeights.reduce((s, w) => s + w, 0) || 1
  for (const it of items) {
    if (weightMap[it] != null) got += weightMap[it]
  }
  return Math.min(1, got / best)
}

// Keyword overlap for free-text style fields (visual_style, audio_mood).
function keywordMatch(text, keywords) {
  if (!text) return 0
  const lower = text.toLowerCase()
  const hits = keywords.filter(k => lower.includes(k)).length
  // 2 keyword hits in a short style phrase is already a strong match.
  return Math.min(1, hits / 2)
}

// Closeness on the 0..1 pacing axis -> 1 when identical, 0 when maximally apart.
function pacingFit(titlePacing, preferred) {
  if (titlePacing == null) return 0.5
  return 1 - Math.abs(titlePacing - preferred)
}

// --- Public API --------------------------------------------------------------

// Returns an array of signal objects shaped exactly how ExplainabilityPanel
// expects: { name, weight (0..1), detail, icon }.
export function computeSignals(content, profile = DEMO_USER_PROFILE) {
  if (!content || !content.dna) return []
  const dna = content.dna
  const genres = content.genres || []
  const tags = dna.thematic_tags || []
  const styleText = `${dna.visual_style || ''} ${dna.audio_mood || ''}`

  const genreScore = weightedOverlap(genres, profile.genreAffinity)
  const pace = pacingFit(dna.pacing, profile.preferredPacing)
  const themeScore = weightedOverlap(tags, profile.resonantThemes)
  const styleScore = keywordMatch(styleText, profile.styleKeywords)

  // Build human-readable detail strings from the ACTUAL matched data, so the
  // reasoning is specific to the title (no more generic Villeneuve line).
  const matchedGenres = genres.filter(g => profile.genreAffinity[g] != null)
  const matchedThemes = tags.filter(t => profile.resonantThemes[t] != null)
  const paceLabel = dna.pacing < 0.35 ? 'slow-burn' : dna.pacing < 0.6 ? 'measured' : dna.pacing < 0.8 ? 'propulsive' : 'relentless'

  const signals = [
    {
      name: 'Genre Affinity',
      weight: genreScore,
      icon: 'film',
      detail: matchedGenres.length
        ? `Matches your taste for ${matchedGenres.slice(0, 2).join(' & ')}.`
        : 'Outside your usual genres — exploratory pick.',
    },
    {
      name: 'Pacing Fit',
      weight: pace,
      icon: 'trending-up',
      detail: `${paceLabel} rhythm vs your preferred measured pace.`,
    },
    {
      name: 'Thematic Resonance',
      weight: themeScore,
      icon: 'brain',
      detail: matchedThemes.length
        ? `Explores ${matchedThemes.slice(0, 2).join(' & ')} — themes you return to.`
        : 'New thematic territory for your profile.',
    },
    {
      name: 'Style Match',
      weight: styleScore,
      icon: 'eye',
      detail: dna.visual_style
        ? `${dna.visual_style} visual style.`
        : 'Style signal unavailable.',
    },
  ]

  // Sort strongest-first so the panel leads with the best reason.
  return signals.sort((a, b) => b.weight - a.weight)
}

// Overall score: weighted blend of the four signals, squashed to a believable
// 0.60–0.97 band. Weights reflect how predictive each axis is of enjoyment.
export function computeMatchScore(content, profile = DEMO_USER_PROFILE) {
  const signals = computeSignals(content, profile)
  if (signals.length === 0) return 0
  const byName = Object.fromEntries(signals.map(s => [s.name, s.weight]))
  const blended =
    0.35 * (byName['Genre Affinity'] || 0) +
    0.20 * (byName['Pacing Fit'] || 0) +
    0.30 * (byName['Thematic Resonance'] || 0) +
    0.15 * (byName['Style Match'] || 0)
  // Map 0..1 -> 0.60..0.97 so even a weak match shows a plausible floor and a
  // perfect one never claims 100%.
  return 0.60 + blended * 0.37
}

// Convenience: attach computed signals + score to a content object without
// mutating the original (returns a shallow copy).
export function withMatch(content, profile = DEMO_USER_PROFILE) {
  if (!content) return content
  return {
    ...content,
    signals: computeSignals(content, profile),
    matchScore: computeMatchScore(content, profile),
  }
}
