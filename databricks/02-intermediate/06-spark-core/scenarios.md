# Scenarios — Apache Spark Core

### Scenario 1 — "A join that should take minutes is taking hours"

**Setup:** A pipeline joins a 2TB fact table against a 50MB dimension table, and it's running far slower than the team expects for such a size mismatch.

**How to reason through it:**
1. First hypothesis: Spark **should** be doing a broadcast join here (small dimension table gets copied to every executor, avoiding a shuffle of the huge fact table entirely) — if it isn't, that's almost certainly the root cause.
2. Check `spark.sql.autoBroadcastJoinThreshold` — if the dimension table's actual size (post-filtering, in memory, not just file size on disk) exceeds the threshold, Spark falls back to a sort-merge join, which shuffles *both* sides including the 2TB fact table.
3. Check whether the dimension table's size is being **mis-estimated** — if it's read through several transformations before the join (filters, joins with other small tables) without up-to-date statistics, Spark's static cost estimate might not reflect what the table actually shrinks to at runtime; this is precisely the class of problem **Adaptive Query Execution (AQE)** is designed to fix, by re-evaluating join strategy using actual runtime sizes rather than only the static plan-time estimate — worth confirming AQE is enabled if on an older DBR/config.
4. If broadcast still isn't happening automatically, the tactical fix is an explicit `broadcast()` hint (`from pyspark.sql.functions import broadcast; df_fact.join(broadcast(df_dim), ...)`) — but frame this as fixing a symptom; understanding *why* auto-broadcast didn't trigger is the more senior answer.

### Scenario 2 — "One task takes 40 minutes while 199 others finish in 2 minutes"

**Setup:** A `groupBy` aggregation shows classic data skew in the Spark UI — one task massively outlasts the rest, dragging out the whole stage.

**How to reason through it:**
1. Name the mechanism explicitly: a wide transformation like `groupBy` shuffles data so all rows for a given key land on the same partition/task — if one key (or a small number of keys) has disproportionately more rows than others (e.g., a "null" or "unknown" customer_id bucket, or one dominant retail region), the task handling that key does far more work than every other task, and the stage can't finish until the slowest task does.
2. Diagnosis: confirm via the Spark UI's task duration distribution for that stage (long tail is the signature of skew, as opposed to uniformly slow tasks which would suggest a resource/config issue instead) — and if possible, check the actual key distribution (`df.groupBy("key").count().orderBy(desc("count"))`) to confirm which key(s) are the culprit.
3. Fixes to discuss: (a) **salting** the skewed key — adding a random suffix to spread one hot key's rows across multiple synthetic sub-keys, aggregating in two stages; (b) enabling/relying on **AQE's skew join handling**, which can automatically detect and split oversized partitions for skewed joins on modern DBR; (c) if the skew is from a genuinely meaningless bucket (e.g., nulls dumped into one key), consider filtering/handling those separately from the main aggregation logic entirely rather than forcing them through the same join.
4. Mention this is one of the most commonly asked "debug this" Spark questions precisely because it tests whether a candidate understands shuffle mechanics, not just Spark syntax.

### Scenario 3 — "New team member asks: why does my simple filter + count take so long the first time but instant the second time I run it?"

**Setup:** A junior engineer notices re-running the exact same `df.filter(...).count()` cell is dramatically faster the second time and assumes something's broken.

**How to explain it (good teaching-moment scenario for an EM interview):**
1. Explain laziness clearly: the *first* run actually reads all the underlying data from storage and executes the full plan; nothing was computed before the action ran.
2. Ask whether anything was **cached** (`.cache()`/`.persist()`) — if so, the second run reuses the in-memory materialized result from the first run's action instead of re-reading from storage and recomputing, which explains the dramatic speedup.
3. If nothing was explicitly cached, point to other likely explanations: cloud storage read caching (e.g., disk cache on the cluster from the first read), or simply that the underlying files are now warmer in OS/Delta cache layers — but be precise that this is *not* the same guarantee as an explicit `.cache()`, and don't let the junior engineer walk away assuming Spark "remembers" results by default without one.
4. Use it as a coaching opportunity: a good habit is to explicitly `.cache()` a DataFrame only when it will genuinely be reused multiple times downstream (and to `.unpersist()` when done) — caching everything "just in case" wastes cluster memory and can itself cause performance problems (eviction, spill) rather than helping.
