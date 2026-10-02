# Talking points — condensed for verbal delivery

**Opening line:**

> "I'd make onboarding a table a config change: one generic pipeline driven by a control table, with all behavior defined as data, not code."

## Mnemonic: Describe → Dispatch → Deliver → Document

### 1. Describe (metadata)
- Control table: source, load type, watermark, keys, SCD type, target, DQ rules, schedule group
- Config lives in Git, validated in CI, synced to the control table on release

### 2. Dispatch (orchestration)
- ADF Lookup → ForEach (batchCount up to 50) → Execute Pipeline per table
- Say the constraint out loud: no nested ForEach, Lookup capped at 5,000 rows, so child pipelines and schedule groups
- Secrets via Key Vault-backed linked services

### 3. Deliver (execution)
- One generic Databricks job: Bronze ingest, Silver MERGE, SCD2 by config
- Idempotent by design: MERGE / partition overwrite keyed by run id
- Advance the watermark only after the write commits

### 4. Document (audit)
- Audit table per run: rows, status, errors; dashboards and alerts on top
- One table fails, the rest continue; re-run only failures

**Closing line:**

> "The measure of success is how many tables a new engineer can onboard in a day without touching pipeline code."

## Delivery tip
If the interviewer is Databricks-heavy, spend more time on the generic job and schema drift policy. If Azure/ADF-heavy, spend more on orchestration limits and parameterized linked services.

## Likely follow-ups to prep for
- How do you handle a source that has no reliable watermark column?
- How do you protect the source database from 50 parallel extracts?
- How would you test the framework itself, not just the tables it loads?
- When would you stop using the generic path and build a custom pipeline?
