import os
import sys
import pytest


from app.evaluation.synthetic_generator import synthetic_generator
from app.evaluation.benchmark_runner import benchmark_runner

def test_synthetic_benchmark_dataset_generation():
    dataset = synthetic_generator.generate_benchmark_dataset(10)
    assert len(dataset) == 10
    categories = set(c["category"] for c in dataset)
    assert len(categories) == 10

def test_benchmark_runner_execution():
    metrics = benchmark_runner.run_benchmark_suite(10)
    assert metrics["total_benchmark_cases"] == 10
    assert metrics["overall_investigation_success_rate"] >= 0.90
    assert metrics["benchmark_status"].startswith("PASSED")

if __name__ == "__main__":
    test_synthetic_benchmark_dataset_generation()
    test_benchmark_runner_execution()
    print("ALL PHASE I TESTS PASSED SUCCESSFULLY!")
