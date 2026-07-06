# Safety principles

TrustCheck's credibility depends on restraint. These rules are treated as
product requirements, not aspirations - each one is backed by a test in
`backend/tests/` so a future change can't quietly weaken them.

## 1. Never confirm legitimacy

TrustCheck has exactly three verdicts: `verify`, `suspicious`, `high_risk`.
There is no "safe" or "genuine" state, in the code or in the copy.

- Enforced by: `test_risk_engine.py::test_no_verdict_label_ever_claims_safety`
- Enforced by: `test_safe_verify.py::test_every_category_disclaimer_avoids_confirming_legitimacy`

## 2. Never reuse a sender-supplied contact detail

Every Safe Verify response is built from a contact directory TrustCheck
maintains itself (see `safe_verify.py`), never from anything extracted
out of the pasted content. If a category can't be confidently matched to
a known organisation, TrustCheck falls back to general guidance rather
than guessing.

## 3. Explanations must be human-readable, not a score

Every risk signal in `risk_engine.py` carries a plain-language reason.
There is no numeric "probability of scam" surfaced to the user - the
verdict is a band (verify / suspicious / high risk), and the reasons
are the actual wording that triggered it, capped at two so the person
isn't overwhelmed.

## 4. Say what's real and what's a placeholder

Anything not yet backed by a live data source says so in its own
disclaimer (see the job-offer and default Safe Verify responses). A
mocked lookup is never presented as if it were a verified result.

## 5. A sensitive topic deserves a calm interface, not an alarming one

No countdown timers, no red flashing, no "your account is at risk"
framing in the product's own voice. The interface's job is to lower
the user's pressure, not add to it - see `docs/ARCHITECTURE.md` for how
this shows up in the UI design choices.
