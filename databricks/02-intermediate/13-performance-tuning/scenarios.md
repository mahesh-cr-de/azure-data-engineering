# Scenarios — Performance Tuning

### Scenario 1 — "One task runs for 45 minutes while the other 199 finish in 20 seconds"

**Setup:** A daily join of `orders` (2B rows) to `customers` takes over an hour. The Spark UI shows a single straggler task in the join stage.

**How to reason through it:**
1. Confirm skew: compare max vs median task duration and shuffle read size in the stage page; the straggler reads far more data.
2. Identify the hot key — a quick `groupBy("customer_id").count().orderBy(desc("count"))` usually reveals `NULL` or a default `-1` customer carrying a large share of rows.
3. If the hot key is meaningless (NULL / sentinel), filter it out of the join and handle it separately (e.g., union back as unmatched rows) rather than shuffling it to one task.
4. Verify AQE skew join handling is on; if the customer table is small enough after column pruning, broadcast it instead and remove the shuffle entirely.
5. If a genuinely large real customer is the hot key and AQE is insufficient, apply salting on that join.
6. Re-run and confirm max task duration is now close to the median.

### Scenario 2 — "The cluster was doubled but the job did not get faster"

**Setup:** A team doubled worker count after a slow job; runtime barely changed.

**How to reason through it:**
1. Adding workers only helps if work is parallelizable across more tasks. If a skewed task or a single big partition dominates, extra workers sit idle.
2. Check the stage: few long tasks with a large max/median ratio indicates skew; a small number of partitions (e.g., after `coalesce(10)` or reading a few huge files) caps parallelism regardless of cluster size.
3. Fix the actual bottleneck — repartition for parallelism, fix skew, or reduce shuffle volume — and then right-size the cluster to the improved job.
4. Make the point explicitly: scaling out is a remedy for insufficient parallel capacity, not for uneven work or inefficient plans.

### Scenario 3 — "Jobs are slow and Spill (Disk) shows hundreds of GB"

**Setup:** A nightly aggregation stage reports large Spill (Memory) and Spill (Disk).

**How to reason through it:**
1. Check partition sizes: with the default 200 shuffle partitions on a multi-TB shuffle, each partition is far above the ~100–200 MB target, so each task's working set exceeds execution memory.
2. Raise shuffle partitions (or confirm AQE is active) so each task handles a manageable amount of data.
3. Look for a `explode` or many-to-many join earlier in the plan inflating row counts; filter or deduplicate before it.
4. If spill persists with correct partition sizing, move to a memory-optimized worker type so each task has more memory.
5. Validate by comparing spill totals and stage duration before/after, and avoid enabling `df.cache()` as a fix — it would compete for the same memory.

### Scenario 4 — "A report re-reads the same Delta table 12 times in one notebook"

**Setup:** A notebook runs 12 queries against the same 500 GB Delta table, each taking several minutes.

**How to reason through it:**
1. Check whether the cluster uses cache-accelerated (local NVMe) worker types; the disk cache then serves repeated file reads automatically after the first pass.
2. If most queries share a filtered/aggregated subset, materialize that subset once (a temp view with `df.cache()` after a selective filter, or a Delta table) and run the 12 queries against it.
3. Call `unpersist()` when done so cached data does not keep occupying executor memory.
4. Also check data layout (clustering/Z-ORDER on filter columns) — caching speeds repeated reads, but good pruning reduces the first read too.
