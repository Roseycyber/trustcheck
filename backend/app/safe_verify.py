"""
Safe Verify: routes the user to an official, independently-sourced way
to check who a message claims to be from.

IMPORTANT - current state of this module (read before using in
production): the bank directory below is static, public contact info
included as a working placeholder so the full product flow can be
demonstrated end-to-end. The Companies House lookup is now LIVE
(see backend/app/companies_house.py); the NHS lookup is still a stub
with a clear integration point, not a live call. See
docs/ARCHITECTURE.md#safe-verify-data-sources for the plan to replace
remaining stubs with live, versioned data feeds. This module never
fabricates a "verified" result - where TrustCheck can't confidently
identify a sender, it says so and falls back to general guidance.

This module has zero external dependencies so it can be unit tested
without installing anything.
"""

from typing import Any, Dict, Optional

from .companies_house import search_company
from .domain import Category, SafeVerifyEntry, SafeVerifyInfo

# Placeholder directory of major UK banks' *own published* contact
# details (the kind of thing printed on the back of a card or on the
# bank's official site). Real deployment should source this from a
# maintained, versioned dataset rather than a hardcoded dict - flagged
# in docs/ARCHITECTURE.md.
# Every entry MUST carry a last_verified date (enforced by a test).
# If an entry's date is older than the staleness window, re-check it
# against the bank's own published page before shipping - a wrong or
# stale phone number in a product whose entire job is routing people to
# the *right* number is the worst data-integrity failure this app can have.
#
# 2026-07-15 audit: every website + phone below was checked against the
# bank's OWN published page (not a third-party list) on this date.
#   - Santander: previous number 0800 9127 500 did not match any number
#     Santander publishes; corrected to 0330 9 123 123 (santander.co.uk
#     telephone-banking + legal pages).
#   - Monzo: upgraded from "in-app chat" to the freephone Monzo itself
#     publishes (monzo.com/help/app-help/contacting-support); Monzo still
#     directs customers to in-app chat first.
#   - Revolut: left as in-app chat only. Revolut publishes no UK support
#     phone line and states it will never call you about your account, so
#     listing a "number" here would be misleading and unsafe.
UK_BANK_DIRECTORY: Dict[str, Dict[str, str]] = {
    "barclays": {"name": "Barclays", "website": "barclays.co.uk", "phone": "0345 734 5345", "last_verified": "2026-07-15"},
    "hsbc": {"name": "HSBC", "website": "hsbc.co.uk", "phone": "03457 404 404", "last_verified": "2026-07-15"},
    "lloyds": {"name": "Lloyds Bank", "website": "lloydsbank.com", "phone": "0345 300 0000", "last_verified": "2026-07-15"},
    "natwest": {"name": "NatWest", "website": "natwest.com", "phone": "03457 888 444", "last_verified": "2026-07-15"},
    "santander": {"name": "Santander UK", "website": "santander.co.uk", "phone": "0330 9 123 123", "last_verified": "2026-07-15"},
    "monzo": {"name": "Monzo", "website": "monzo.com", "phone": "0800 088 4040 (in-app chat preferred)", "last_verified": "2026-07-15"},
    "revolut": {"name": "Revolut", "website": "revolut.com", "phone": "In-app chat only (see revolut.com)", "last_verified": "2026-07-15"},
    "nationwide": {"name": "Nationwide", "website": "nationwide.co.uk", "phone": "03457 30 20 11", "last_verified": "2026-07-15"},
    "halifax": {"name": "Halifax", "website": "halifax.co.uk", "phone": "0345 603 4020", "last_verified": "2026-07-16"},
}

_NEVER_CONFIRMS = "TrustCheck never confirms a message is genuine, whichever channel you check."


def _find_named_bank(content: str) -> Optional[Dict[str, str]]:
    lowered = (content or "").lower()
    for key, info in UK_BANK_DIRECTORY.items():
        if key in lowered:
            return info
    return None


def _bank_guidance(content: str) -> SafeVerifyInfo:
    bank = _find_named_bank(content)
    if bank:
        return SafeVerifyInfo(
            heading=f"How to verify a {bank['name']} message safely",
            instructions=(
                "Do not use any link, phone number, or QR code from the message. "
                "Contact the bank directly using details found independently, "
                "such as the ones below or the number on your card."
            ),
            entries=[
                SafeVerifyEntry(label="Official website", value=bank["website"]),
                SafeVerifyEntry(label="Official phone", value=bank["phone"]),
            ],
            disclaimer=(
                "These details come from the bank's own public sources"
                + (
                    ", but have not been re-verified recently - cross-check "
                    "them on the bank's official website before calling"
                    if bank.get("last_verified") == "UNVERIFIED"
                    else f" (last verified {bank.get('last_verified')})"
                )
                + ". Providing them does not confirm the message is genuine. "
                + _NEVER_CONFIRMS
            ),
        )
    return SafeVerifyInfo(
        heading="How to verify a bank or payment message safely",
        instructions=(
            "TrustCheck could not identify a specific bank from the wording. "
            "Use the number on the back of your card or your bank's official app - "
            "never a number or link from the message itself."
        ),
        entries=[],
        disclaimer=f"No bank could be confidently identified. {_NEVER_CONFIRMS}",
    )


