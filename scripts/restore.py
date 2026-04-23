#!/usr/bin/env python3
"""
Restore Aetherion data from a backup tarball.
Usage: python scripts/restore.py <backup_file>
"""

import os
import tarfile
import sys
import shutil

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/restore.py <backup_file>")
        sys.exit(1)

    backup_file = sys.argv[1]
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        sys.exit(1)

    print(f"Restoring from: {backup_file}")
    with tarfile.open(backup_file, "r:gz") as tar:
        for member in tar.getmembers():
            # Extract to current directory
            tar.extract(member, ".")
            print(f"  ✅ Restored: {member.name}")

    print("\n✅ Restore complete.")

if __name__ == "__main__":
    main()
