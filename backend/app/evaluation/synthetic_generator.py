from typing import List, Dict, Any
import uuid

SCAM_CATEGORIES = [
    "UPI Fraud",
    "Phishing",
    "Account Takeover",
    "Investment Scam",
    "Fake Customer Support",
    "Identity Theft",
    "Payment Fraud",
    "Crypto Scam",
    "Social Engineering",
    "Malicious URL"
]

class SyntheticBenchmarkGenerator:
    """
    Synthetic Fraud Case Dataset Generator.
    Generates ground-truth labeled investigation cases across 10 scam categories
    for benchmarking multi-agent investigation precision, recall, and reliability.
    """

    def generate_benchmark_dataset(self, num_cases: int = 10) -> List[Dict[str, Any]]:
        dataset = []
        for i in range(num_cases):
            cat = SCAM_CATEGORIES[i % len(SCAM_CATEGORIES)]
            case_id = f"bench_case_{i+1:03d}"
            
            dataset.append({
                "case_id": case_id,
                "category": cat,
                "description": f"Synthetic benchmark case for {cat}. Attacker used fraudulent indicator indicator_{i}@bank.",
                "ground_truth": {
                    "attack_type": cat.lower().replace(" ", "_"),
                    "expected_entities": [f"upi_indicator_{i}@bank", f"phone_+9198765432{i:02d}"],
                    "expected_status": "INVESTIGATING",
                    "expected_recovery_action": "bank_freeze"
                }
            })
        return dataset

synthetic_generator = SyntheticBenchmarkGenerator()
