import unittest
import uuid
from api.auth import create_user_account, authenticate_user, generate_user_token, verify_user_token


class AuthStorageTests(unittest.TestCase):
    def test_register_and_login(self):
        email = f"user_{uuid.uuid4().hex[:8]}@example.com"
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

    def test_token_generation_and_verification(self):
        user_id = str(uuid.uuid4())
        email = "token_test@example.com"

        token = generate_user_token(user_id, email)
        self.assertIsNotNone(token)
        self.assertTrue(token.startswith("amt."))

        payload = verify_user_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["user_id"], user_id)
        self.assertEqual(payload["email"], email)

        # Tampered token should fail
        tampered_token = token[:-4] + "abcd"
        self.assertIsNone(verify_user_token(tampered_token))

        # Bearer prefix should work
        bearer_payload = verify_user_token(f"Bearer {token}")
        self.assertIsNotNone(bearer_payload)
        self.assertEqual(bearer_payload["user_id"], user_id)


if __name__ == "__main__":
    unittest.main()
