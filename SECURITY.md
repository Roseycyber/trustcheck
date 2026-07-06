# Security Policy

## Reporting a vulnerability

If you find a security issue in TrustCheck - especially anything that
could route a user to a non-official contact channel, weaken the
"never confirms legitimacy" guarantee, or abuse the `/api/check`
endpoint - please report it privately rather than opening a public
issue.

Use GitHub's **"Report a vulnerability"** button under the Security
tab of this repository (private vulnerability reporting), or contact
the maintainer directly via the profile listed on the repo.

Please include: what you found, how to reproduce it, and what impact
you believe it has. You'll get an acknowledgement within a few days.

## Scope notes

- The rate limiter in `backend/app/main.py` is in-memory and
  single-process by design; bypassing it across multiple workers or
  instances is a known, documented limitation, not a vulnerability.
- The bank contact directory carries explicit `last_verified` status
  per entry. A stale entry that is honestly marked `UNVERIFIED` is a
  data-maintenance task; a stale entry presented as verified would be
  a serious bug - please report that as a vulnerability.

## Supported versions

This is a pre-1.0 project; only the latest commit on `main` is
supported.
