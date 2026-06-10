#!/usr/bin/env python3
"""
Nightly Terraform drift detection script.
Runs terraform plan and alerts if infrastructure has drifted
from the IaC definition.
"""
import subprocess
import sys
import os
from datetime import datetime

# Always resolve terraform dir relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TERRAFORM_DIR = os.path.join(SCRIPT_DIR, '..', 'terraform')

def check_drift():
    print(f"🔍 Drift detection started at {datetime.now().isoformat()}")
    print(f"Terraform directory: {os.path.abspath(TERRAFORM_DIR)}")
    print("Running terraform plan...")

    result = subprocess.run(
        ['terraform', 'plan', '-detailed-exitcode', '-no-color'],
        capture_output=True,
        text=True,
        cwd=TERRAFORM_DIR
    )

    if result.returncode == 0:
        print("✅ No drift detected — infrastructure matches IaC")
        return 0

    elif result.returncode == 2:
        print("⚠️  DRIFT DETECTED — infrastructure has changed outside of Terraform!")
        print("\n--- Drift Details ---")
        print(result.stdout)
        print("Action required: Review changes and either:")
        print("  1. Apply via Terraform to restore IaC state")
        print("  2. Update IaC to reflect intentional changes")
        return 2

    else:
        print(f"❌ Terraform plan failed with exit code {result.returncode}")
        print(result.stderr)
        return 1

if __name__ == "__main__":
    exit_code = check_drift()
    sys.exit(exit_code)
