import os
import sys
import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.schemas.hypothesis import CaseHypothesis
from backend.app.services.hypothesis_engine import hypothesis_engine

def test_hypothesis_generation_and_ranking():
    hypotheses = hypothesis_engine.generate_competing_hypotheses(
        case_id="case_001",
        attack_type="upi_fraud",
        indicators=["pay.refund8821@ybl"]
    )
    assert len(hypotheses) == 3
    assert hypotheses[0].title.startswith("H1:")
    
    ranked = hypothesis_engine.rank_hypotheses(hypotheses)
    assert ranked[0].confidence_score >= ranked[1].confidence_score >= ranked[2].confidence_score

if __name__ == "__main__":
    test_hypothesis_generation_and_ranking()
    print("ALL PHASE D TESTS PASSED SUCCESSFULLY!")
