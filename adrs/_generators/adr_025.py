#!/usr/bin/env python3
"""ADR-2026-25 — Microsoft Security Stack"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *

OUTPUT = DOCS_ROOT / "adrs" / "ADR-2026-25.pdf"


def content(story, p):
    story.append(BrandHeader(USABLE, "ADR-2026-25", "Adopt Microsoft Security Stack"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Status:</b> Proposed  |  <b>Date:</b> 2026-02-28  |  "
                   "<b>Owner:</b> Daniel Shanklin  |  <b>Approver:</b> Michael D. Nguyen", META))
    story.append(Spacer(1, 6))

    story.append(p("BLUF (Bottom Line Up Front)", H2))
    story.append(p(
        "Adopt Microsoft Entra ID, Azure Key Vault, and Microsoft Authenticator as Greenmark's unified "
        "identity, secrets, and MFA stack. It's already included in the M365 subscription, replaces three "
        "separate vendors (LastPass + Duo + Railway env vars), and gives one-click offboarding plus a full "
        "audit trail. Retire the shared it@greenmarkwaste.com account for interactive logins."))
    story.append(Spacer(1, 6))

    story.append(AccentBox(USABLE,
                           "DECISION: Adopt Entra ID (identity) + Azure Key Vault (secrets) + "
                           "Microsoft Authenticator (MFA). Retire the shared it@ account. "
                           "All within the existing M365 subscription."))
    story.append(Spacer(1, 6))

    story.append(p("Context", H2))
    story.append(p(
        "Greenmark operates 15+ vendor systems with no centralized identity or credential management. "
        "The shared it@greenmarkwaste.com account is used across HubSpot, Railway, Supabase, GitHub, and "
        "LastPass. If that password leaks from any one service, an attacker has the keys to everything. "
        "MFA is inconsistent — Duo on some accounts, nothing on others."))
    story.append(hr())

    story.append(p("Rationale", H2))
    story.append(tbl(["Factor", "Assessment"], [
        [p("<b>Already paying for it</b>", CELL),
         p("M365 Business Premium includes Entra ID P1 and Azure services. No new vendor contracts.", CELL)],
        [p("<b>One ecosystem</b>", CELL),
         p("Identity + auth + secrets + MFA in one Microsoft tenant instead of three vendors.", CELL)],
        [p("<b>Offboarding in one click</b>", CELL),
         p("Disable an Entra ID account → locked out of every SSO-connected system within minutes.", CELL)],
        [p("<b>Audit trail</b>", CELL),
         p("Entra ID logs every login. Key Vault logs every secret access. Compliance-ready.", CELL)],
        [p("<b>Leadership alignment</b>", CELL),
         p("Michael's team asked for Microsoft auth. This is what they already want.", CELL)],
    ], [USABLE * 0.25, USABLE * 0.75]))
    story.append(Spacer(1, 6))

    story.append(p("Options Considered", H2))
    story.append(tbl(["Option", "Description", "Assessment"], [
        [p("<b>A. Microsoft stack (chosen)</b>", CELL),
         p("Entra ID + Key Vault + Authenticator", CELL),
         p("Already licensed, one ecosystem, leadership wants it", CELL)],
        [p("B. Keep current", CELL), p("LastPass + Duo + Railway env vars", CELL),
         p("Shared account risk, three vendors, no audit trail", CELL)],
        [p("C. Build custom (GreenKnox)", CELL), p("Self-hosted secrets store", CELL),
         p("Greenmark is a waste company, not a security company", CELL)],
        [p("D. HashiCorp Vault", CELL), p("Industry-standard secrets manager", CELL),
         p("New vendor, new cost, overkill at this scale", CELL)],
    ], [USABLE * 0.28, USABLE * 0.34, USABLE * 0.38]))
    story.append(Spacer(1, 6))

    story.append(p("Cost", H2))
    story.append(tbl(["Component", "Monthly", "Notes"], [
        ["Entra ID P1", "$6/user/mo", "May already be included in M365 Business Premium"],
        ["Azure Key Vault", "~$1/mo", "Usage-based, negligible"],
        ["Microsoft Authenticator", "Free", ""],
        [p("<b>Total</b>", CELL), p("<b>~$25-50/mo</b>", CELL),
         p("<b>For 4-8 users. Replaces LastPass + Duo.</b>", CELL)],
    ], [USABLE * 0.3, USABLE * 0.2, USABLE * 0.5]))
    story.append(Spacer(1, 6))

    story.append(p("Consequences", H2))
    story.append(p("<b>Positive:</b> Central identity directory. One-click offboarding. Full audit trail. "
                   "API keys encrypted in Key Vault with RBAC. MFA on every account."))
    story.append(Spacer(1, 4))
    story.append(p("<b>Negative:</b> Migration effort — creating individual accounts, configuring SSO, "
                   "moving secrets from Railway env vars to Key Vault. Requires Michael to approve Azure tenant."))


if __name__ == "__main__":
    build_doc(OUTPUT, "ADR-2026-25: Microsoft Security Stack", content)
