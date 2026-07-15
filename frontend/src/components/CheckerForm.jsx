import { useState } from 'react'
import CategoryTabs from './CategoryTabs.jsx'

const PLACEHOLDER =
  "Paste the message, offer, or link you're unsure about - for example:\n\n" +
  '"Congratulations! You have been selected for a remote position paying ' +
  '£450/week. To secure your start date, please send a £40 registration ' +
  'fee via gift card within 24 hours."'

export default function CheckerForm({ onSubmit, isChecking }) {
  const [content, setContent] = useState('')
  const [category, setCategory] = useState('other')

  function handleSubmit(event) {
    event.preventDefault()
    if (!content.trim() || isChecking) return
    onSubmit(content.trim(), category)
  }

  return (
    <form className="checker-form" onSubmit={handleSubmit} aria-label="Message checker">
      <span className="checker-form__label" id="category-label">
        What is this about?
      </span>
      <CategoryTabs value={category} onChange={setCategory} aria-labelledby="category-label" />

      <label className="checker-form__label checker-form__label--textarea" htmlFor="content">
        Paste it below
      </label>
      <textarea
        id="content"
        className="checker-form__textarea"
        placeholder={PLACEHOLDER}
        value={content}
        onChange={(event) => setContent(event.target.value)}
        rows={7}
        maxLength={5000}
        aria-describedby="hint-text"
      />

      <div className="checker-form__footer">
        <span className="checker-form__hint" id="hint-text">
          TrustCheck never says something is "safe" - only how risky it looks, and how to check it yourself.
        </span>
        <button
          type="submit"
          className="checker-form__submit"
          disabled={!content.trim() || isChecking}
          aria-busy={isChecking}
        >
          {isChecking ? 'Checking…' : 'Check this'}
        </button>
      </div>
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {isChecking ? 'Checking message. Please wait.' : ''}
      </div>
    </form>
  )
}
