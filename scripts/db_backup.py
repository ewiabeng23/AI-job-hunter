#!/usr/bin/env python3
"""
PostgreSQL Database Backup Script
Dumps the database from the Kubernetes pod and uploads to S3.
Run nightly to ensure data recovery capability.
"""
import subprocess
import boto3
import sys
import os
from datetime import datetime

S3_BUCKET = 'job-hunter-terraform-state-905846954342'
S3_PREFIX = 'database-backups'
NAMESPACE = 'job-hunter'
DB_USER = 'jobhunter_user'
DB_NAME = 'jobhunter'

def run_backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'backup_{timestamp}.sql'
    local_path = f'/tmp/{filename}'

    print(f"💾 Database Backup Started: {timestamp}")
    print(f"Database: {DB_NAME} | Namespace: {NAMESPACE}")

    # Get postgres pod name
    result = subprocess.run(
        ['kubectl', 'get', 'pod', '-n', NAMESPACE,
         '-l', 'app=postgres',
         '-o', 'jsonpath={.items[0].metadata.name}'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"❌ Failed to get postgres pod: {result.stderr}")
        return 1

    pod_name = result.stdout.strip()
    print(f"📦 Postgres pod: {pod_name}")

    # Run pg_dump
    print("Running pg_dump...")
    with open(local_path, 'w') as f:
        dump = subprocess.run(
            ['kubectl', 'exec', '-n', NAMESPACE, pod_name,
             '--', 'pg_dump', '-U', DB_USER, DB_NAME],
            stdout=f, stderr=subprocess.PIPE, text=True
        )

    if dump.returncode != 0:
        print(f"❌ pg_dump failed: {dump.stderr}")
        return 1

    file_size = os.path.getsize(local_path)
    print(f"✅ Dump complete: {file_size} bytes")

    # Upload to S3
    print(f"Uploading to S3: s3://{S3_BUCKET}/{S3_PREFIX}/{filename}")
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.upload_file(local_path, S3_BUCKET, f'{S3_PREFIX}/{filename}')
    print(f"✅ Backup uploaded successfully!")
    print(f"📍 Location: s3://{S3_BUCKET}/{S3_PREFIX}/{filename}")

    # Clean up local file
    os.remove(local_path)
    return 0

if __name__ == "__main__":
    sys.exit(run_backup())
