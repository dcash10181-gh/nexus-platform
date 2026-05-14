/**
 * useDemo — sets up a pre-seeded demo user profile so visitors on the
 * live demo URL immediately see personalized results without signing up.
 *
 * When DEMO_MODE=true in API env, the /v1/demo/setup endpoint pre-seeds:
 *   - A demo user with a rich watch history (50 titles across genres)
 *   - A vector preference profile calibrated for diverse recommendations
 *   - A proactive agent notification ready to fire on page load
 */
import { useState, useEffect } from 'react'

const DEMO_USER_ID = 'demo-user-nexus'
const DEMO_API_KEY = 'nxk_trial_demo'  // Injected at build time for demo deployments

export function useDemo() {
  const [demoReady, setDemoReady]   = useState(false)
  const [demoError, setDemoError]   = useState(null)
  const [apiKey, setApiKey]         = useState(null)

  useEffect(() => {
    async function setup() {
      try {
        // Check if the API is in demo mode
        const root = await fetch('/api/').then(r => r.json()).catch(() => null)
        const isDemo = root?.license === 'trial' || import.meta.env.VITE_DEMO_MODE === 'true'

        if (isDemo) {
          // Try to get a demo key from the API
          const keyRes = await fetch('/api/v1/demo/key').catch(() => null)
          if (keyRes?.ok) {
            const { api_key } = await keyRes.json()
            setApiKey(api_key)
          } else {
            // Fall back to env-configured demo key
            setApiKey(import.meta.env.VITE_DEMO_API_KEY || DEMO_API_KEY)
          }
        }

        setDemoReady(true)
      } catch (e) {
        setDemoError(e.message)
        setDemoReady(true)  // Continue in mock mode even if setup fails
      }
    }

    setup()
  }, [])

  return { demoReady, demoError, demoUserId: DEMO_USER_ID, apiKey }
}
