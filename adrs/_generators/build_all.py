#!/usr/bin/env python3
"""Regenerate all ADR PDFs from decisions/_generators/."""
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
for script in sorted(HERE.glob("adr_*.py")):
    print(f"── {script.name} ──")
    subprocess.run(["python3", str(script)], check=True)
print("\nAll ADR PDFs regenerated.")
