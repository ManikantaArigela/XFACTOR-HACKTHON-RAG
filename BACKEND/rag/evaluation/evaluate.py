import json
import os
import sys
import time

# Ensure BACKEND root is in python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
rag_parent = os.path.dirname(backend_dir)
if rag_parent not in sys.path:
    sys.path.insert(0, rag_parent)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from rag import rag_service

def run_evaluation():
    eval_file = os.path.join(os.path.dirname(__file__), "questions.json")
    if not os.path.exists(eval_file):
        eval_file = os.path.join(backend_dir, "evaluation", "questions.json")

    with open(eval_file, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print("\n=======================================================")
    print("  RUNNING RAG EVALUATION BENCHMARK SUITE (100% LOCAL)")
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

        # Execute unified RAG answer pipeline
        res = rag_service.answer_query(q_text)
        is_grounded = res.get("grounded", False)
        answer = res.get("answer", "")
        confidence = res.get("confidence", 0.0)

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