def _lookup_company(content: str) -> Optional[Dict[str, Any]]:
    """Heuristically detect a company name in content and look it up."""
    for line in content.splitlines():
        stripped = line.strip()
        if stripped and stripped[0].isupper() and len(stripped) > 3:
            try:
                return search_company(stripped)
            except Exception:
                return None
    return None


def _job_guidance(content: str = "") -> SafeVerifyInfo:
    company = _lookup_company(content) if content else None
    if company:
        return SafeVerifyInfo(
            heading=f"How to verify a {company['company_name']} job offer safely",
            instructions=(
                "Legitimate employers do not ask for fees, bank details, or ID "
                "documents before you've formally accepted a role. Look the "
                "company up independently and check its careers page directly "
                "rather than any link in the message."
            ),
            entries=[
                SafeVerifyEntry(label="Registered company name", value=company["company_name"]),
                SafeVerifyEntry(label="Company number", value=company["company_number"]),
                SafeVerifyEntry(label="Registered address", value=company["address"]),
                SafeVerifyEntry(
                    label="UK company registry",
                    value="find-and-update.company-information.service.gov.uk",
                ),
            ],
            disclaimer=(
                f"This information comes from Companies House (company number "
                f"{company['company_number']}). Providing it does not confirm "
                "the message or job offer is genuine - always verify through "
                f"the company's own official website. {_NEVER_CONFIRMS}"
            ),
        )
    return SafeVerifyInfo(
        heading="How to verify a job offer safely",
        instructions=(
            "Legitimate employers do not ask for fees, bank details, or ID "
            "documents before you've formally accepted a role. Look the "
            "company up independently and check its careers page directly "
            "rather than any link in the message."
        ),
        entries=[
            SafeVerifyEntry(
                label="UK company registry",
                value="find-and-update.company-information.service.gov.uk",
            ),
        ],
        disclaimer=(
            "TrustCheck could not find this company in the Companies House "
            "register, or the live lookup was unavailable. Always verify "
            f"independently. {_NEVER_CONFIRMS}"
        ),
    )


def _healthcare_guidance() -> SafeVerifyInfo:
    return SafeVerifyInfo(
        heading="How to verify a healthcare message safely",
        instructions=(
            "The NHS and registered clinics do not pressure you into paying "
            "or acting immediately by phone or text. Verify independently "
            "using the official directory below."
        ),
        entries=[
            SafeVerifyEntry(label="NHS website", value="nhs.uk"),
            SafeVerifyEntry(label="Find a GP", value="nhs.uk/find-a-gp"),
            SafeVerifyEntry(label="Non-emergency advice", value="111.nhs.uk"),
        ],
        disclaimer=(
            "These are public NHS sources. They do not confirm the original "
            f"message was actually sent by the NHS or a real clinic. {_NEVER_CONFIRMS}"
        ),
    )


def _brand_guidance() -> SafeVerifyInfo:
    return SafeVerifyInfo(
        heading="How to verify an advert or brand message safely",
        instructions=(
            "Do not click the link in the message. Search for the brand "
            "directly in your browser or app store and check the offer on "
            "the brand's own official site."
        ),
        entries=[],
        disclaimer=f"TrustCheck does not confirm whether a brand or advert is genuine. {_NEVER_CONFIRMS}",
    )


def _default_guidance() -> SafeVerifyInfo:
    return SafeVerifyInfo(
        heading="How to verify safely",
        instructions=(
            "Avoid clicking links or calling numbers included in the message. "
            "Search independently for the organisation involved and use only "
            "the contact details it publishes itself."
        ),
        entries=[],
        disclaimer=f"TrustCheck provides guidance, not confirmation. {_NEVER_CONFIRMS}",
    )


def build_safe_verify(content: str, category: Optional[Category]) -> SafeVerifyInfo:
    """Return verification guidance for the given category.

    Always returns something actionable - even the default/fallback
    path gives general guidance rather than nothing - but never
    represents a lookup as confirming legitimacy.
    """
    if category == Category.BANK:
        return _bank_guidance(content)
    if category == Category.JOB:
        return _job_guidance(content)
    if category == Category.HEALTHCARE:
        return _healthcare_guidance()
    if category == Category.BRAND:
        return _brand_guidance()
    return _default_guidance()
