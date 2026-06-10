#!/usr/bin/env python3
"""
GuardDuty Findings Reporter
Fetches active findings and prints a formatted security report.
Run nightly or on-demand to monitor security posture.
"""
import boto3
import json
import sys
from datetime import datetime

REGION = 'us-east-1'
SEVERITY_EMOJI = {
    'LOW': '🟡',
    'MEDIUM': '🟠', 
    'HIGH': '🔴',
    'CRITICAL': '🚨'
}

def get_severity_label(score):
    if score < 4:
        return 'LOW'
    elif score < 7:
        return 'MEDIUM'
    elif score < 9:
        return 'HIGH'
    else:
        return 'CRITICAL'

def run_report():
    print(f"🛡️  GuardDuty Security Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    gd = boto3.client('guardduty', region_name=REGION)

    # Get detector
    detectors = gd.list_detectors()['DetectorIds']
    if not detectors:
        print("❌ No GuardDuty detector found")
        sys.exit(1)

    detector_id = detectors[0]
    print(f"Detector ID: {detector_id}")

    # Get active findings
    finding_ids = gd.list_findings(
        DetectorId=detector_id,
        FindingCriteria={
            'Criterion': {
                'service.archived': {
                    'Eq': ['false']
                }
            }
        }
    )['FindingIds']

    if not finding_ids:
        print("\n✅ No active findings — environment is clean!")
        return 0

    # Get finding details
    findings = gd.get_findings(
        DetectorId=detector_id,
        FindingIds=finding_ids
    )['Findings']

    # Group by severity
    by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
    for f in findings:
        severity = get_severity_label(f['Severity'])
        by_severity[severity].append(f)

    # Print summary
    print(f"\n📊 Summary: {len(findings)} active finding(s)")
    for sev, items in by_severity.items():
        if items:
            emoji = SEVERITY_EMOJI[sev]
            print(f"  {emoji} {sev}: {len(items)}")

    # Print details
    print("\n📋 Finding Details:")
    print("-" * 60)
    for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        for f in by_severity[sev]:
            emoji = SEVERITY_EMOJI[sev]
            print(f"\n{emoji} [{sev}] {f['Title']}")
            print(f"   Type: {f['Type']}")
            print(f"   Updated: {f['UpdatedAt']}")

    # Return non-zero if high/critical findings exist
    if by_severity['CRITICAL'] or by_severity['HIGH']:
        print("\n🚨 ACTION REQUIRED: High/Critical findings detected!")
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(run_report())
