#!/usr/bin/env python3
"""Database Entity Map — Per-service diagrams showing bronze → silver → gold flow"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.greenmark_pdf import *
from reportlab.lib.pagesizes import letter, landscape

OUTPUT = DOCS_ROOT / "diagrams" / "database-entity-map.pdf"

# Landscape dimensions
L_W, L_H = landscape(letter)
L_MARGIN = 0.5 * inch
L_USABLE = L_W - 2 * L_MARGIN


def content(story, p):
    story.append(BrandHeader(L_USABLE, "DIAGRAM", "Database Entity Map"))
    story.append(Spacer(1, 10))
    story.append(p("<b>Last Updated:</b> 2026-03-11  |  "
                   "<b>Owner:</b> Daniel Shanklin / Director of AI &amp; Technology  |  "
                   "<b>Database:</b> Supabase (zbscgmkkictwxoridyui)", META))
    story.append(Spacer(1, 8))
    story.append(p(
        "One diagram per service showing every table from raw ingestion (bronze) through "
        "cleaned views (silver) to business metrics (gold). Arrows show data lineage. "
        "Services without silver/gold layers are bronze-only today — silver and gold "
        "will be built as connectors come online."))
    story.append(Spacer(1, 12))

    # =========================================================
    # HUBSPOT — Full bronze → silver → gold
    # =========================================================
    story.append(p("HubSpot — Full Medallion Pipeline", H2))
    story.append(p(
        "23 bronze tables → 22 silver materialized views → 25 gold analytics tables. "
        "The only service with a complete medallion pipeline today."))
    story.append(Spacer(1, 4))

    # HubSpot Diagram 1: People, Deals & Engagements
    story.append(p("HubSpot — People, Deals &amp; Engagements", H3))
    story.append(mermaid("""
        flowchart LR
            subgraph "hubspot_bronze"
                b_companies[companies]
                b_contacts[contacts]
                b_deals[deals]
                b_owners[owners]
                b_calls[calls]
                b_emails[emails]
                b_meetings[meetings]
                b_notes[notes]
                b_tasks[tasks]
                b_assoc_dc[assoc_deal_contact]
                b_assoc_dco[assoc_deal_company]
                b_assoc_cc[assoc_contact_company]
            end
            subgraph "hubspot_silver"
                s_companies[companies]
                s_contacts[contacts]
                s_deals[deals]
                s_owners[owners]
                s_calls[calls]
                s_emails[emails]
                s_meetings[meetings]
                s_notes[notes]
                s_tasks[tasks]
                s_engagements[engagements<br/>UNION ALL]
                s_deal_contacts[deal_contacts]
                s_deal_companies[deal_companies]
            end
            subgraph "gold — Sales Intelligence"
                g_pipeline[pipeline_summary]
                g_velocity[deal_velocity]
                g_aging[deal_aging]
                g_stage[deal_stage_flow]
                g_winloss[win_loss_analysis]
                g_forecast[forecast]
            end
            subgraph "gold — Rep Performance"
                g_owner[owner_performance]
                g_rep[rep_activity]
                g_coverage[rep_pipeline_coverage]
                g_funnel[contact_funnel]
            end
            subgraph "gold — Customer"
                g_health[customer_health]
                g_territory[territory_summary]
                g_company[companies]
            end
            b_companies --> s_companies
            b_contacts --> s_contacts
            b_deals --> s_deals
            b_owners --> s_owners
            b_calls --> s_calls
            b_emails --> s_emails
            b_meetings --> s_meetings
            b_notes --> s_notes
            b_tasks --> s_tasks
            b_assoc_dc --> s_deal_contacts
            b_assoc_dco --> s_deal_companies
            b_assoc_cc --> s_deal_companies
            s_calls --> s_engagements
            s_emails --> s_engagements
            s_meetings --> s_engagements
            s_notes --> s_engagements
            s_tasks --> s_engagements
            s_deals --> g_pipeline
            s_deals --> g_velocity
            s_deals --> g_aging
            s_deals --> g_stage
            s_deals --> g_winloss
            s_deals --> g_forecast
            s_deals --> g_health
            s_deals --> g_coverage
            s_deals --> g_owner
            s_engagements --> g_rep
            s_engagements --> g_health
            s_companies --> g_territory
            s_companies --> g_company
            s_companies --> g_health
            s_contacts --> g_funnel
            s_owners --> g_owner
            style s_engagements fill:#FFF8E6,stroke:#D4A017
            style g_pipeline fill:#E8F0EC,stroke:#2D6B4A
            style g_velocity fill:#E8F0EC,stroke:#2D6B4A
            style g_aging fill:#E8F0EC,stroke:#2D6B4A
            style g_stage fill:#E8F0EC,stroke:#2D6B4A
            style g_winloss fill:#E8F0EC,stroke:#2D6B4A
            style g_forecast fill:#E8F0EC,stroke:#2D6B4A
            style g_health fill:#E8F0EC,stroke:#2D6B4A
            style g_territory fill:#E8F0EC,stroke:#2D6B4A
            style g_company fill:#E8F0EC,stroke:#2D6B4A
            style g_owner fill:#E8F0EC,stroke:#2D6B4A
            style g_rep fill:#E8F0EC,stroke:#2D6B4A
            style g_coverage fill:#E8F0EC,stroke:#2D6B4A
            style g_funnel fill:#E8F0EC,stroke:#2D6B4A
    """))
    story.append(Spacer(1, 8))

    # HubSpot Diagram 2: Support, Products & Contracts
    story.append(p("HubSpot — Support, Products &amp; Contracts", H3))
    story.append(mermaid("""
        flowchart LR
            subgraph "hubspot_bronze"
                b_tickets[tickets]
                b_feedback[feedback_submissions]
                b_products[products]
                b_line_items[line_items]
                b_quotes[quotes]
                b_goals[goals]
                b_comms[communications]
                b_postal[postal_mail]
                b_assoc_tc[assoc_ticket_company]
                b_assoc_qd[assoc_quote_deal]
                b_assoc_lid[assoc_line_item_deal]
            end
            subgraph "hubspot_silver"
                s_tickets[tickets]
                s_feedback[feedback]
                s_products[products]
                s_line_items[line_items]
                s_quotes[quotes]
                s_goals[goals]
                s_ticket_co[ticket_companies]
                s_quote_deals[quote_deals]
                s_li_deals[line_item_deals]
            end
            subgraph "gold — Support"
                g_tsummary[ticket_summary]
                g_taging[ticket_aging]
                g_tcompany[ticket_by_company]
                g_csat[customer_satisfaction]
            end
            subgraph "gold — Product & Contract"
                g_product[product_mix]
                g_contract[contract_details]
                g_quote[quote_pipeline]
                g_quota[quota_attainment]
            end
            b_tickets --> s_tickets
            b_feedback --> s_feedback
            b_products --> s_products
            b_line_items --> s_line_items
            b_quotes --> s_quotes
            b_goals --> s_goals
            b_assoc_tc --> s_ticket_co
            b_assoc_qd --> s_quote_deals
            b_assoc_lid --> s_li_deals
            b_comms -.-> s_tickets
            b_postal -.-> s_tickets
            s_tickets --> g_tsummary
            s_tickets --> g_taging
            s_tickets --> g_tcompany
            s_ticket_co --> g_tcompany
            s_feedback --> g_csat
            s_products --> g_product
            s_line_items --> g_product
            s_line_items --> g_contract
            s_li_deals --> g_contract
            s_quotes --> g_quote
            s_quote_deals --> g_quote
            s_goals --> g_quota
            style g_tsummary fill:#E8F0EC,stroke:#2D6B4A
            style g_taging fill:#E8F0EC,stroke:#2D6B4A
            style g_tcompany fill:#E8F0EC,stroke:#2D6B4A
            style g_csat fill:#E8F0EC,stroke:#2D6B4A
            style g_product fill:#E8F0EC,stroke:#2D6B4A
            style g_contract fill:#E8F0EC,stroke:#2D6B4A
            style g_quote fill:#E8F0EC,stroke:#2D6B4A
            style g_quota fill:#E8F0EC,stroke:#2D6B4A
    """))
    story.append(PageBreak())

    # =========================================================
    # SAGE INTACCT — Bronze only
    # =========================================================
    story.append(p("Sage Intacct — Financial Data (Bronze Only)", H2))
    story.append(p(
        "5 bronze tables for GL, AP, AR, and vendor data. Multi-entity (ntx, hometown). "
        "Silver and gold layers planned once sage-intacct connector is implemented."))
    story.append(Spacer(1, 4))
    story.append(mermaid("""
        flowchart LR
            subgraph "sage_bronze"
                gl_accounts[gl_accounts<br/>account_no, title<br/>account_type, normal_balance<br/>category, department]
                gl_journal[gl_journal_entries<br/>entry_date, account_no<br/>debit, credit, memo<br/>period, department]
                ap_bills[ap_bills<br/>vendor_id, bill_date<br/>due_date, total_amount<br/>status, department]
                ar_invoices[ar_invoices<br/>customer_id, invoice_date<br/>due_date, total_amount<br/>status, department]
                vendors[vendors<br/>vendor_name, vendor_type<br/>payment_terms, status]
            end
            subgraph "sage_silver (planned)"
                s_sage["Silver views TBD<br/>GL summaries, AP aging<br/>AR aging, vendor analytics"]
            end
            subgraph "gold (planned)"
                g_sage["Gold tables TBD<br/>Financial dashboards<br/>Cash flow, P&L metrics"]
            end
            gl_accounts -.-> s_sage
            gl_journal -.-> s_sage
            ap_bills -.-> s_sage
            ar_invoices -.-> s_sage
            vendors -.-> s_sage
            s_sage -.-> g_sage
            style s_sage fill:#F5F5F5,stroke:#999,stroke-dasharray: 5 5
            style g_sage fill:#F5F5F5,stroke:#999,stroke-dasharray: 5 5
    """))
    story.append(Spacer(1, 12))

    # =========================================================
    # NAVUSOFT — Bronze only
    # =========================================================
    story.append(p("Navusoft — Operations &amp; Routes (Bronze Only)", H2))
    story.append(p(
        "5 bronze tables for NTX waste operations: customers, work orders, invoicing, "
        "routes, and service agreements. This is the core operational system."))
    story.append(Spacer(1, 4))
    story.append(mermaid("""
        flowchart LR
            subgraph "navusoft_bronze"
                customers[customers<br/>customer_name, type, status<br/>address, service_area<br/>account_rep]
                work_orders[work_orders<br/>order_type, service_type<br/>scheduled_date, driver_id<br/>container_size, tonnage]
                invoices[invoices<br/>invoice_number, line_of_business<br/>haul_charge, tonnage_fee<br/>total_amount, status]
                routes[routes<br/>route_name, route_type<br/>driver_id, truck_id<br/>day_of_week, stop_count]
                agreements[service_agreements<br/>agreement_type, container_size<br/>service_frequency<br/>monthly_rate, haul_rate]
            end
            subgraph "navusoft_silver (planned)"
                s_nav["Silver views TBD<br/>Customer profiles<br/>Route efficiency<br/>Revenue by service type"]
            end
            subgraph "gold (planned)"
                g_nav["Gold tables TBD<br/>Operational metrics<br/>Route profitability<br/>Customer lifetime value"]
            end
            customers -.-> s_nav
            work_orders -.-> s_nav
            invoices -.-> s_nav
            routes -.-> s_nav
            agreements -.-> s_nav
            s_nav -.-> g_nav
            style s_nav fill:#F5F5F5,stroke:#999,stroke-dasharray: 5 5
            style g_nav fill:#F5F5F5,stroke:#999,stroke-dasharray: 5 5
    """))
    story.append(PageBreak())

    # =========================================================
    # CRM — Bronze only
    # =========================================================
    story.append(p("CRM — Generic Sales Pipeline (Bronze Only)", H2))
    story.append(p(
        "5 bronze tables for multi-entity CRM data (ntx, hometown, memphis). "
        "Separate from HubSpot — this is the generic CRM schema for non-HubSpot sources."))
    story.append(Spacer(1, 4))
    story.append(mermaid("""
        flowchart LR
            subgraph "crm_bronze"
                accounts[accounts<br/>account_name, industry<br/>annual_revenue, status<br/>owner, website]
                contacts[contacts<br/>first_name, last_name<br/>email, phone, title<br/>account_id, is_primary]
                opportunities[opportunities<br/>opportunity_name, stage<br/>amount, close_date<br/>probability, account_id]
                activities[activities<br/>activity_type, subject<br/>activity_date, is_completed<br/>account_id, contact_id]
                leads[leads<br/>lead_source, company_name<br/>contact_name, status<br/>assigned_to]
            end
            subgraph "crm_silver (planned)"
                s_crm["Silver views TBD<br/>Unified contacts<br/>Pipeline stages<br/>Activity timeline"]
            end
            subgraph "gold (planned)"
                g_crm["Gold tables TBD<br/>Pipeline analytics<br/>Conversion rates<br/>Lead scoring"]
            end
            accounts -.-> s_crm
            contacts -.-> s_crm
            opportunities -.-> s_crm
            activities -.-> s_crm
            leads -.-> s_crm
            s_crm -.-> g_crm
            style s_crm fill:#F5F5F5,stroke:#999,stroke-dasharray: 5 5
            style g_crm fill:#F5F5F5,stroke:#999,stroke-dasharray: 5 5
    """))
    story.append(Spacer(1, 12))

    # =========================================================
    # FLEET — Bronze only
    # =========================================================
    story.append(p("Fleet — Vehicle Management (Bronze Only)", H2))
    story.append(p(
        "4 bronze tables for multi-entity fleet data (ntx, hometown, memphis). "
        "Vehicles, maintenance, inspections, and fuel tracking."))
    story.append(Spacer(1, 4))
    story.append(mermaid("""
        flowchart LR
            subgraph "fleet_bronze"
                vehicles[vehicles<br/>vehicle_number, vin<br/>make, model, year<br/>vehicle_type, status]
                maintenance[maintenance_orders<br/>order_type, priority<br/>vendor_name, total_cost<br/>labor_hours, parts_cost]
                inspections[inspections<br/>inspection_type, inspector_id<br/>pass_fail, defects_found<br/>next_due_date]
                fuel[fuel_logs<br/>gallons, cost_per_gallon<br/>odometer, fuel_type<br/>station_name]
            end
            subgraph "fleet_silver (planned)"
                s_fleet["Silver views TBD<br/>Vehicle profiles<br/>Maintenance history<br/>Fuel efficiency"]
            end
            subgraph "gold (planned)"
                g_fleet["Gold tables TBD<br/>Fleet utilization<br/>Cost per mile<br/>Compliance status"]
            end
            vehicles -.-> s_fleet
            maintenance -.-> s_fleet
            inspections -.-> s_fleet
            fuel -.-> s_fleet
            s_fleet -.-> g_fleet
            style s_fleet fill:#F5F5F5,stroke:#999,stroke-dasharray: 5 5
            style g_fleet fill:#F5F5F5,stroke:#999,stroke-dasharray: 5 5
    """))
    story.append(PageBreak())

    # =========================================================
    # SUPPORTING INFRASTRUCTURE
    # =========================================================
    story.append(p("Supporting Infrastructure", H2))
    story.append(p(
        "Schemas that power the medallion system but don't belong to a vendor service. "
        "Forge orchestrates refreshes, audit monitors security, daemon tracks ETL state."))
    story.append(Spacer(1, 4))
    story.append(mermaid("""
        flowchart TD
            subgraph "forge — Refresh Orchestration"
                refresh_all[refresh_all<br/>master orchestrator]
                refresh_all --> r_pipeline[refresh_pipeline_summary]
                refresh_all --> r_velocity[refresh_deal_velocity]
                refresh_all --> r_aging[refresh_deal_aging]
                refresh_all --> r_stage[refresh_deal_stage_flow]
                refresh_all --> r_winloss[refresh_win_loss_analysis]
                refresh_all --> r_forecast[refresh_forecast]
                refresh_all --> r_rep[refresh_rep_activity]
                refresh_all --> r_coverage[refresh_rep_pipeline_coverage]
                refresh_all --> r_quota[refresh_quota_attainment]
                refresh_all --> r_health[refresh_customer_health]
                refresh_all --> r_territory[refresh_territory_summary]
                refresh_all --> r_tsummary[refresh_ticket_summary]
                refresh_all --> r_taging[refresh_ticket_aging]
                refresh_all --> r_tcompany[refresh_ticket_by_company]
                refresh_all --> r_contract[refresh_contract_details]
                refresh_all --> r_product[refresh_product_mix]
                refresh_all --> r_quote[refresh_quote_pipeline]
                refresh_all --> r_csat[refresh_customer_satisfaction]
                refresh_all --> r_owner[refresh_owner_performance]
                refresh_all --> r_funnel[refresh_contact_funnel]
                refresh_all --> r_company[refresh_companies]
            end
            subgraph "audit — Security Monitoring"
                security_drift_log[security_drift_log<br/>check results + timestamps]
                vault_access_log[vault_access_log<br/>secret access audit trail]
                check_security[check_gold_security<br/>14 security properties]
                run_tests[run_gold_security_tests<br/>RLS, policies, roles, JWT]
                cron[cron_security_check<br/>hourly at :30]
                cron --> check_security
                cron --> run_tests
                check_security --> security_drift_log
                run_tests --> security_drift_log
            end
            subgraph "daemon — ETL Runtime"
                jobs[jobs<br/>status, priority, payload]
                run_history[run_history<br/>rows_extracted/loaded<br/>duration_ms]
                watermarks[watermarks<br/>sync cursors per table]
                service_state[service_state<br/>enabled, next_due_at]
                migration_history[migration_history<br/>filename, applied_at]
            end
            subgraph "rbac + public — Auth"
                user_roles["public.user_roles<br/>email, role, entities<br/>is_active, suspended_at"]
                token_hook["rbac.custom_access_token_hook<br/>JWT to tenant_id, role<br/>entities, permissions"]
                user_roles --> token_hook
            end
            refresh_all --> check_security
            style refresh_all fill:#E8F0EC,stroke:#2D6B4A
            style cron fill:#FFF8E6,stroke:#D4A017
    """))
    story.append(Spacer(1, 8))

    # =========================================================
    # OBJECT COUNT SUMMARY
    # =========================================================
    story.append(p("Object Count Summary", H2))
    story.append(tbl(["Schema", "Tables", "Mat Views", "Views", "Functions", "Total"], [
        [p("<b>hubspot_bronze</b>", CELL), p("23", CELL), p("—", CELL), p("—", CELL), p("—", CELL), p("23", CELL)],
        [p("<b>sage_bronze</b>", CELL), p("5", CELL), p("—", CELL), p("—", CELL), p("—", CELL), p("5", CELL)],
        [p("<b>navusoft_bronze</b>", CELL), p("5", CELL), p("—", CELL), p("—", CELL), p("—", CELL), p("5", CELL)],
        [p("<b>crm_bronze</b>", CELL), p("5", CELL), p("—", CELL), p("—", CELL), p("—", CELL), p("5", CELL)],
        [p("<b>fleet_bronze</b>", CELL), p("4", CELL), p("—", CELL), p("—", CELL), p("—", CELL), p("4", CELL)],
        [p("<b>hubspot_silver</b>", CELL), p("—", CELL), p("16", CELL), p("6", CELL), p("—", CELL), p("22", CELL)],
        [p("<b>gold</b>", CELL), p("25", CELL), p("—", CELL), p("2", CELL), p("1", CELL), p("28", CELL)],
        [p("<b>forge</b>", CELL), p("—", CELL), p("—", CELL), p("—", CELL), p("21", CELL), p("21", CELL)],
        [p("<b>audit</b>", CELL), p("2", CELL), p("—", CELL), p("—", CELL), p("3", CELL), p("5", CELL)],
        [p("<b>rbac</b>", CELL), p("—", CELL), p("—", CELL), p("—", CELL), p("1", CELL), p("1", CELL)],
        [p("<b>public</b>", CELL), p("1", CELL), p("—", CELL), p("—", CELL), p("—", CELL), p("1", CELL)],
        [p("<b>daemon</b>", CELL), p("5", CELL), p("—", CELL), p("—", CELL), p("—", CELL), p("5", CELL)],
        [p("<b>TOTAL</b>", CELL), p("<b>75</b>", CELL), p("<b>16</b>", CELL), p("<b>8</b>", CELL), p("<b>26</b>", CELL), p("<b>125</b>", CELL)],
    ], [L_USABLE * 0.20, L_USABLE * 0.14, L_USABLE * 0.16, L_USABLE * 0.14, L_USABLE * 0.18, L_USABLE * 0.14]))
    story.append(Spacer(1, 8))

    # RLS Pattern
    story.append(p("RLS Pattern (All Gold Tables)", H2))
    story.append(p(
        "Every gold table has RLS + FORCE ROW LEVEL SECURITY. Single policy pattern "
        "using gold.current_entities() reading JWT app_metadata. service_role revoked entirely."))
    story.append(Spacer(1, 4))
    story.append(tbl(["JWT entities[]", "Access"], [
        [p("<font face='Courier'>['*']</font>", CELL), p("Wildcard — sees all entities (consolidated view)", CELL)],
        [p("<font face='Courier'>['ntx']</font>", CELL), p("Single entity — sees only NTX data", CELL)],
        [p("<font face='Courier'>['ntx','hometown']</font>", CELL), p("Multi-entity — sees NTX + Hometown", CELL)],
        [p("<font face='Courier'>[]</font>", CELL), p("Empty — sees nothing (disabled/unassigned user)", CELL)],
    ], [L_USABLE * 0.35, L_USABLE * 0.65]))


def validate_mermaid_diagrams(build_fn):
    """Pre-validate every mermaid diagram before building the PDF.

    Extracts all mermaid() calls, renders each one, and reports failures
    with the actual Mermaid CLI error so you can fix them before wasting
    a full PDF build cycle.
    """
    import re, inspect, textwrap

    source = inspect.getsource(build_fn)
    # Find all mermaid(""" ... """) blocks
    pattern = r'mermaid\(\s*"""(.*?)"""\s*\)'
    matches = re.findall(pattern, source, re.DOTALL)

    if not matches:
        print("No mermaid diagrams found to validate.")
        return True

    all_passed = True
    for i, code in enumerate(matches, 1):
        mmd_file = tempfile.NamedTemporaryFile(suffix=".mmd", delete=False, mode="w")
        mmd_file.write(code.strip())
        mmd_file.close()
        png_path = mmd_file.name.replace(".mmd", ".png")

        try:
            result = subprocess.run(
                ["npx", "--yes", "@mermaid-js/mermaid-cli",
                 "-i", mmd_file.name,
                 "-o", png_path,
                 "-b", "transparent",
                 "-s", "1"],
                capture_output=True, text=True, timeout=30,
            )
            if not Path(png_path).exists() or result.returncode != 0:
                all_passed = False
                # Extract the useful parse error line
                err = result.stderr or result.stdout or "(no output)"
                # Find the "Parse error on line" portion
                parse_match = re.search(r'(Parse error on line.*?)(?:Parser3|$)', err, re.DOTALL)
                err_msg = parse_match.group(1).strip() if parse_match else err[:300]
                print(f"  FAIL  Diagram {i}: {err_msg}")
            else:
                print(f"  OK    Diagram {i}")
        except Exception as e:
            all_passed = False
            print(f"  FAIL  Diagram {i}: {e}")
        finally:
            Path(mmd_file.name).unlink(missing_ok=True)
            Path(png_path).unlink(missing_ok=True)

    if not all_passed:
        print("\nFix the failing diagrams above before generating the PDF.")
        sys.exit(1)
    else:
        print(f"All {len(matches)} diagrams validated.\n")
    return all_passed


def build_doc_landscape(output_path, doc_title, build_fn):
    """Create a branded landscape PDF."""
    from reportlab.lib.pagesizes import letter, landscape as ls
    page = ls(letter)
    lw, lh = page
    margin = 0.5 * inch
    doc = SimpleDocTemplate(str(output_path), pagesize=page,
                            leftMargin=margin, rightMargin=margin,
                            topMargin=margin, bottomMargin=0.6 * inch)
    story = []
    p = lambda t, s=BODY: Paragraph(t, s)
    build_fn(story, p)

    def footer_func(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(margin, 0.35 * inch,
                          f"Greenmark Waste Solutions  |  {doc_title}  |  "
                          f"{datetime.now().strftime('%Y-%m-%d')}")
        canvas.drawRightString(lw - margin, 0.35 * inch, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer_func, onLaterPages=footer_func)
    print(f"PDF written to: {output_path}")


if __name__ == "__main__":
    print("Validating mermaid diagrams...")
    validate_mermaid_diagrams(content)
    build_doc_landscape(OUTPUT, "Database Entity Map — Greenmark Waste Solutions", content)
