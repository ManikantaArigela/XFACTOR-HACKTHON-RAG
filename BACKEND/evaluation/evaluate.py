import json
import os
import sys
import time

# Ensure BACKEND root is in python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from generation.query_analyzer import QueryAnalyzer
from retrieval.hybrid_search import HybridSearchService
from guardrails.grounding import GroundingGuardrail
from generation.generator import ResponseGenerator

def run_evaluation():
    eval_file = os.path.join(backend_dir, "evaluation", "questions.json")
    if not os.path.exists(eval_file):
        print(f"[ERROR] Test dataset not found at {eval_file}")
        sys.exit(1)

    with open(eval_file, "r", encoding="utf-8") as f:
        questions = json.load(f)

    analyzer = QueryAnalyzer()
    hybrid_search = HybridSearchService()
    guardrail = GroundingGuardrail()
    generator = ResponseGenerator()

    print("\n=======================================================")
    print("  RUNNING RAG EVALUATION BENCHMARK SUITE")
    print("=======================================================\n")

    total_tests = len(questions)
    passed_tests = 0
    total_latency_ms = 0

    for idx, item in enumerate(questions, 1):
        q_id = item["id"]
        q_text = item["question"]
        expected_grounded = item["expected_grounded"]
        q_type = item["type"]

        start_time = time.time()

        # 1. Analyze
        q_analysis = analyzer.analyze(q_text)

        # 2. Retrieve
        retrieval_res = hybrid_search.hybrid_search(q_analysis)

        # 3. Grounding Guardrail
        is_grounded, fallback_msg, confidence = guardrail.evaluate_grounding(retrieval_res, q_analysis)

        # 4. Generate
        if is_grounded:
            answer = generator.generate_response(q_text, retrieval_res.get("candidates", []))
        else:
            answer = fallback_msg

        latency_ms = (time.time() - start_time) * 1000
        total_latency_ms += latency_ms

        test_passed = (is_grounded == expected_grounded)
        if test_passed:
            passed_tests += 1
            status_symbol = "✅ PASSED"
        else:
            status_symbol = "❌ FAILED"

        print(f"[{idx}/{total_tests}] Test ID: {q_id} ({q_type.upper()}) | Status: {status_symbol} | Latency: {latency_ms:.1f}ms")
        print(f"      Query    : '{q_text}'")
        print(f"      Grounded : Expected={expected_grounded}, Got={is_grounded} (Confidence: {confidence:.4f})")
        print(f"      Answer   : '{answer[:120]}...'")
        print("-" * 65)

    accuracy_pct = (passed_tests / total_tests) * 100
    avg_latency = total_latency_ms / total_tests

    print("\n=======================================================")
    print("  EVALUATION SUMMARY REPORT")
    print(f"  Total Test Queries : {total_tests}")
    print(f"  Passed Benchmark   : {passed_tests} / {total_tests} ({accuracy_pct:.1f}%)")
    print(f"  Average Latency    : {avg_latency:.1f} ms")
    print("=======================================================\n")

if __name__ == "__main__":
    run_evaluation()
