# Scenarios — Delta Lake Fundamentals

### Scenario 1 — "Two pipelines are writing to the same Delta table and getting failures"

**Setup:** A streaming job continuously appends to a `orders_bronze` table while a separate batch job runs a daily `MERGE` for late-arriving corrections into the same table. The batch job intermittently fails with a `ConcurrentAppendException` / `ConcurrentDeleteReadException`.

**How to reason through it:**
1. Explain the root cause: Delta uses optimistic concurrency control — both writers assume no conflict and race to commit the next log version; when the streaming append and the MERGE's read/write overlap on the same files/partitions, one loses the race and Delta throws a concurrency exception rather than silently corrupting data.
2. Real fix options: (a) partition the table so the batch MERGE only touches partitions the streaming job isn't actively writing to (e.g. merge only into "yesterday and older" partitions), (b) schedule the MERGE window to avoid overlapping with peak streaming writes, (c) rely on Delta's built-in retry logic for transient conflicts (Databricks Runtime auto-retries certain conflict types), or (d) redesign as append-only bronze + a separate silver table where corrections are applied, avoiding concurrent writes to the same physical table entirely.
3. Mention this is a real, common production pattern question — the "aha" the interviewer wants is understanding *why* Delta throws instead of silently losing one writer's data.

### Scenario 2 — "Storage costs on our lake are growing much faster than data volume"

**Setup:** A table is written to hourly via MERGE-based upserts. Storage keeps growing well beyond what the logical row count would suggest.

**Diagnosis path:**
1. Ask: is VACUUM ever run? By default, every "removed" file from every MERGE/UPDATE/DELETE sits in storage for 7+ days before it's eligible for physical deletion — high-frequency MERGE tables accumulate huge numbers of orphaned files fast.
2. Check for small-file bloat separately from VACUUM — if OPTIMIZE isn't scheduled, hourly writes create many small files that also inflate storage and, more importantly, hurt read performance.
3. Recommend: schedule `OPTIMIZE` (or enable Auto Optimize/Optimized Writes) after write-heavy windows, and schedule `VACUUM` on a cadence matched to your actual time-travel/audit requirements (e.g., weekly `VACUUM RETAIN 168 HOURS` if 7-day rollback is the real business need — don't go below what compliance/rollback actually requires).
4. Caveat to raise proactively: shortening VACUUM retention below 7 days requires explicitly overriding a safety check (`spark.databricks.delta.retentionDurationCheck.enabled`) and risks breaking any query or streaming read still referencing older files — flag this as a real operational risk, not just a config toggle.

### Scenario 3 — "Design the load pattern for a daily CDC feed with deletes"

**Setup:** You receive a daily extract from a source system that includes inserted, updated, and hard-deleted rows (a `_change_type` column with insert/update/delete). Design how you'd land this into a Delta silver table.

**Expected design talk-through:**
1. Land the raw extract as-is into a bronze Delta table (append-only, full audit trail, `_ingested_at` column) — never mutate bronze.
2. In silver, use `MERGE INTO silver_table AS t USING bronze_batch AS s ON t.id = s.id WHEN MATCHED AND s._change_type = 'delete' THEN DELETE WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED AND s._change_type != 'delete' THEN INSERT *`.
3. Mention idempotency: since MERGE keys on business key + is naturally idempotent, re-running the same day's batch twice (e.g., after a pipeline retry) doesn't double-insert or corrupt state — call this out explicitly, it's a common follow-up question ("what if this job fails halfway and reruns?").
4. If SCD Type 2 history is required instead of overwrite, extend this to a merge that closes out the previous "current" row (set `is_current = false`, `end_date = today`) and inserts a new current row — worth sketching the MERGE `WHEN MATCHED` branch that does the row-versioning if asked.

### Scenario 4 — "A dashboard is showing stale/inconsistent numbers mid-ETL"

**Setup:** Business users complain a Databricks SQL dashboard sometimes shows partial-looking numbers (e.g., some regions updated, others not) right after the nightly job runs.

**How to explain the likely (non-)cause and the real cause:**
1. First, reassure: Delta's snapshot isolation guarantees a reader never sees a *partially committed* single transaction — so it's not that one MERGE is half-applied.
2. The real cause is almost always a **multi-step pipeline**: if the nightly job runs several separate MERGE/INSERT statements across several tables (or partitions) sequentially, a dashboard querying mid-pipeline will see table N fully updated and table N+1 not yet started — each is individually atomic, but the *pipeline as a whole* isn't one transaction.
3. Fixes to discuss: publish to a "staging" schema and do an atomic `swap`/rename at the very end (blue-green pattern), or gate the dashboard/downstream consumers behind a pipeline "success" signal (e.g., a Workflow completion event or a `_SUCCESS` marker table) rather than letting them query tables that are mid-refresh.
