"""
Measures the scam detector on a labelled dataset and writes an honest report.

    python -m app.evaluation.evaluate_detector                    # full dataset
    python -m app.evaluation.evaluate_detector --limit 10         # quick smoke run
    python -m app.evaluation.evaluate_detector --data my.jsonl    # your own samples

Dataset format (JSONL): {"label": "scam" | "legit", "category": "...", "text": "..."}
The bundled set is small and hand-written; add real (anonymised) messages to make the numbers meaningful.

Two operating points are reported:
- strict:   only a SCAM verdict counts as "flagged"
- cautious: SCAM or SUSPICIOUS counts as "flagged" (what the UI effectively warns about)
"""
import argparse
import json
import os
import time
from collections import defaultdict
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app.agents.scam_detection_agent import detect_scam  # noqa: E402
from app.schemas.common import UserProfile  # noqa: E402
from app.services.llm_provider import GEMINI_MODEL, GROQ_MODEL  # noqa: E402

HERE = os.path.dirname(__file__)
DEFAULT_DATA = os.path.join(HERE, "data", "scam_eval.jsonl")
REPORT_DIR = os.path.join(HERE, "reports")


def metrics(rows: list[dict], flagged_verdicts: set[str]) -> dict:
    tp = sum(r["label"] == "scam" and r["verdict"] in flagged_verdicts for r in rows)
    fn = sum(r["label"] == "scam" and r["verdict"] not in flagged_verdicts for r in rows)
    fp = sum(r["label"] == "legit" and r["verdict"] in flagged_verdicts for r in rows)
    tn = sum(r["label"] == "legit" and r["verdict"] not in flagged_verdicts for r in rows)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "tp": tp, "fn": fn, "fp": fp, "tn": tn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(2 * precision * recall / (precision + recall), 3) if precision + recall else 0.0,
        "false_negative_rate": round(fn / (tp + fn), 3) if tp + fn else 0.0,
        "false_positive_rate": round(fp / (fp + tn), 3) if fp + tn else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--delay", type=float, default=2.0, help="seconds between samples (free-tier rate limits)")
    args = parser.parse_args()

    with open(args.data, encoding="utf-8") as f:
        samples = [json.loads(line) for line in f if line.strip()]
    if args.limit:
        # Keep both classes in a short run
        samples = samples[: args.limit // 2] + [s for s in samples if s["label"] == "legit"][: args.limit - args.limit // 2]

    profile = UserProfile(user_type="adult")
    rows = []
    for i, s in enumerate(samples, 1):
        started = time.perf_counter()
        report = detect_scam(s["text"], profile)
        rows.append({
            **s,
            "verdict": report.verdict,
            "risk_score": report.risk_score,
            "analysis_status": report.analysis_status,
            "latency_s": round(time.perf_counter() - started, 2),
        })
        print(f"[{i}/{len(samples)}] {s['label']:5} -> {report.verdict:10} risk={report.risk_score:3} {s['category']}")
        time.sleep(args.delay)

    failed = [r for r in rows if r["analysis_status"] == "failed"]
    by_category = defaultdict(lambda: {"total": 0, "correct_cautious": 0})
    for r in rows:
        c = by_category[f"{r['label']}/{r['category']}"]
        c["total"] += 1
        c["correct_cautious"] += (r["verdict"] != "SAFE") == (r["label"] == "scam")

    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "dataset": os.path.basename(args.data),
        "samples": len(rows),
        "models": {"groq": GROQ_MODEL, "gemini": GEMINI_MODEL},
        "strict": metrics(rows, {"SCAM"}),
        "cautious": metrics(rows, {"SCAM", "SUSPICIOUS"}),
        "analysis_failures": len(failed),
        "median_latency_s": sorted(r["latency_s"] for r in rows)[len(rows) // 2] if rows else None,
        "missed_scams": [r for r in rows if r["label"] == "scam" and r["verdict"] == "SAFE"],
        "false_alarms": [r for r in rows if r["label"] == "legit" and r["verdict"] == "SCAM"],
        "by_category": by_category,
    }
    os.makedirs(REPORT_DIR, exist_ok=True)
    path = os.path.join(REPORT_DIR, f"detector_eval_{datetime.utcnow():%Y%m%d_%H%M}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\nstrict  :", report["strict"])
    print("cautious:", report["cautious"])
    print(f"analysis failures: {len(failed)}, median latency: {report['median_latency_s']}s")
    print("report written to", path)


if __name__ == "__main__":
    main()
