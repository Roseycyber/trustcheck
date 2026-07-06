import { useState } from 'react'
import CheckerForm from './components/CheckerForm.jsx'
import VerdictCard from './components/VerdictCard.jsx'
import SafeVerifyBox from './components/SafeVerifyBox.jsx'
import HowItWorks from './components/HowItWorks.jsx'
import Principles from './components/Principles.jsx'
import { checkContent, TrustCheckApiError } from './api/client.js'

export default function App() {
  const [result, setResult] = useState(null)
  const [isChecking, setIsChecking] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(content, category) {
    setIsChecking(true)
    setError(null)
    try {
      const data = await checkContent(content, category)
      setResult(data)
    } catch (err) {
      setResult(null)
      setError(
        err instanceof TrustCheckApiError
          ? err.message
          : 'Something went wrong reaching TrustCheck. Please try again.',
      )
    } finally {
      setIsChecking(false)
    }
  }

  return (
    <div className="page">
      <header className="site-header">
        <span className="site-header__mark">TrustCheck</span>
        <a
          className="site-header__github"
          href="https://github.com/"
          target="_blank"
          rel="noreferrer"
        >
          View on GitHub
        </a>
      </header>

      <main>
        <section className="hero">
          <p className="hero__eyebrow">Not sure what you're looking at?</p>
          <h1 className="hero__headline">Check before you trust.</h1>
          <p className="hero__subhead">
            Paste a job offer, bank text, healthcare call, advert, or link below.
            TrustCheck gives you a cautious read and shows you how to verify it
            safely - it never tells you something is genuine.
          </p>

          <CheckerForm onSubmit={handleSubmit} isChecking={isChecking} />

          {error && (
            <p className="error-banner" role="alert">
              {error}
            </p>
          )}

          {result && (
            <div className="result" aria-live="polite">
              <VerdictCard
                verdict={result.verdict}
                verdictLabel={result.verdict_label}
                reasons={result.reasons}
              />
              <SafeVerifyBox safeVerify={result.safe_verify} />
            </div>
          )}
        </section>

        <HowItWorks />
        <Principles />
      </main>

      <footer className="site-footer">
        <p>
          TrustCheck is decision support, not confirmation. It does not replace
          your bank, employer, or healthcare provider - always verify
          independently before acting.
        </p>
        <p className="site-footer__meta">Open source, Apache 2.0 licensed.</p>
      </footer>
    </div>
  )
}
