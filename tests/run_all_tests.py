import subprocess
import sys


TESTS = [
    "tests.test_safety",
    "tests.test_remediation",
    "tests.test_rca",
    "tests.test_workflow",
    "tests.test_api",
    "tests.test_observability",
]


def main():

    print("\n========================================")
    print(" SRE MULTI-AGENT TEST SUITE")
    print("========================================\n")

    failed = []

    for test in TESTS:

        print(f"\nRunning: {test}")
        print("-" * 50)

        result = subprocess.run(
            [sys.executable, "-m", test]
        )

        if result.returncode != 0:

            failed.append(test)

            print(
                f"\nFAIL: {test}"
            )

        else:

            print(
                f"\nPASS: {test}"
            )

    print("\n========================================")
    print(" TEST SUITE SUMMARY")
    print("========================================")

    if failed:

        print("\nFailed tests:")

        for test in failed:
            print(f"  - {test}")

        print(
            f"\nResult: FAILED ({len(failed)} test(s))"
        )

        sys.exit(1)

    print("\nAll tests passed.")
    print("Result: SUCCESS")


if __name__ == "__main__":
    main()