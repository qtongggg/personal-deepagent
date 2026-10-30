import subprocess
import sys
from typing import List, Tuple


def run_tier(tier_name: str, test_files: List[str]) -> Tuple[bool, str]:
    print(f"\n==================================================")
    print(f"  RUNNING {tier_name}")
    print(f"==================================================")
    cmd = [sys.executable, "-m", "pytest", "-v"] + test_files
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0, result.stdout


def main():
    print("==================================================")
    print("  PERSONAL DEEPAGENT 3-TIER REGRESSION SUITE")
    print("==================================================")

    tiers = [
        ("Tier L1: Scaffolding, Configuration & Schemas", ["tests/test_config.py"]),
        (
            "Tier L2: Pluggable Skills & Sanitizer Unit Tests",
            [
                "tests/test_catalog_skill.py",
                "tests/test_retriever_skill.py",
                "tests/test_memory_skill.py",
                "tests/test_sanitizer.py",
            ],
        ),
        (
            "Tier L3: Autonomous Agent Assembly & Golden Traces",
            [
                "tests/test_agent_assembly.py",
                "tests/test_agent_e2e.py",
            ],
        ),
    ]

    all_passed = True
    summary = []

    for name, files in tiers:
        passed, _ = run_tier(name, files)
        status = "PASSED" if passed else "FAILED"
        summary.append((name, status))
        if not passed:
            all_passed = False

    print("\n==================================================")
    print("  TEST EXECUTION SUMMARY")
    print("==================================================")
    for name, status in summary:
        print(f"[{status}] {name}")

    if all_passed:
        print("\nAll tiers PASSED with 100% success!")
        sys.exit(0)
    else:
        print("\nOne or more test tiers FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
