# Interview Q&A — Performance Tuning

**Q1. A Spark job is slow. Where do you start?**
> With the Spark UI, not with configuration changes. I find the stage that dominates wall-clock time, then look at the task-duration distribution (median vs max), shuffle read/write sizes, spill columns, and GC time. Those four signals map to skew, shuffle volume, memory pressure, and GC respectively. Only after identifying which one it is do I change anything, and I change one thing at a time so I can attribute the improvement.

**Q2. How do you recognize data skew, and how do you fix it?**
> In the stage page, nearly all tasks finish quickly while one or a few run far longer, and their shuffle read size is many times the median. Fixes in order: rely on AQE skew join handling (verify it is enabled and that the join is a sort-merge join); filter out or separately process hot keys such as NULLs and sentinel values; broadcast the smaller table if it fits; and as a last resort salt the key — add a random suffix on the large side and replicate the small side across the suffix range — accepting extra complexity and data duplication.

**Q3. What does AQE actually do, and what are its limits?**
> AQE re-plans a query at runtime using real statistics gathered at shuffle boundaries. It coalesces small shuffle partitions, switches a sort-merge join to a broadcast join when a side turns out small after filtering, and splits skewed partitions in joins. Its limits: it only learns sizes after a shuffle has run, it does not fix a poor physical data layout or small-file problem, and it handles skew in joins but is less helpful for heavily skewed aggregations, where two-phase aggregation or salting may still be needed.

**Q4. Disk cache versus `df.cache()` — when do you use each?**
> The Databricks disk cache stores raw Parquet/Delta file data on workers' local SSDs, is populated automatically on read, and is invalidated automatically when files change — ideal for repeated reads of hot tables. `df.cache()` stores a computed DataFrame in executor memory/disk, is lazy, and does not detect upstream changes, and it competes with execution memory. I use the disk cache by default and reach for `df.cache()` only when an expensive intermediate DataFrame feeds multiple actions in the same job, and I `unpersist()` it when finished.

**Q5. What is spill, and is it a bug?**
> Spill happens when a sort, aggregation, or join cannot fit its working set in execution memory, so Spark writes intermediate data to disk and reads it back. It is not an error, but it can slow a stage substantially. I look at the Spill (Memory) and Spill (Disk) columns, then address the cause: partitions too large (raise shuffle partitions or repartition), a skewed partition (fix skew), insufficient memory per task (memory-optimized nodes), or row explosion from `explode`/many-to-many joins (filter or deduplicate first).

**Q6. How would you choose `spark.sql.shuffle.partitions`?**
> The default of 200 is a static guess. The goal is partitions of roughly 100–200 MB each: too few produce oversized partitions that spill, too many produce tiny tasks dominated by scheduling overhead. With AQE enabled I set it somewhat high and let partition coalescing trim it at runtime; without AQE I estimate from the shuffle data size seen in the Spark UI and set it accordingly per job.

**Q7. Why are Python UDFs a performance concern, and what do you do instead?**
> A row-at-a-time Python UDF serializes data between the JVM and a Python process and is opaque to the Catalyst optimizer, so predicate pushdown and code generation cannot be applied through it. I replace UDFs with built-in functions or SQL expressions where possible, and when custom logic is unavoidable I use pandas (vectorized) UDFs, which process Arrow batches instead of single rows.
