#!/usr/bin/env python3
"""Copy sample log files to a known location for testing (optional)."""
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DIR = REPO_ROOT / "sample_data"
OUTPUT_DIR = REPO_ROOT / "sample_data" / "out"

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for sub in ("nginx", "syslog"):
        src = SAMPLE_DIR / sub / "example.log"
        if src.exists():
            dest = OUTPUT_DIR / f"{sub}_example.log"
            shutil.copy(src, dest)
            print(f"Copied {src} -> {dest}")
    print("Done. Sample logs are in sample_data/out/")

if __name__ == "__main__":
    main()
