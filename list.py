#!/usr/bin/env python3
"""Print a one-liner per ADR and SOP.

Usage:
    python3 list.py          # all docs
    python3 list.py adrs     # ADRs only
    python3 list.py sops     # SOPs only
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
ADRS_DIR = ROOT / "adrs"
SOPS_DIR = ROOT / "sops"


def title(path: Path) -> str:
    for line in path.read_text().splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def status(path: Path) -> str:
    for line in path.read_text().splitlines():
        if line.startswith("## "):
            break
        m = re.search(r"\*\*Status\*\*[:\s]*(.+)", line)
        if m:
            raw = m.group(1).strip().rstrip(" |")
            # Strip markdown links for display
            return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw)
    return ""


def print_adrs():
    for md in sorted(ADRS_DIR.glob("ADR-*.md")):
        s = status(md)
        tag = f"  [{s}]" if s else ""
        print(f"  {md.stem}{tag}")


def print_sops():
    for md in sorted(SOPS_DIR.glob("SOP-*.md")):
        print(f"  {title(md)}")


if __name__ == "__main__":
    filt = sys.argv[1] if len(sys.argv) > 1 else "all"

    if filt in ("all", "adrs"):
        print(f"ADRs ({len(list(ADRS_DIR.glob('ADR-*.md')))})")
        print_adrs()

    if filt in ("all", "sops"):
        if filt == "all":
            print()
        print(f"SOPs ({len(list(SOPS_DIR.glob('SOP-*.md')))})")
        print_sops()
