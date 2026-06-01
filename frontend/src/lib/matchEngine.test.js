// matchEngine.test.js
// Regression coverage for the NEXUS match scoring engine. Guards against a
// return to the original bug (fabricated flat score, zero signals).
//
// Run with: npx vitest run src/lib/matchEngine.test.js
// (or adapt to your existing test runner; assertions are framework-agnostic.)

import { describe, it, expect } from 'vitest'
import { computeSignals, computeMatchScore, withMatch } from './matchEngine.js'

const TITLE = {
  title: 'The Wire',
  genres: ['Drama', 'Crime'],
  dna: {
    pacing: 0.45,
    thematic_tags: ['surveillance', 'class', 'institutional failure'],
    visual_style: 'gritty documentary',
    audio_mood: 'urban sparse',
  },
}

describe('computeSignals', () => {
  it('returns exactly 4 signals for a complete title', () => {
    expect(computeSignals(TITLE)).toHaveLength(4)
  })

  it('produces weights within 0..1', () => {
    for (const s of computeSignals(TITLE)) {
      expect(s.weight).toBeGreaterThanOrEqual(0)
      expect(s.weight).toBeLessThanOrEqual(1)
    }
  })

  it('sorts signals strongest-first', () => {
    const s = computeSignals(TITLE)
    for (let i = 1; i < s.length; i++) {
      expect(s[i - 1].weight).toBeGreaterThanOrEqual(s[i].weight)
    }
  })

  it('always attaches a non-empty human-readable detail', () => {
    for (const s of computeSignals(TITLE)) {
      expect(typeof s.detail).toBe('string')
      expect(s.detail.length).toBeGreaterThan(0)
    }
  })

  it('returns no signals for null or DNA-less content', () => {
    expect(computeSignals(null)).toHaveLength(0)
    expect(computeSignals({ genres: ['Drama'] })).toHaveLength(0)
  })
})

describe('computeMatchScore', () => {
  it('maps into the believable 0.60..0.97 band', () => {
    const score = computeMatchScore(TITLE)
    expect(score).toBeGreaterThanOrEqual(0.60)
    expect(score).toBeLessThanOrEqual(0.97)
  })

  it('never returns the old fabricated flat value across varied titles', () => {
    const weak = computeMatchScore({
      genres: ['Western'],
      dna: { pacing: 0.95, thematic_tags: ['rodeo'], visual_style: 'x', audio_mood: 'y' },
    })
    const strong = computeMatchScore(TITLE)
    // Different inputs must yield different scores (the original bug returned 91 for everything).
    expect(weak).not.toBeCloseTo(strong, 2)
    // And nothing claims a perfect 100%.
    expect(strong).toBeLessThan(1)
  })
})

describe('withMatch', () => {
  it('attaches signals + matchScore without mutating the original', () => {
    const enriched = withMatch(TITLE)
    expect(enriched.signals.length).toBe(4)
    expect(enriched.matchScore).toBeGreaterThan(0)
    expect(TITLE.signals).toBeUndefined() // original untouched
  })
})
