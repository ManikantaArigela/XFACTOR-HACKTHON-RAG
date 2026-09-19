import unittest
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from rag import rag_service
from config.settings import settings

class TestQueryPrecisionAndContext(unittest.TestCase):
    """Verifies that the RAG assistant answers ONLY what is queried,
    resolves conversational history, and operates with zero external agent API keys."""

    def test_zero_external_agent_keys_dependency(self):
        """Ensure no external agent API keys are configured or required."""
        self.assertFalse(hasattr(settings, "OPENAI_API_KEY"))
        self.assertFalse(hasattr(settings, "GEMINI_API_KEY"))
        self.assertTrue(getattr(settings, "LOCAL_RAG_ENABLED", False))

    def test_price_query_precision(self):
        """Price queries should answer ONLY the price and configuration without dumping unsolicited camera/charging specs."""
        res = rag_service.answer_query("What is the price of Realme 12 Pro 5G?")
        self.assertTrue(res["grounded"])
        answer = res["answer"]

        # Must include price
        self.assertIn("25,999", answer)
        self.assertIn("Realme 12 Pro", answer)

        # Must NOT dump camera, charging, or marketing boilerplate
        self.assertNotIn("Visit Arudhra Mobile Stores in Pithapuram or order online", answer)
        self.assertNotIn("Verified Instagram Offer", answer)

    def test_fast_charging_query_precision(self):
        """Charging queries should answer ONLY the charging and battery specs."""
        res = rag_service.answer_query("Does OnePlus Nord CE4 have fast charging?")
        self.assertTrue(res["grounded"])
        answer = res["answer"]

        # Must answer the charging speed
        self.assertIn("100W", answer)
        self.assertIn("OnePlus Nord CE4", answer)

        # Must NOT dump price or display specs
        self.assertNotIn("₹", answer)
        self.assertNotIn("Visit Arudhra Mobile Stores in Pithapuram", answer)

    def test_budget_5g_query_precision(self):
        """Budget 5G query should not mistake budget for a model name and should list 5G phones under budget."""
        res = rag_service.answer_query("Show me 5G phones under ₹30,000")
        self.assertTrue(res["grounded"])
        answer = res["answer"]

        self.assertIn("5G", answer)
        self.assertIn("under ₹30,000", answer)
        self.assertNotIn("do not have the **under ₹30000** in stock", answer)

    def test_multi_turn_conversational_history(self):
        """Follow-up queries with pronouns ('it', 'its price') should resolve the product from prior turns."""
        history = [
            {"role": "user", "content": "Tell me about iPhone 15"},
            {"role": "assistant", "content": "The Apple iPhone 15 features a 48MP main camera and A16 Bionic chip."}
        ]

        # Follow-up: "What is its price?"
        res = rag_service.answer_query("What is its price?", history=history)
        self.assertTrue(res["grounded"])
        answer = res["answer"]

        # Must resolve iPhone 15 price
        self.assertIn("iPhone 15", answer)
        self.assertIn("65,999", answer)

    def test_multi_turn_charging_followup(self):
        """Follow-up on Nord CE4 about charging."""
        history = [
            {"role": "user", "content": "Do you have OnePlus Nord CE4 5G in stock?"},
            {"role": "assistant", "content": "Yes! The OnePlus Nord CE4 5G is currently in stock at Arudhra Mobile Stores."}
        ]

        # Follow-up: "Does it support fast charging?"
        res = rag_service.answer_query("Does it support fast charging?", history=history)
        self.assertTrue(res["grounded"])
        answer = res["answer"]

        self.assertIn("100W", answer)
        self.assertIn("OnePlus Nord CE4", answer)

    def test_user_prompt_like_mobiles_under_15k(self):
        """Verify 'like mobiles under 15k' returns budget options under 15k."""
        res = rag_service.answer_query("like mobiles under 15k")
        self.assertTrue(res["grounded"])
        self.assertGreaterEqual(res["confidence"], 0.60)
        self.assertGreater(len(res["products"]), 0)
        for p in res["products"]:
            self.assertLessEqual(p["price"], 15000)
        self.assertIn("under", res["answer"].lower())

    def test_user_prompt_mobiles(self):
        """Verify single-word query 'mobiles' is recognized as catalog browse and grounded."""
        res = rag_service.answer_query("mobiles")
        self.assertTrue(res["grounded"])
        self.assertGreaterEqual(res["confidence"], 0.80)
        self.assertGreater(len(res["products"]), 0)
        self.assertIn("Arudhra Mobile Stores", res["answer"])

    def test_user_prompt_where_the_location_is(self):
        """Verify 'where the location is' returns accurate Pithapuram store location."""
        res = rag_service.answer_query("where the location is")
        self.assertTrue(res["grounded"])
        self.assertEqual(res["confidence"], 1.0)
        self.assertIn("Pithapuram", res["answer"])
        self.assertIn("RTC Bus Stand", res["answer"])

if __name__ == "__main__":
    unittest.main()
