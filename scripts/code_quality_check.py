#!/usr/bin/env python3
"""
Comprehensive code quality cleanup script for Weather Dashboard.
Runs black, isort, flake8, and mypy to ensure code quality standards.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n🔧 {description}")
    print("-" * 50)

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        success = result.returncode == 0
        print(
            f"✅ {description} completed successfully!"
            if success
            else f"❌ {description} failed!"
        )
        return success

    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def main():
    """Run all code quality checks and fixes."""
    print("🧹 Weather Dashboard - Code Quality Cleanup")
    print("=" * 60)

    commands = [
        # Format with black
        (
            "black src/ tests/ scripts/ --line-length=88 --target-version=py39",
            "Formatting code with Black",
        ),
        # Organize imports with isort
        (
            "isort src/ tests/ scripts/ --profile=black --line-length=88",
            "Organizing imports with isort",
        ),
        # Check style with flake8
        (
            "flake8 src/ tests/ scripts/ --max-line-length=88 --extend-ignore=E203,W503,F401,E501",
            "Checking style with flake8",
        ),
        # Type checking with mypy
        (
            "mypy src/ --ignore-missing-imports --no-strict-optional --show-error-codes",
            "Type checking with mypy",
        ),
    ]

    results = []

    for command, description in commands:
        success = run_command(command, description)
        results.append((description, success))

    # Summary
    print("\n" + "=" * 60)
    print("📊 CODE QUALITY SUMMARY")
    print("=" * 60)

    passed = 0
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{description:30} | {status}")
        if success:
            passed += 1

    total = len(results)
    success_rate = (passed / total) * 100

    print(f"\nOverall: {passed}/{total} checks passed ({success_rate:.1f}%)")

    if passed == total:
        print("\n🎉 All code quality checks passed!")
        print("✅ Code is ready for push to repository")
    else:
        print("\n⚠️ Some quality checks failed")
        print("❌ Please fix issues before pushing")

        # Show specific failure guidance
        print("\n💡 Next steps:")
        for description, success in results:
            if not success:
                if "flake8" in description.lower():
                    print("   - Fix flake8 style issues in the output above")
                elif "mypy" in description.lower():
                    print("   - Add type hints or fix type errors")
                elif "black" in description.lower():
                    print("   - Check black formatting issues")
                elif "isort" in description.lower():
                    print("   - Fix import organization issues")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
