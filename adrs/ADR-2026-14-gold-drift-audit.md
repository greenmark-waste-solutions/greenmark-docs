# ADR-2026-14: Gold Security Drift Audit

- **Status**: Accepted
- **Date**: 2026-03-09
- **Owner**: Daniel Shanklin / Director of AI & Technology
- **Related**: ADR-2026-04, ADR-2026-09, ADR-2026-11

## Context

- Security configurations (RLS policies, grants, FORCE RLS) can drift over time: manual SQL, failed migrations, accidental changes.
- A gold table missing RLS is a data breach — this must be detected before it's exploited.
- PostgreSQL's system catalogs (`pg_class`, `pg_policies`, `information_schema.role_table_grants`) contain the ground truth for security state.

## Decision

- A drift audit function `audit.check_gold_security(p_table TEXT)` runs against every gold table on a schedule.
- The function checks: RLS enabled, FORCE RLS enabled, at least one policy exists, no grants to `anon` or `public`, no grants to `service_role`, entity column exists.
- Any FAIL result triggers an alert via the existing ALERT_WEBHOOK_URL (Slack/PagerDuty).
- The forge tool runs drift audit after every gold refresh and after every migration.

## Checks

```sql
CREATE FUNCTION audit.check_gold_security(p_table TEXT)
RETURNS TABLE(check_name TEXT, status TEXT) AS $$
BEGIN
    -- RLS enabled
    RETURN QUERY SELECT 'rls_enabled',
        CASE WHEN relrowsecurity THEN 'OK' ELSE 'FAIL' END
        FROM pg_class WHERE relname = p_table AND relnamespace = 'gold'::regnamespace;

    -- FORCE RLS enabled
    RETURN QUERY SELECT 'force_rls',
        CASE WHEN relforcerowsecurity THEN 'OK' ELSE 'FAIL' END
        FROM pg_class WHERE relname = p_table AND relnamespace = 'gold'::regnamespace;

    -- At least one RLS policy exists
    RETURN QUERY SELECT 'policy_exists',
        CASE WHEN EXISTS (
            SELECT 1 FROM pg_policies WHERE schemaname = 'gold' AND tablename = p_table
        ) THEN 'OK' ELSE 'FAIL' END;

    -- No anon grant
    RETURN QUERY SELECT 'no_anon_grant',
        CASE WHEN NOT EXISTS (
            SELECT 1 FROM information_schema.role_table_grants
            WHERE table_schema = 'gold' AND table_name = p_table AND grantee = 'anon'
        ) THEN 'OK' ELSE 'FAIL' END;

    -- No service_role grant
    RETURN QUERY SELECT 'no_service_role_grant',
        CASE WHEN NOT EXISTS (
            SELECT 1 FROM information_schema.role_table_grants
            WHERE table_schema = 'gold' AND table_name = p_table AND grantee = 'service_role'
        ) THEN 'OK' ELSE 'FAIL' END;
END;
$$ LANGUAGE plpgsql;
```

## Consequences

- Security drift is detected within one audit cycle (minutes, not days).
- Forge tool refuses to complete a refresh if drift audit fails post-refresh.
- Audit results are logged to `audit.security_checks` table for historical tracking.
- False positives are possible during migrations — audit should be suppressed during active DDL.
