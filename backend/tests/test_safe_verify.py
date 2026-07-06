import unittest

from app.domain import Category
from app.safe_verify import build_safe_verify


class TestSafeVerify(unittest.TestCase):
    def test_named_bank_is_detected(self):
        info = build_safe_verify(
            "This is a message from Barclays about your account.", Category.BANK
        )
        self.assertTrue(any("barclays.co.uk" in e.value for e in info.entries))

    def test_unnamed_bank_falls_back_to_general_guidance(self):
        info = build_safe_verify("Your account needs attention.", Category.BANK)
        self.assertEqual(info.entries, [])
        self.assertIn("card", info.instructions.lower())

    def test_healthcare_returns_official_nhs_links(self):
        info = build_safe_verify("Your test results are ready, call now.", Category.HEALTHCARE)
        values = [e.value for e in info.entries]
        self.assertIn("nhs.uk", values)

    def test_job_flags_that_lookup_is_a_stub(self):
        info = build_safe_verify("We'd like to offer you a role.", Category.JOB)
        self.assertIn("does not yet perform a live", info.disclaimer.lower())

    def test_every_category_disclaimer_avoids_confirming_legitimacy(self):
        for category in Category:
            info = build_safe_verify("sample message", category)
            self.assertIn("confirm", info.disclaimer.lower())
            self.assertTrue(info.heading)
            self.assertTrue(info.instructions)

    def test_default_category_still_returns_actionable_guidance(self):
        info = build_safe_verify("Some random link", Category.OTHER)
        self.assertTrue(info.instructions)

    def test_every_bank_entry_has_a_verification_status(self):
        # Data-integrity rule from the security review: a wrong or stale
        # phone number is the worst failure this product can have, so
        # every entry must carry an explicit verification status.
        from app.safe_verify import UK_BANK_DIRECTORY

        for key, entry in UK_BANK_DIRECTORY.items():
            self.assertIn("last_verified", entry, f"'{key}' is missing last_verified")

    def test_unverified_bank_details_say_so_in_the_disclaimer(self):
        from app.safe_verify import UK_BANK_DIRECTORY

        if any(e.get("last_verified") == "UNVERIFIED" for e in UK_BANK_DIRECTORY.values()):
            info = build_safe_verify("A message from Barclays", Category.BANK)
            self.assertIn("not been re-verified", info.disclaimer)


if __name__ == "__main__":
    unittest.main()
