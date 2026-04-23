#!/usr/bin/env python3
"""
Backup Aetherion data (knowledge graph, audit logs, workspaces, council archive).
Creates a timestamped tarball in ./backups/.
"""

import os
import tarfile
import time
import sys

BACKUP_DIR = "./backups"
DIRS_TO_BACKUP = [
    "memory",
    "audit",
    "workspaces",
    "council_archive",
    "logs",
    "reports",
]

def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"aetherion_backup_{timestamp}.tar.gz")

    with tarfile.open(backup_file, "w:gz") as tar:
        for dir_name in DIRS_TO_BACKUP:
            if os.path.exists(dir_name):
                tar.add(dir_name, arcname=dir_name)
                print(f"  ✅ Added: {dir_name}")
            else:
                print(f"  ⚠️ Skipped (not found): {dir_name}")

    print(f"\n✅ Backup created: {backup_file}")
    print(f"   Size: {os.path.getsize(backup_file) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    main()
