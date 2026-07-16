export default function SafeVerifyBox({ safeVerify }) {
  if (!safeVerify) return null

  return (
    <div className="safe-verify" aria-labelledby="safe-verify-heading">
      <h3 id="safe-verify-heading" className="safe-verify__heading">{safeVerify.heading}</h3>
      <p className="safe-verify__instructions">{safeVerify.instructions}</p>

      {safeVerify.entries.length > 0 && (
        <dl className="safe-verify__entries" aria-label="Verified contact details">
          {safeVerify.entries.map((entry) => (
            <div className="safe-verify__entry" key={entry.label}>
              <dt>{entry.label}</dt>
              <dd>{entry.value}</dd>
            </div>
          ))}
        </dl>
      )}

      <p className="safe-verify__disclaimer">{safeVerify.disclaimer}</p>
    </div>
  )
}
