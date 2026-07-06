const PRINCIPLES = [
  {
    wont: "Say something is \u201Csafe,\u201D \u201Cgenuine,\u201D or \u201Cverified.\u201D",
    instead: 'Three honest verdicts, always paired with a way to check yourself.',
  },
  {
    wont: 'Use a contact detail, link, or number from the message you pasted.',
    instead: "Route you to the organisation's own published channels only.",
  },
  {
    wont: 'Hide behind an unexplained score or a black-box model.',
    instead: 'Name the specific wording behind every verdict, in plain language.',
  },
]

export default function Principles() {
  return (
    <section className="principles" aria-labelledby="principles-heading">
      <h2 id="principles-heading" className="section-heading">
        What TrustCheck will never do
      </h2>
      <div className="principles__grid">
        {PRINCIPLES.map((principle) => (
          <div className="principles__card" key={principle.wont}>
            <p className="principles__wont">
              <span aria-hidden="true">✕</span> {principle.wont}
            </p>
            <p className="principles__instead">
              <span aria-hidden="true">→</span> {principle.instead}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}
