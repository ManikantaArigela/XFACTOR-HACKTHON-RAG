import unittest
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from rag.query_analyzer import QueryAnalyzer
from rag.retrieval.hybrid_search import HybridSearchService
from rag.guardrails.grounding import GroundingGuardrail
from rag.generation.generator import ResponseGenerator


class TestChatAccuracy(unittest.TestCase):
    def setUp(self):
        self.analyzer = QueryAnalyzer()
        self.hybrid_search = HybridSearchService()
        self.guardrail = GroundingGuardrail()
        self.generator = ResponseGenerator()

    def test_greeting_intent(self):
        greetings = ["hello", "hi", "good morning", "namaste", "hey"]
        for g in greetings:
            analysis = self.analyzer.analyze(g)
            self.assertEqual(analysis["intent"], "greeting", f"Failed for '{g}'")
            ans = self.generator.generate_greeting()
            self.assertIn("Arudhra Mobile Stores", ans)
            self.assertIn("Pithapuram", ans)

    def test_store_info_intent(self):
        queries = ["where is your store located", "what is the store address", "store timings"]
        for q in queries:
            analysis = self.analyzer.analyze(q)
            self.assertEqual(analysis["intent"], "store_info", f"Failed for '{q}'")
            ans = self.generator.generate_store_info()
            self.assertIn("Pithapuram", ans)
            self.assertIn("Main Road", ans)

    def test_exact_model_apple_18_pro(self):
        # Query specifically for Apple 18 Pro
        analysis = self.analyzer.analyze("apple 18 pro")
        self.assertTrue(analysis["is_specific_model"])
        self.assertIn("18", analysis["model_tokens"])
        self.assertIn("pro", analysis["model_tokens"])

        res = self.hybrid_search.hybrid_search(analysis)
        candidates = res.get("candidates", [])
        self.assertTrue(len(candidates) > 0)
        
        # Verify that EVERY candidate is actually an iPhone 18 Pro / 18 Pro Max!
        for c in candidates:
            name = c["product"]["name"].lower()
            self.assertIn("18", name)
            self.assertIn("pro", name)
            self.assertNotIn("iphone 15", name)
            self.assertNotIn("macbook", name)

    def test_exact_model_oneplus_nord_ce4(self):
        analysis = self.analyzer.analyze("Does OnePlus Nord CE4 have fast charging?")
        self.assertTrue(analysis["is_specific_model"])
        res = self.hybrid_search.hybrid_search(analysis)
        candidates = res.get("candidates", [])
        self.assertTrue(len(candidates) > 0)
        # Verify it matched Nord CE4 and NOT OnePlus Open
        top_name = candidates[0]["product"]["name"]
        self.assertIn("Nord CE4", top_name)
        self.assertNotIn("OnePlus Open", top_name)

    def test_exact_model_realme_12_pro(self):
        analysis = self.analyzer.analyze("What is the price of Realme 12 Pro 5G?")
        self.assertTrue(analysis["is_specific_model"])
        res = self.hybrid_search.hybrid_search(analysis)
        candidates = res.get("candidates", [])
        self.assertTrue(len(candidates) > 0)
        top_name = candidates[0]["product"]["name"]
        self.assertIn("12 Pro", top_name)
        self.assertNotIn("Realme P3", top_name)

    def test_nonexistent_model_polite_apology(self):
        # Query for non-existent models
        for query in ["apple 25 ultra", "samsung s99"]:
            analysis = self.analyzer.analyze(query)
            self.assertTrue(analysis["is_specific_model"])
            res = self.hybrid_search.hybrid_search(analysis)
            
            # Candidates must be empty (no false representation)
            self.assertEqual(len(res.get("candidates", [])), 0)
            self.assertTrue(res.get("is_model_not_found"))
            
            # Guardrail evaluation must produce polite message
            is_grounded, msg, conf = self.guardrail.evaluate_grounding(res, analysis)
            self.assertFalse(is_grounded)
            self.assertIn("Sorry, we currently do not have", msg)
            self.assertIn("Pithapuram", msg)

    def test_general_brand_query(self):
        # Query for brand in general without specific model
        analysis = self.analyzer.analyze("What Samsung phones do you have?")
        self.assertFalse(analysis["is_specific_model"])
        res = self.hybrid_search.hybrid_search(analysis)
        candidates = res.get("candidates", [])
        self.assertTrue(len(candidates) > 0)
        for c in candidates:
            self.assertEqual(c["product"]["brand"], "Samsung")


if __name__ == "__main__":
    unittest.main()
