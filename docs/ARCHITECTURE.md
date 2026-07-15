# Architecture

## Overview

```
frontend/ (React + Vite)  --->  backend/ (FastAPI)
     |                                |
     |                                +-- risk_engine.py   (pure Python, rule-based)
     |                                +-- safe_verify.py   (pure Python, source directory)
     +-- calls POST /api/check        +-- main.py          (thin HTTP wrapper)
```

The split between `domain.py` / `risk_engine.py` / `safe_verify.py` and
`main.py` is deliberate: the first three files have **zero external
dependencies** (stdlib `enum` and `dataclasses` only), so the actual
decision-making logic can be unit tested without installing anything.
`main.py` is a thin FastAPI wrapper that does request validation and
JSON shaping - the boring, low-risk part.

## Why situation-based categories, not channel-based ones

The category selector is `job / bank / healthcare / brand / other`,
not `SMS / email / call / social media`. This mirrors how people
actually describe what happened to them ("I got a job offer that felt
off") rather than the technical channel it arrived on. It also lets
the Safe Verify step pick the right official source without asking the
user anything technical.

## Why a rule-based engine instead of an ML model

Every signal in `risk_engine.py` is a named pattern with a
plain-English reason attached to it (`urgency_pressure`,
`upfront_payment`, and so on). This is intentional: TrustCheck's
"reasons" output only works if the verdict is explainable in one
sentence. An opaque classifier could produce a similar risk band but
couldn't honestly produce the second half of the product (a specific,
human reason) without either hallucinating an explanation or exposing
model internals nobody asked for. Nothing here rules out layering a
model in later as an additional signal - but it would need to produce
an explanation, not just a score, to fit the product's rules in
`docs/SAFETY_PRINCIPLES.md`.

## Safe Verify data sources - current state and integration points

This is the most important thing to understand before using this
project for anything beyond a demo.

| Category | Current state | Real integration point |
|---|---|---|
| Bank | Static dict of major UK banks' public contact info, in `safe_verify.py::UK_BANK_DIRECTORY` | Move to a maintained, versioned data source; ideally cross-checked periodically against banks' own published pages |
| Job / employer | **Live** - calls the [Companies House public API](https://developer.company-information.service.gov.uk/) from `companies_house.py`, wired into `safe_verify.py::_job_guidance`. Falls back to general guidance when the API key is not set or the API is unreachable. | N/A - live integration complete |
| Healthcare | Static NHS URLs (`nhs.uk`, `nhs.uk/find-a-gp`, `111.nhs.uk`) | These are stable enough to leave static; consider the [NHS API developer hub](https://digital.nhs.uk/developer) if a live directory lookup is ever needed |
| Brand / advert | Generic guidance only, no directory | Would need a source of truth for "official domains per brand," which doesn't have an obvious authoritative UK public API - likely a manually curated, versioned list to start |

The rule this project holds itself to: **a mocked source says it's
mocked.** See the `disclaimer` field on every `SafeVerifyInfo` -
several of them explicitly state that a lookup isn't live yet. Do not
remove those disclaimers without actually wiring up the real source.

## Frontend design decisions

The interface uses a "verification stamp" as its one deliberate visual
signature - a circular ink-stamp seal on every result - because the
product's actual job is exactly that: checking something against an
official mark of provenance. The palette (muted paper background, ink
navy text, three verdict colours) and typography (a document-like
serif for headings, a plain sans for body text, a monospace for
verdict codes and data) were chosen to read as calm and civic rather
than as a security-vendor or growth-hacked consumer app - see
`docs/SAFETY_PRINCIPLES.md#5` for why that matters for this product
specifically.

## Known limitations of this version

- No persistence layer - nothing submitted is stored (by design, for
  now; see the business plan's data-minimisation commitments, though a
  real product would need to decide this deliberately rather than by
  default).
- No authentication, accounts, or the "history" feature described in
  the paid tier of the business plan - out of scope for this v1.
- No rate limiting on `/api/check`.
- CORS is wide open (`allow_origins=["*"]`) for local development -
  tighten this before any real deployment.
