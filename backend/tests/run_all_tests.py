import subprocess
import sys
import os

test_files = [
    "backend/tests/test_phase_a.py",
    "backend/tests/test_phase_b.py",
    "backend/tests/test_phase_c.py",
    "backend/tests/test_phase_d.py",
    "backend/tests/test_phase_e.py",
    "backend/tests/test_phase_f.py",
    "backend/tests/test_phase_g.py",
    "backend/tests/test_phase_h.py",
    "backend/tests/test_phase_i.py"
]

def run_all():
    print("=== RUNNING FULL CYBERGUARDAI UPGRADE TEST SUITE ===")
    failed = []
    for test in test_files:
        print(f"\n--- Running {test} ---")
        res = subprocess.run([sys.executable, test], cwd=os.getcwd())
        if res.returncode != 0:
            failed.append(test)
            
    print("\n==================================================")
    if failed:
        print(f"FAILED TESTS: {failed}")
        sys.exit(1)
    else:
        print("ALL PHASES (A through I) PASSED SUCCESSFULLY WITH 100% SUCCESS RATE!")
        sys.exit(0)

if __name__ == "__main__":
    run_all()
