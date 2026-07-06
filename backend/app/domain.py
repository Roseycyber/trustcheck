"""
Core domain types for TrustCheck.

Deliberately dependency-free (stdlib only: enum + dataclasses) so the
risk-assessment and safe-verify logic can be imported and unit-tested
without installing FastAPI/Pydantic. The API layer (main.py) wraps these
types for HTTP.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Category(str, Enum):
    """The real-life situation a piece of content is about.

    This mirrors how people actually describe what they've received
    ("a job offer", "a bank text") rather than a technical channel
    (SMS, email, call) - see docs/ARCHITECTURE.md for the reasoning.
    """

    JOB = "job"
    BANK = "bank"
    HEALTHCARE = "healthcare"
    BRAND = "brand"
    OTHER = "other"


class Verdict(str, Enum):
    """The only three outcomes TrustCheck will ever return.

    There is deliberately no "safe" or "genuine" value here. See
    docs/SAFETY_PRINCIPLES.md - this is a product rule, not an
    accident, and it is enforced in code, not just copy.
    """

    VERIFY = "verify"
    SUSPICIOUS = "suspicious"
    HIGH_RISK = "high_risk"


VERDICT_LABELS = {
    Verdict.VERIFY: "Looks legitimate, but verify",
    Verdict.SUSPICIOUS: "Suspicious",
    Verdict.HIGH_RISK: "High risk",
}


@dataclass(frozen=True)
class SafeVerifyEntry:
    """One official, independently-sourced contact detail."""

    label: str
    value: str


@dataclass(frozen=True)
class SafeVerifyInfo:
    """Guidance for verifying a claimed sender through official channels.

    `entries` may be empty when TrustCheck cannot confidently identify
    who the message claims to be from - in that case it still returns
    general guidance rather than nothing.
    """

    heading: str
    instructions: str
    entries: List[SafeVerifyEntry] = field(default_factory=list)
    disclaimer: str = ""


@dataclass(frozen=True)
class CheckResult:
    """The full result of assessing one piece of content."""

    verdict: Verdict
    verdict_label: str
    reasons: List[str]
    safe_verify: SafeVerifyInfo
