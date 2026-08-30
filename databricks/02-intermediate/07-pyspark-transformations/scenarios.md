# Scenarios — PySpark Transformations, Joins & Partitioning Strategy

### Scenario 1 — "Our nightly job writes 40,000 tiny files and downstream queries have gotten slow"

**Setup:** A pipeline ingests hourly data, partitions the output table by `event_date`, and after a few months of daily runs, each day's partition directory has hundreds of tiny files instead of a handful of well-sized ones. Downstream BI queries have slowed noticeably.

**How to reason through it:**
1. Name the mechanism: file count is driven by in-memory partition count at write time, not by the on-disk `partitionBy` column itself. If the DataFrame going into the writer has, say, 200 in-memory partitions but each day only has a modest amount of data, you get up to 200 small files per day regardless of the partition scheme.
2. Check how the DataFrame arrived at that partition count — likely a wide operation upstream left it at the default `spark.sql.shuffle.partitions` (200), which was never adjusted down for the actual daily data volume.
3. Fix at write time: `repartition(n)` (or `coalesce(n)` if already reasonably distributed) to a partition count sized so each resulting file lands around 128MB–1GB, ideally computed from expected daily volume rather than hardcoded.
4. For the accumulated backlog of small files already written, mention `OPTIMIZE` (Databricks/Delta-specific, Topic 08) as the remediation tool for existing tables rather than trying to rewrite history manually.
5. Senior framing: this is a "the on-disk partition column was fine, the write-time in-memory partitioning wasn't" answer — precisely the distinction interviewers are listening for.

### Scenario 2 — "A join works fine in dev on sampled data but times out in production on the full dataset"

**Setup:** A join between two large tables runs in seconds against a 1% sample in dev, but the same code times out against full production volume.

**How to reason through it:**
1. First hypothesis: the join strategy that worked on the sample (likely a broadcast join, since a 1% sample of even a large table often falls under the broadcast threshold) doesn't hold at full scale — Spark silently falls back to a Sort-Merge Join once the "small" side isn't small anymore, and nobody re-validated the plan against realistic data volume.
2. Confirm via `explain()` on both the sampled and full-scale query — if the physical plan differs (Broadcast vs. SMJ), that's the root cause, not a resource/cluster-size problem.
3. If SMJ is genuinely correct at full scale (both sides are large), the next question is whether either side has skew that only manifests at full volume — a sample can accidentally smooth over a skewed key that dominates in the full dataset.
4. Practical takeaway to state explicitly: dev/sample testing needs to validate the *plan shape* (via `explain()`), not just correctness of output — a query that's correct on a sample but chose its physical strategy based on sample-sized statistics can behave completely differently in production, which is a common and painful surprise for teams that only test on small data.

### Scenario 3 — "Design a join for two tables where one is 5GB but frequently updated, and correctness matters more than speed"

**Setup:** An interviewer asks how you'd approach a join between a large, slowly-changing fact table and a 5GB reference table that's refreshed several times a day, where getting stale broadcast data would cause real business errors (e.g., pricing).

**How to reason through it:**
1. 5GB is past the default broadcast threshold and likely close to the edge of what's safe to broadcast even if raised — worth stating the trade-off explicitly rather than reflexively forcing a broadcast: a broadcast join copies the *entire* table to every executor's memory, so at 5GB you're spending real cluster memory per executor for the convenience of avoiding a shuffle.
2. Raise the actual sensitivity in the prompt: broadcasting a frequently-updated table risks executors holding a broadcast variable built from a slightly stale read if the underlying table changes mid-job — for Delta tables this is mitigated somewhat by Delta's snapshot isolation (each query sees a consistent version), but it's worth naming that Spark's broadcast is a point-in-time copy, not a live view.
3. Recommend validating with `explain()` and actual runtime metrics rather than assuming broadcast is automatically right just because the table is "the smaller one" — if 5GB doesn't comfortably fit alongside other executor memory needs (caching, shuffle buffers, other concurrent jobs on a shared cluster), a Sort-Merge Join with a well-chosen shuffle partition count can be the more *robust* choice even if a broadcast would technically be faster in isolation.
4. This scenario rewards showing judgment about trade-offs (speed vs. memory pressure vs. correctness risk) rather than reciting "small table = broadcast" as a rule with no limits.
