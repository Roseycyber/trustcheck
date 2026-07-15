# TrustCheck

[![CI](https://github.com/Roseycyber/trustcheck/actions/workflows/ci.yml/badge.svg)](https://github.com/Roseycyber/trustcheck/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.12 | 3.13](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue.svg)](backend/requirements.txt)

**Check before you trust.**

TrustCheck gives you a cautious second opinion on a job offer, a bank
text, a healthcare call, an advert, or a link you're not sure about -
and shows you how to verify it safely, without ever telling you
something is "safe." It never confirms legitimacy. It never uses a
contact detail from the message you pasted. It always names the
specific wording behind its verdict, in plain language.

This repository is the reference implementation of the product
described in the accompanying business plan: a rule-based risk
assessment engine, a "Safe Verify" module that routes people to
official sources, and a small web app around both.

## Why this exists

Most scam-checking tools stop at a warning. TrustCheck pairs the
warning with the next step: an official, independently-sourced way to
check for yourself - because a warning without a path forward often
just leaves people stuck, or looking for reassurance in the wrong
place. See `docs/SAFETY_PRINCIPLES.md` for the specific commitments
this project holds itself to, and `docs/ARCHITECTURE.md` for how
they're reflected in the code, not just the copy.

## What's real in this version, and what's a placeholder

This is an honest v1, not a polished demo dressed up as a finished
product:

- The **risk engine** (`backend/app/risk_engine.py`) is real,
  rule-based logic, fully unit tested, with zero external
  dependencies.
- The **Safe Verify bank directory** uses real, publicly published
  bank contact details as a working placeholder. Each entry carries a
  `last_verified` date and is checked against the bank's own official
  page; the static directory is still a stand-in for the live,
  versioned data feed planned in `docs/ARCHITECTURE.md`.
- The **Companies House and NHS lookups** are stubs with a documented
  integration point - see the table in `docs/ARCHITECTURE.md` - not
  live API calls yet.
- There's **no accounts, history, or billing** yet - this version is
  the free-tier check flow only.

Every mocked piece says so in its own disclaimer text in the app
itself, not just in this README.

## Requirements

- **Python 3.12 or 3.13.** These are the supported versions and have
  prebuilt wheels for all dependencies. Avoid pre-release/beta Python
  (e.g. 3.15 betas): some dependencies don't yet publish wheels for
  them, so `pip install` will try to compile from source and fail
  unless you have a C/C++ and Rust toolchain installed.
- **Node.js 18+** for the frontend.

## Quickstart

### Backend

```bash
cd backend
python3 -m venv .venv
```

Then activate the virtual environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (Git Bash)
source .venv/Scripts/activate

# Windows (PowerShell)
# .venv\Scripts\Activate.ps1
```

Install dependencies and run the API:

```bash
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

The API is now at `http://localhost:8000` (interactive docs at
`/docs`, courtesy of FastAPI).

> **Windows note:** if `python3` isn't found, use `python` or the
> launcher `py -3.12` / `py -3.13`. In Git Bash the activate script is
> under `.venv/Scripts/`, not `.venv/bin/`.

Run the tests:

```bash
pytest
```

`test_risk_engine.py` and `test_safe_verify.py` need nothing beyond
the standard library. `test_api.py` needs the full dependency list
above and is skipped automatically if FastAPI isn't installed.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`). The dev
server proxies `/api` requests to `http://localhost:8000`, so run the
backend first.

## API

### `POST /api/check`

```json
{
  "content": "Congratulations! You've been selected for a remote role paying £450/week. Send a £40 registration fee via gift card within 24 hours to secure your start date.",
  "category": "job"
}
```

```json
{
  "verdict": "high_risk",
  "verdict_label": "High risk",
  "reasons": [
    "Asks for an upfront payment or fee",
    "Uses urgency and pressure to make you act quickly"
  ],
  "safe_verify": {
    "heading": "How to verify a job offer safely",
    "instructions": "Legitimate employers do not ask for fees...",
    "entries": [
      { "label": "UK company registry", "value": "find-and-update.company-information.service.gov.uk" }
    ],
    "disclaimer": "This version does not yet perform a live Companies House lookup..."
  }
}
```

`category` is one of `job`, `bank`, `healthcare`, `brand`, `other` and
defaults to `other`. `verdict` is one of `verify`, `suspicious`,
`high_risk` - never anything implying confirmed safety.

## Project layout

```
backend/
  app/
    domain.py       # Category, Verdict, and result types - stdlib only
    risk_engine.py  # Rule-based scoring - stdlib only, fully unit tested
    safe_verify.py  # Official-source routing - stdlib only, fully unit tested
    main.py         # FastAPI HTTP layer
  tests/
frontend/
  src/
    components/     # CheckerForm, VerdictCard, SafeVerifyBox, Stamp, ...
    api/client.js
docs/
  ARCHITECTURE.md
  SAFETY_PRINCIPLES.md
```

## Roadmap

See the "Known limitations" section of `docs/ARCHITECTURE.md` and the
integration table for the concrete next steps (Companies House live
lookup is the best-scoped starting point for a first real
contribution).

## Contributing

See `CONTRIBUTING.md`. Contributions that touch anything in
`docs/SAFETY_PRINCIPLES.md` get extra scrutiny, on purpose.

## About this project

TrustCheck is designed, built, and maintained by its founder as the
reference implementation of a UK consumer trust product. The design
principles behind it - conservative verdicts, official-source routing,
explainability over scores - are documented in
`docs/SAFETY_PRINCIPLES.md` and enforced by the test suite, not just
stated. Issues and contributions are welcome; see `CONTRIBUTING.md`
and `SECURITY.md`.

## License

Apache License 2.0 - see `LICENSE`.
