const STEPS = [
  {
    title: 'Paste what you received',
    body: 'A job offer, a bank text, a clinic call, an advert, or a link - whatever you\'re unsure about.',
  },
  {
    title: 'Get a cautious read',
    body: 'One of three verdicts, plus up to two plain-language reasons. Never a claim that something is safe.',
  },
  {
    title: 'Verify through an official channel',
    body: "TrustCheck points you to the organisation's own published details - not the ones in the message.",
  },
]

export default function HowItWorks() {
  return (
    <section className="how-it-works" aria-labelledby="how-it-works-heading">
      <h2 id="how-it-works-heading" className="section-heading">
        How it works
      </h2>
      <ol className="how-it-works__steps">
        {STEPS.map((step, index) => (
          <li key={step.title} className="how-it-works__step">
            <span className="how-it-works__index">{String(index + 1).padStart(2, '0')}</span>
            <h3>{step.title}</h3>
            <p>{step.body}</p>
          </li>
        ))}
      </ol>
    </section>
  )
}
