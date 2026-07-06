# Contributing to TrustCheck

Thanks for considering it. This is an early-stage project, so process
is intentionally light - but a few things matter more here than in a
typical app, because of what TrustCheck is for.

## Before you open a PR

1. **Read `docs/SAFETY_PRINCIPLES.md`.** Changes that weaken any of the
   five commitments there (especially "never confirm legitimacy" and
   "never reuse a sender-supplied contact detail") will be asked to
   change, however small they seem.
2. **Run the tests.**
   ```bash
   cd backend
   pip install -r requirements-dev.txt
   pytest
   ```
   `test_risk_engine.py` and `test_safe_verify.py` require no
   dependencies beyond the standard library and should always pass
   without installing anything.
3. If you add a new risk signal to `risk_engine.py`, add a test for it
   - both that it fires when it should, and that it doesn't fire
   outside its intended category (see
   `test_too_good_offer_signal_is_scoped_to_job_and_brand` for the
   pattern).
4. If you add or change a Safe Verify data source, update the table in
   `docs/ARCHITECTURE.md` and make sure the disclaimer honestly
   reflects whether the source is live or mocked.

## Good first contributions

- A new, well-scoped risk signal (with a false-positive check, not
  just a true-positive one).
- Extending `UK_BANK_DIRECTORY` in `safe_verify.py` with more banks -
  from each bank's own official page, please, not a third-party list.
- Accessibility passes on the frontend (keyboard navigation, screen
  reader labels, colour contrast).
- Wiring up the first real integration from the table in
  `docs/ARCHITECTURE.md` (Companies House is the best-documented
  starting point).

## Code style

- Backend: standard library `dataclasses`/`enum` for anything in
  `domain.py`, `risk_engine.py`, `safe_verify.py` - no new dependencies
  in those three files without a strong reason, since staying
  dependency-free is what keeps them trivially testable.
- Frontend: plain React function components, CSS custom properties for
  anything themeable. No CSS-in-JS, no component libraries added
  without discussion first.

## Reporting a safety concern

If you find a case where TrustCheck's wording could read as confirming
something is safe or genuine, or a Safe Verify response that could
route someone to a non-official channel, please open an issue tagged
`safety` rather than a general bug report - these get priority.
