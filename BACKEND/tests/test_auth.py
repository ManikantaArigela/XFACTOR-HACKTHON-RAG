import unittest

from api.auth import create_user_account, authenticate_user


class AuthStorageTests(unittest.TestCase):
    def test_register_and_login(self):
        email = "demo@example.com"
        password = "secret123"

        user = create_user_account(email=email, password=password, full_name="Demo User")

        self.assertIsNotNone(user)
        self.assertEqual(user.email, email.lower())
        self.assertTrue(user.password_hash.startswith("scrypt"))

        authenticated = authenticate_user(email=email, password=password)
        self.assertIsNotNone(authenticated)
        self.assertEqual(authenticated.email, email.lower())

        wrong_password = authenticate_user(email=email, password="wrongpass")
        self.assertIsNone(wrong_password)


if __name__ == "__main__":
    unittest.main()
