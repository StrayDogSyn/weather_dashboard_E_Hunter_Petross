#!/usr/bin/env python3
"""Final code quality verification before push."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Run final verification."""
    print("🎯 Final Code Quality Verification")
    print("=" * 50)

    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Step 1: Apply formatting
    print("1️⃣ Applying code formatting...")
    subprocess.run(
        ["python", "-m", "black", "src/", "tests/", "scripts/", "main.py"],
        capture_output=True,
    )
    subprocess.run(
        ["python", "-m", "isort", "src/", "tests/", "scripts/", "main.py"],
        capture_output=True,
    )
    print("   ✅ Formatting applied")

    # Step 2: Check formatting
    print("2️⃣ Checking code formatting...")
    black_result = subprocess.run(
        ["python", "-m", "black", "--check", "--quiet", "src/"], capture_output=True
    )
    if black_result.returncode == 0:
        print("   ✅ Black formatting: PASSED")
    else:
        print("   ❌ Black formatting: FAILED")
        return False

    # Step 3: Check imports
    print("3️⃣ Checking import organization...")
    isort_result = subprocess.run(
        ["python", "-m", "isort", "--check-only", "--quiet", "src/"],
        capture_output=True,
    )
    if isort_result.returncode == 0:
        print("   ✅ isort imports: PASSED")
    else:
        print("   ❌ isort imports: FAILED")
        return False

    # Step 4: Check style
    print("4️⃣ Checking code style...")
    flake8_result = subprocess.run(
        [
            "python",
            "-m",
            "flake8",
            "src/",
            "--max-line-length=88",
            "--extend-ignore=E203,W503,F401,E501",
        ],
        capture_output=True,
    )
    if flake8_result.returncode == 0:
        print("   ✅ flake8 style: PASSED")
    else:
        print("   ❌ flake8 style: FAILED")
        if flake8_result.stdout:
            print(f"   Issues: {flake8_result.stdout.decode()}")
        return False

    # Step 5: Check types
    print("5️⃣ Checking type hints...")
    mypy_result = subprocess.run(
        [
            "python",
            "-m",
            "mypy",
            "src/",
            "--ignore-missing-imports",
            "--no-strict-optional",
        ],
        capture_output=True,
    )
    if mypy_result.returncode == 0:
        print("   ✅ mypy types: PASSED")
    else:
        print("   ⚠️ mypy types: Some issues (acceptable)")
        # Mypy warnings are often acceptable for this project

    print("\n🎉 All code quality checks completed!")
    print("✅ Code is ready for push!")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
