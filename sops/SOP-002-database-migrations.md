# SOP-002: Database Migrations

- **Effective**: 2026-03-11
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Applies to**: Anyone writing SQL migrations for Greenmark's Supabase databases

## BLUF

Two migration systems write to the same Postgres database. Data-daemon owns bronze schemas (raw vendor data). Cerebro owns everything else (silver, gold, auth, RBAC). Follow this SOP to know which system to use, how to apply migrations, and how to verify they ran.

## Schema Ownership

| Schema | Owner | Why | Migration System |
|--------|-------|-----|-----------------|
| `daemon` | data-daemon | Job queue, migration history, daemon lifecycle | data-daemon numbered SQL |
| `hubspot_bronze` | data-daemon | Raw HubSpot extraction target | data-daemon numbered SQL |
| `sage_bronze` | data-daemon | Raw Sage Intacct extraction | data-daemon numbered SQL |
| `navusoft_bronze` | data-daemon | Raw Navusoft extraction | data-daemon numbered SQL |
| `crm_bronze` | data-daemon | Raw CRM extraction (legacy) | data-daemon numbered SQL |
| `fleet_bronze` | data-daemon | Raw Fleetio extraction | data-daemon numbered SQL |
| `vault` | data-daemon | Vendor API credentials | data-daemon numbered SQL |
| `gold` | cerebro | Business metrics, RLS-protected | Supabase CLI |
| `silver` / per-vendor silver | cerebro | Normalized views for app consumption | Supabase CLI |
| `public` | cerebro | User auth, roles | Supabase CLI |
| `rbac` | cerebro | Role/permission lookups | Supabase CLI |
| `audit` | cerebro | Drift detection, security checks | Supabase CLI |
| `platform` | cerebro | Config, feature flags | Supabase CLI |
| `forge` / `secure` | cerebro | SECURITY DEFINER refresh functions | Supabase CLI |

**The clean rule**: If you're writing SQL that creates tables where the data-daemon extracts raw vendor data into, it goes in data-daemon. Everything else goes in cerebro.

## Migration System A: Data-Daemon

### Where migrations live
```
data-daemon/migrations/NNN_description.sql
```
Numbered sequentially: `001_`, `002_`, ..., `019_`.

### How they're tracked
Table: `daemon.migration_history` (columns: `id`, `filename`, `applied_at`).
Created automatically on first run.

### How to apply
**Migrations auto-run on data-daemon startup.** To apply pending migrations:

1. **Production (Railway):** Push to `main` branch. Railway redeploys. Startup runs `src/db/migrate.py` which applies any unapplied `.sql` files in sorted order.

2. **Local / Manual:**
   ```bash
   cd data-daemon
   DATABASE_URL=postgresql://postgres:<password>@db.wwmcgtyngnziepeynccz.supabase.co:5432/postgres \
     python -c "from src.db.pool import get_pool; from src.db.migrate import run_migrations; p=get_pool(); run_migrations(p.getconn())"
   ```

### How to verify
```sql
SELECT filename, applied_at FROM daemon.migration_history ORDER BY applied_at;
```
(Requires direct DB access or exposing `daemon` schema in PostgREST.)

### How to write a new migration
1. Create `data-daemon/migrations/NNN_description.sql` (next number in sequence)
2. Only touch bronze schemas, daemon schema, or vault
3. Use `IF NOT EXISTS` / `IF EXISTS` for idempotency
4. Test against Cerebro Test project (`izmuckuepryqneebwwol`) first
5. Merge to `main` and deploy

## Migration System B: Cerebro (Supabase CLI)

### Where migrations live
```
cerebro/supabase/migrations/YYYYMMDDHHMMSS_description.sql
```
Timestamped filenames, managed by Supabase CLI.

### How they're tracked
Supabase's internal `supabase_migrations.schema_migrations` table.

### How to apply

1. **Generate a new migration:**
   ```bash
   cd cerebro
   npx supabase migration new description_here
   # Creates: supabase/migrations/YYYYMMDDHHMMSS_description_here.sql
   # Write your SQL in the generated file
   ```

2. **Apply to remote (production):**
   ```bash
   npx supabase db push --linked
   ```

3. **Apply to remote (test):**
   ```bash
   npx supabase db push --db-url postgresql://postgres:<password>@db.izmuckuepryqneebwwol.supabase.co:5432/postgres
   ```

### How to verify
```sql
SELECT version, name FROM supabase_migrations.schema_migrations ORDER BY version;
```
Or in Supabase Dashboard: Database > Migrations.

### How to write a new migration
1. Run `npx supabase migration new <name>`
2. Write SQL for silver, gold, rbac, audit, platform, forge, or public schemas
3. Never touch bronze or daemon schemas
4. Test against Cerebro Test project first
5. Run `npx supabase db push --linked` to apply

## PostgREST Exposed Schemas

PostgREST (the REST API layer) only serves schemas that are explicitly exposed. As of 2026-03-11:

**Currently exposed:** `public`, `graphql_public`, `audit`, `platform`, `rbac`, `gold`

**Not exposed (needs fix):** `hubspot_bronze`, `silver` / per-vendor silver schemas, `daemon`

### How to expose a new schema
Supabase Dashboard > Settings > API > Schema Settings > Add schema to "Exposed schemas" list.

Or via SQL:
```sql
ALTER ROLE authenticator SET pgrst.db_schemas TO 'public,graphql_public,audit,platform,rbac,gold,hubspot_bronze,silver';
NOTIFY pgrst, 'reload config';
```

## Pre-Flight Checklist

Before writing any migration:

- [ ] Confirm which system owns the schema (see table above)
- [ ] Check what's already been applied (`daemon.migration_history` or `supabase_migrations.schema_migrations`)
- [ ] Test against Cerebro Test project first (`izmuckuepryqneebwwol`)
- [ ] Use `IF NOT EXISTS` / `IF EXISTS` for all CREATE/ALTER/DROP statements
- [ ] Include `GRANT` statements if new tables need to be readable by `anon`, `authenticated`, or service roles
- [ ] If creating gold tables: add RLS policy for entity isolation
- [ ] If creating refresh functions: use `SECURITY DEFINER` owned by `svc_etl_runner`

## Known Issues

### Deprecated data-daemon migrations (009, 010, 012, 017)
These migrations create `silver.crm_*` materialized views and old `gold.*` materialized views that have been superseded by cerebro migrations. They still run on data-daemon startup but their objects get overwritten by cerebro. Tracked for cleanup but harmless due to `IF NOT EXISTS`.

### Missing gold tables
As of 2026-03-11, only 5 of 19 planned gold tables exist in production:
- `pipeline_summary`, `deal_velocity`, `owner_performance`, `contact_funnel`, `company_overview`

The remaining 14 are defined in data-daemon migrations 018-019 but belong in cerebro. A new cerebro migration is needed to create them.

## Why This Exists

We discovered that 14 of 19 gold tables were returning 404 from PostgREST because the migrations that create them (in data-daemon) hadn't been deployed. Both migration systems were creating objects in the same schemas with no documented ownership. This SOP prevents future confusion about which system owns what and how to apply pending migrations.

## Exceptions

None. All database schema changes go through one of these two migration systems. No ad-hoc SQL in the Supabase SQL Editor for schema changes (data queries are fine).
