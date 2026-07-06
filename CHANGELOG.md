# Changelog

All notable changes to TrustCheck are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/); versioning follows
[SemVer](https://semver.org/) once 1.0 is reached.

## [Unreleased]

### Added
- Rule-based risk assessment engine with named, explainable signals
  (`backend/app/risk_engine.py`), fully unit tested with zero external
  dependencies
- Safe Verify module routing to official UK sources: bank directory,
  Companies House and NHS guidance (`backend/app/safe_verify.py`)
- FastAPI backend (`POST /api/check`, `GET /api/health`)
- React + Vite frontend: checker form, verdict card with verification
  stamp, Safe Verify box, principles section
- Per-IP rate limiting on `/api/check` (in-memory sliding window)
- Environment-driven CORS configuration (`TRUSTCHECK_ALLOWED_ORIGINS`)
- CI workflow (backend tests + frontend build), SECURITY.md,
  CONTRIBUTING.md, architecture and safety-principles docs

### Security
- Bounded a regex quantifier that allowed ~80x CPU amplification on
  crafted inputs; added a regression test forbidding unbounded `.*`
  in any risk signal
- Added mandatory `last_verified` status to every bank directory entry;
  unverified entries disclose that status in the user-facing disclaimer
- Added request timeout and 429 handling to the frontend API client
