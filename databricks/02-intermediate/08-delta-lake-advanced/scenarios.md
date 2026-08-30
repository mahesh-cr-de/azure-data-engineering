# Scenarios — Delta Lake Advanced

### Scenario 1 — "A bad job overwrote a table with corrupted data, and it's already been an hour"

**Setup:** An engineer's job had a bug that wrote incorrect values into a production Delta table, overwriting the previous good state. The mistake was caught an hour later; multiple downstream jobs may have already read the bad data.

**How to reason through it:**
1. Immediate recovery: since Delta never deletes files in place, the previous good version is still fully reconstructable — `RESTORE TABLE sales TO VERSION AS OF <last_good_version>` (or `TIMESTAMP AS OF`) atomically reverts the table to that state, itself recorded as a new commit (so RESTORE is non-destructive to history too).
2. Identify the correct version to restore to: `DESCRIBE HISTORY sales` lists every commit with its operation type and timestamp, making it straightforward to find the version immediately before the bad write.
3. Address the downstream blast radius explicitly, since this is the part junior candidates often skip: any job that already read and propagated the bad data downstream (aggregations written elsewhere, dashboards refreshed, ML features computed) also needs to be identified and potentially re-run — restoring the source table doesn't retroactively fix already-materialized downstream artifacts.
4. Prevention framing for a senior answer: mention this is exactly the kind of incident that argues for validating writes (row count sanity checks, schema/constraint checks) before a job's write is considered "complete," rather than relying on Time Travel purely as a safety net after the fact.

### Scenario 2 — "MERGE performance has degraded badly as a table has grown"

**Setup:** A nightly MERGE that upserts ~1% of rows into a 2-billion-row Delta table used to take 10 minutes; six months later it takes over 3 hours, even though the source data volume hasn't changed.

**How to reason through it:**
1. Name the mechanism: MERGE has to find matching rows in the target for every source row, which means scanning (or at least statistics-checking) target files — as the table has grown without maintenance, file count and total scan volume have grown with it, even though the *matched* row count is unchanged.
2. Check whether OPTIMIZE has been run regularly — if the table has accumulated many small files over six months (Topic 07, Scenario 1 dynamic, but from continuous MERGE writes instead of streaming), MERGE's target-side scan pays file-open overhead across far more files than necessary.
3. Check whether the target is Z-ordered (or even just partitioned) on the MERGE join key — if the join key isn't the partition column and the table isn't Z-ordered on it, MERGE can't use file-level statistics to skip target files and ends up scanning much more of the table than the 1% match rate would suggest is necessary.
4. Recommend a maintenance cadence going forward — scheduled `OPTIMIZE` (and `ZORDER BY` on the merge key, if it's a stable, frequently-used key) as a recurring job, not a one-time fix — framing this as "MERGE performance degrades gracefully into a maintenance problem if you don't schedule compaction," which is the senior-level insight interviewers want to hear.

### Scenario 3 — "Design the retention and cleanup policy for a table that both feeds ML training snapshots and needs cost control"

**Setup:** An interviewer asks how you'd set up VACUUM and retention policy for a large Delta table where data scientists occasionally need to reproduce a training run against the exact data as of a specific past date, but storage cost from retained old files is also a real concern.

**How to reason through it:**
1. Frame it as a direct trade-off: longer retention (`delta.deletedFileRetentionDuration`, and holding off on aggressive VACUUM) preserves more Time Travel history but costs more in stored, otherwise-unreferenced files; shorter retention saves storage but shrinks the reproducibility window.
2. Propose a two-tier approach rather than picking one blanket policy: keep a moderate default retention (e.g., 30 days) for ad-hoc Time Travel needs, but for specific known milestones (e.g., "the dataset a model was trained on"), explicitly materialize that version into a separate, cheaper-tier archival location (e.g., `RESTORE` into a dated snapshot table, or `deep clone` the version) rather than relying on indefinite retention of the live table's history to cover every possible future need.
3. Note the operational discipline this requires: someone (or an automated job) needs to actually run VACUUM on a schedule with the agreed retention — if it's never run, the cost-control half of the goal silently fails even though the policy exists on paper.
4. Bonus point if raised: mention that `deep clone` (a full physical copy of a table as of a version) is the more robust way to pin an ML training snapshot for the long term, since it doesn't depend on the source table's ongoing retention policy at all once created.
