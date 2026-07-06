const VARIANT_LABEL = {
  verify: 'VERIFY',
  suspicious: 'CAUTION',
  high_risk: 'HIGH RISK',
}

/**
 * The one deliberate flourish in this UI: an ink-stamp seal, because the
 * product's entire job is "go check this against an official source" -
 * literally a stamp of provenance, not a decoration borrowed from
 * elsewhere. Kept to a single instance per result so it stays a
 * signature, not a pattern.
 */
export default function Stamp({ variant = 'verify' }) {
  const label = VARIANT_LABEL[variant] || VARIANT_LABEL.verify

  return (
    <svg
      viewBox="0 0 160 160"
      className={`stamp stamp--${variant}`}
      role="img"
      aria-label={`TrustCheck verification stamp: ${label}`}
    >
      <defs>
        <path
          id="stampRing"
          d="M 80,80 m -60,0 a 60,60 0 1,1 120,0 a 60,60 0 1,1 -120,0"
        />
      </defs>
      <circle cx="80" cy="80" r="72" className="stamp__ring-outer" />
      <circle cx="80" cy="80" r="52" className="stamp__ring-inner" />
      <text className="stamp__ring-text">
        <textPath href="#stampRing" startOffset="0%">
          TRUSTCHECK &#8226; VERIFY INDEPENDENTLY &#8226; TRUSTCHECK &#8226; VERIFY INDEPENDENTLY &#8226;
        </textPath>
      </text>
      <text x="80" y="76" textAnchor="middle" className="stamp__label">
        {label}
      </text>
      <text x="80" y="94" textAnchor="middle" className="stamp__sublabel">
        NOT CONFIRMED
      </text>
    </svg>
  )
}
