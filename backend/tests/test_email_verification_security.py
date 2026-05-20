import unittest

from app.core.security import (
    generate_email_verification_code,
    generate_email_verification_token,
    hash_email_verification_code,
    hash_email_verification_token,
)


class EmailVerificationSecurityTest(unittest.TestCase):
    def test_email_verification_tokens_are_random_and_hashable(self):
        first = generate_email_verification_token()
        second = generate_email_verification_token()

        self.assertNotEqual(first, second)
        self.assertGreaterEqual(len(first), 40)
        self.assertEqual(hash_email_verification_token(first), hash_email_verification_token(first))
        self.assertNotEqual(hash_email_verification_token(first), first)
        self.assertNotEqual(hash_email_verification_token(first), hash_email_verification_token(second))

    def test_email_verification_codes_are_six_digits_and_user_scoped(self):
        code = generate_email_verification_code()

        self.assertRegex(code, r"^\d{6}$")
        self.assertEqual(hash_email_verification_code("user-1", code), hash_email_verification_code("user-1", code))
        self.assertNotEqual(hash_email_verification_code("user-1", code), hash_email_verification_code("user-2", code))
        self.assertNotEqual(hash_email_verification_code("user-1", code), code)


if __name__ == "__main__":
    unittest.main()
