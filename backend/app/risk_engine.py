"""
Rule-based risk assessment.

TrustCheck deliberately does not use an opaque ML "probability of scam"
score. Every signal here is a named, human-readable behavioural pattern,
because the product's second output (the "reasons") only works if the
first output (the verdict) is explainable in plain language. See
docs/SAFETY_PRINCIPLES.md.

This module has zero external dependencies so it can be unit tested
without installing anything.
"""

import re
from dataclasses import dataclass
from typing import FrozenSet, List, Optional, Pattern, Tuple

from .domain import VERDICT_LABELS, Category, Verdict

# Score thresholds. Kept as module-level constants (not magic numbers)
# so they're easy to tune and to reference from tests.
SUSPICIOUS_THRESHOLD = 2
HIGH_RISK_THRESHOLD = 5

# Reasons shown to the user are capped at 2, matching the product's
# "max two reasons, always behavioural" rule - see TrustCheck App.docx.
MAX_REASONS = 2

FALLBACK_REASON = (
    "No high-risk wording detected, but TrustCheck never confirms "
    "something is genuine - verify independently before acting."
)


@dataclass(frozen=True)
class Signal:
    id: str
    pattern: Pattern
    weight: int
    reason: str
    # None = applies regardless of category; otherwise restrict to these.
    categories: Optional[FrozenSet[Category]] = None


SIGNALS: Tuple[Signal, ...] = (
    Signal(
        id="urgency_pressure",
        pattern=re.compile(
            r"\b(urgent(ly)?|immediately|act now|right away|"
            r"within\s+\d+\s*(hours?|hrs?|minutes?)|final notice|"
            r"expires?\s+(today|soon)|don't\s+delay)\b",
            re.IGNORECASE,
        ),
        weight=2,
        reason="Uses urgency and pressure to make you act quickly",
    ),
    Signal(
        id="upfront_payment",
        pattern=re.compile(
            r"\b(processing fee|registration fee|admin fee|"
            r"pay(ing)?\s+(a\s+)?(deposit|fee)|send\s+money|"
            r"wire\s+transfer|gift\s*cards?|western union|pay\s+upfront)\b",
            re.IGNORECASE,
        ),
        weight=3,
        reason="Asks for an upfront payment or fee",
    ),
    Signal(
        id="sensitive_info_request",
        pattern=re.compile(
            r"\b(bank details|sort code|card number|cvv|security code|"
            r"password|pin\s*number|national insurance number|"
            r"passport\s+(copy|scan|photo|number)|"
            r"one[-\s]?time\s+(code|passcode))\b",
            re.IGNORECASE,
        ),
        weight=3,
        reason="Asks you to share sensitive personal or financial details",
    ),
    Signal(
        id="threat_language",
        pattern=re.compile(
            r"\b(legal action|arrest(ed)?|court proceedings|"
            r"account (will be )?(suspended|closed|locked|frozen)|"
            r"failure to (respond|comply))\b",
            re.IGNORECASE,
        ),
        weight=2,
        reason="Threatens a serious consequence if you don't respond",
    ),
    Signal(
        id="too_good_offer",
        pattern=re.compile(
            r"\b(guaranteed income|no experience (needed|required)|"
            r"earn\s+£?\$?\d+.*(day|week)|risk[-\s]?free|easy money)\b",
            re.IGNORECASE,
        ),
        weight=2,
        reason="Offers an unusually high reward for little or no effort",
        categories=frozenset({Category.JOB, Category.BRAND}),
    ),
    Signal(
        id="generic_greeting",
        pattern=re.compile(
            r"\bdear\s+(customer|user|sir\s*/?\s*madam|valued customer)\b",
            re.IGNORECASE,
        ),
        weight=1,
        reason="Uses a generic greeting instead of your name",
    ),
    Signal(
        id="shortened_or_lookalike_link",
        pattern=re.compile(
            r"\b(bit\.ly|tinyurl\.com|goo\.gl|t\.co|"
            r"[a-z0-9-]+-(secure|verify|account|login|update)\.[a-z]{2,})\b",
            re.IGNORECASE,
        ),
        weight=2,
        reason="Uses a shortened or unofficial-looking link",
    ),
)


def assess_content(
    content: str, category: Optional[Category] = None
) -> Tuple[Verdict, str, List[str]]:
    """Return (verdict, verdict_label, reasons) for a piece of content.

    `reasons` is capped at MAX_REASONS, ordered by the weight of the
    signal that triggered them (highest-impact reason first).
    """
    matched: List[Signal] = []
    for signal in SIGNALS:
        if signal.categories is not None and category not in signal.categories:
            continue
        if signal.pattern.search(content or ""):
            matched.append(signal)

    total_score = sum(s.weight for s in matched)

    if total_score >= HIGH_RISK_THRESHOLD:
        verdict = Verdict.HIGH_RISK
    elif total_score >= SUSPICIOUS_THRESHOLD:
        verdict = Verdict.SUSPICIOUS
    else:
        verdict = Verdict.VERIFY

    top_signals = sorted(matched, key=lambda s: -s.weight)[:MAX_REASONS]
    reasons = [s.reason for s in top_signals] or [FALLBACK_REASON]

    return verdict, VERDICT_LABELS[verdict], reasons
