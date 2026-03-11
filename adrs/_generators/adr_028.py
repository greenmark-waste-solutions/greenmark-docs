#!/usr/bin/env python3
"""ADR-2026-28 — Reject Vault Admin UI in Cerebro"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "adrs" / "ADR-2026-28-reject-vault-admin-ui.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "ADR-2026-28", "Reject Vault Admin UI in Cerebro"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Status:</b> Rejected  |  <b>Date:</b> 2026-03-11  |  "
                   "<b>Owner:</b> Daniel Shanklin / Director of AI &amp; Technology", META))
    story.append(Spacer(1, 6))

    story.append(p("BLUF (Bottom Line Up Front)", H2))
    story.append(p(
        "We will not build a secrets management UI in Cerebro. Any web-tier access to vault secrets "
        "creates a permanent privilege escalation path — SECURITY DEFINER functions would let a "
        "compromised admin session exfiltrate every vendor API key and hijack the data pipeline. "
        "The inconvenience of SQL Editor access is the security control."))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "DECISION: Reject the Vault Admin UI. Do not build it. "
                           "The web tier must never have write access to production secrets.",
                           bg=RED_BG, border=RED_BORDER, text_color=RED))
    story.append(Spacer(1, 6))

    story.append(p("Context", H2))
    story.append(p(
        "Security analysis revealed a fundamental architectural flaw: the feature would require "
        "SECURITY DEFINER functions in Postgres to bridge from the web tier's <i>authenticated</i> role "
        "to <i>svc_etl_runner</i>. This creates a permanent privilege escalation path."))
    story.append(hr())

    story.append(p("The Privilege Escalation Chain", H2))
    story.append(tbl(["Step", "What Happens", "Impact"], [
        [p("1", CELL_CENTER),
         p("<b>SECURITY DEFINER bridge</b> — PostgREST uses authenticated, vault needs svc_etl_runner", CELL),
         p("Permanent escalation path in the database", CELL)],
        [p("2", CELL_CENTER),
         p("<b>Admin session compromise</b> — XSS, session hijack, or account takeover", CELL),
         p("Attacker inherits all admin capabilities", CELL)],
        [p("3", CELL_CENTER),
         p("<b>Credential exfiltration</b> — vault read/write via compromised session", CELL),
         p("All vendor API keys exposed", CELL)],
        [p("4", CELL_CENTER),
         p("<b>Pipeline hijacking</b> — rotate keys, redirect data-daemon", CELL),
         p("Full data pipeline compromised", CELL)],
    ], [0.4 * inch, USABLE * 0.55, USABLE - 0.4 * inch - USABLE * 0.55]))
    story.append(Spacer(1, 6))

    story.append(p("Risk Assessment", H2))
    story.append(severity_tbl(["Risk", "Severity", "Description"], [
        ["Privilege escalation", "CRITICAL",
         p("SECURITY DEFINER creates permanent bridge from web tier to vault tier", CELL)],
        ["Credential exfiltration", "CRITICAL",
         p("Compromised admin session = all vendor API keys exposed", CELL)],
        ["Pipeline hijacking", "HIGH",
         p("Attacker could redirect data-daemon to malicious endpoints", CELL)],
        ["Blast radius", "HIGH",
         p("Single compromise affects all 15 vendor integrations", CELL)],
        ["Audit bypass", "MEDIUM",
         p("Attacker with admin access could falsify audit logs", CELL)],
    ], [1.3 * inch, 0.8 * inch, USABLE - 2.1 * inch]))
    story.append(hr())

    story.append(p("Options Considered", H2))
    story.append(tbl(["Option", "Description", "Verdict"], [
        [p("<b>A. Reject (chosen)</b>", CELL),
         p("No vault UI. SQL Editor + vault-helper.html only.", CELL),
         p("<b>Zero attack surface</b> for credential theft via web app.", CELL)],
        [p("B. Full Vault Admin UI", CELL),
         p("Owner-only page with CRUD, audit logging.", CELL),
         p("Creates permanent privilege escalation path.", RED_TEXT)],
        [p("C. Read-only Vault UI", CELL),
         p("Show names/metadata, no mutations.", CELL),
         p("Still requires SECURITY DEFINER. Leaks inventory.", RED_TEXT)],
        [p("D. Rotation-only UI", CELL),
         p("Only allow key rotation.", CELL),
         p("Still an escalation path. Operationally fragile.", RED_TEXT)],
    ], [1.2 * inch, USABLE * 0.38, USABLE - 1.2 * inch - USABLE * 0.38]))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "PRINCIPLE: The web tier should never have write access to production secrets. "
                           "Even if every other security layer fails, the attacker still cannot touch "
                           "vault secrets because the capability does not exist in the application."))
    story.append(Spacer(1, 6))

    story.append(p("Friction Is the Security Control", H2))
    story.append(p(
        "The inconvenience of SQL Editor access is deliberate. An attacker who compromises a web session "
        "faces a <b>capability gap</b> — the application literally cannot perform vault writes. "
        "Each additional system they must breach multiplies cost and reduces likelihood of success."))
    story.append(Spacer(1, 4))
    story.append(AccentBox(USABLE,
                           "The time it takes to rotate a key through SQL Editor is the security budget. "
                           "That 60 seconds of human friction buys permanent immunity from web-tier credential theft.",
                           bg=AMBER_BG, border=AMBER_BORDER, text_color=AMBER))


if __name__ == "__main__":
    build_doc(OUTPUT, "ADR-2026-28: Reject Vault Admin UI", content)
