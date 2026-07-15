import unittest

from app.domain import Category, Verdict
from app.risk_engine import assess_content


class TestRiskEngine(unittest.TestCase):
    def test_high_risk_job_scam(self):
        content = (
            "URGENT! Guaranteed income, no experience needed. Please pay a "
            "small registration fee via gift cards to secure your position "
            "immediately."
        )
        verdict, label, reasons = assess_content(content, Category.JOB)
        self.assertEqual(verdict, Verdict.HIGH_RISK)
        self.assertEqual(label, "High risk")
        self.assertLessEqual(len(reasons), 2)

    def test_benign_message_returns_verify_not_safe(self):
        content = "Hi Sam, just confirming our meeting on Thursday at 3pm. See you then!"
        verdict, label, reasons = assess_content(content, Category.OTHER)
        self.assertEqual(verdict, Verdict.VERIFY)
        self.assertEqual(label, "Looks legitimate, but verify")
        self.assertTrue(len(reasons) >= 1)

    def test_threats_plus_generic_greeting_is_at_least_suspicious(self):
        content = "Dear Customer, your account will be suspended unless you verify immediately."
        verdict, _, _ = assess_content(content, Category.BANK)
        self.assertIn(verdict, {Verdict.SUSPICIOUS, Verdict.HIGH_RISK})

    def test_no_verdict_label_ever_claims_safety(self):
        # This is a product safety rule, not just copy - enforce it in tests.
        samples = [
            "",
            "Hello there",
            "URGENT pay now with gift cards, send your bank details immediately",
            "Dear Customer, guaranteed income, no experience needed, act now",
        ]
        for content in samples:
            _, label, _ = assess_content(content, Category.OTHER)
            self.assertNotIn("safe", label.lower())
            self.assertNotIn("genuine", label.lower())
            self.assertNotIn("legitimate and verified", label.lower())

    def test_reasons_are_capped_at_two_even_with_many_signals(self):
        content = (
            "URGENT dear customer send your bank details and password, "
            "pay a processing fee immediately or legal action will follow, "
            "guaranteed income no experience needed, click bit.ly/xyz"
        )
        verdict, _, reasons = assess_content(content, Category.JOB)
        self.assertEqual(verdict, Verdict.HIGH_RISK)
        self.assertEqual(len(reasons), 2)

    def test_too_good_offer_signal_is_scoped_to_job_and_brand(self):
        content = "Guaranteed income, no experience needed, easy money."
        _, _, reasons_job = assess_content(content, Category.JOB)
        _, _, reasons_healthcare = assess_content(content, Category.HEALTHCARE)
        self.assertTrue(
            any("reward" in r.lower() for r in reasons_job),
            "expected the too_good_offer reason to fire for JOB category",
        )
        self.assertFalse(
            any("reward" in r.lower() for r in reasons_healthcare),
            "too_good_offer should not fire outside JOB/BRAND categories",
        )

    def test_secrecy_pressure_signal_fires(self):
        content = "Keep this offer strictly confidential and don't tell anyone."
        _, _, reasons = assess_content(content, Category.OTHER)
        self.assertTrue(
            any("secret" in reason.lower() for reason in reasons),
            "expected the secrecy pressure reason to fire",
        )

    def test_secrecy_signal_is_scoped_to_pressure_to_keep_something_secret(self):
        content = "The company treats customer payment records as confidential."
        _, _, reasons = assess_content(content, Category.BRAND)
        self.assertFalse(
            any("secret" in reason.lower() for reason in reasons),
            "secrecy signal should not fire for a neutral confidentiality notice",
        )

    def test_empty_content_does_not_error(self):
        verdict, label, reasons = assess_content("", Category.OTHER)
        self.assertEqual(verdict, Verdict.VERIFY)
        self.assertEqual(len(reasons), 1)

    def test_no_signal_uses_unbounded_dot_star(self):
        # Regression guard for a security-review finding: an unbounded
        # .* caused ~80x CPU amplification on crafted inputs. All
        # quantifiers over arbitrary text must be bounded.
        from app.risk_engine import SIGNALS

        for signal in SIGNALS:
            self.assertNotIn(
                ".*",
                signal.pattern.pattern,
                f"signal '{signal.id}' contains an unbounded .* quantifier",
            )

    def test_pathological_input_completes_fast(self):
        import time

        pathological = ("earn £9 " * 500)[:5000]
        start = time.perf_counter()
        assess_content(pathological, Category.JOB)
        elapsed = time.perf_counter() - start
        self.assertLess(
            elapsed, 0.05, f"assessment took {elapsed*1000:.1f}ms on crafted input"
        )


if __name__ == "__main__":
    unittest.main()
