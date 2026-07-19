import Stamp from './Stamp.jsx'

export default function VerdictCard({ verdictLabel, verdict, reasons }) {
  return (
    <div
      className={`verdict-card verdict-card--${verdict}`}
      role="alert"
      aria-live="polite"
      aria-atomic="true"
    >
      <div className="verdict-card__stamp">
        <Stamp variant={verdict} />
      </div>
      <div className="verdict-card__body">
        <p className="verdict-card__eyebrow">TrustCheck's read</p>
        <h2 className="verdict-card__label">{verdictLabel}</h2>
        <ul className="verdict-card__reasons" aria-label="Reasons for this verdict">
          {reasons.map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
