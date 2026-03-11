#!/usr/bin/env python3
"""Regenerate all SOP PDFs from sops/_generators/."""
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
for script in sorted(HERE.glob("sop_*.py")):
    print(f"── {script.name} ──")
    subprocess.run(["python3", str(script)], check=True)
print("\nAll SOP PDFs regenerated.")
