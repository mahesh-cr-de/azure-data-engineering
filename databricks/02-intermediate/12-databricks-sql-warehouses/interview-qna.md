# Interview Q&A — Databricks SQL & SQL Warehouses

**Q1. Why would you run BI queries on a SQL warehouse instead of an all-purpose cluster?**
> A SQL warehouse is purpose-built for SQL serving: it has Photon enabled, result and disk caching, automatic scale-out based on query concurrency, and (on serverless) startup in seconds. An all-purpose cluster is sized and priced for interactive development, has no concurrency-based scaling for many BI users, and is billed at a higher DBU rate. Putting dashboards on all-purpose clusters usually means paying more for worse concurrency behavior, and it also lets analysts run arbitrary code on a shared development resource.

**Q2. Serverless, Pro, or Classic — how do you choose?**
> Default to serverless where it is available: near-instant startup, Intelligent Workload Management, and no cluster infrastructure to manage, which makes aggressive auto-stop practical and lowers idle cost. Choose Pro when serverless is not available in the region or compute must stay inside your own VNet/subscription, and you still need features like materialized views, streaming tables, and federation. Classic is only appropriate for light, cost-sensitive workloads that do not need those features. The decision is mostly about network/compliance constraints and startup latency, not raw query speed.

**Q3. A dashboard is slow only at 9 AM when everyone logs in. Scale up or scale out?**
> Scale out. Individual queries are fine at other times, so the symptom is queueing under concurrency, not insufficient per-query resources. I would confirm in Query History that queued time is high while execution time is normal, then raise the warehouse's max cluster count so additional clusters spin up as concurrent queries grow. Increasing the T-shirt size would raise cost without reducing queue time, since each query would still wait for a free slot.

**Q4. One monthly finance query takes 40 minutes. What do you check?**
> That is a single-query problem, so I open the Query Profile rather than touching cluster counts. I check bytes read versus rows returned (poor pruning or small files → `OPTIMIZE` / clustering / better predicates), whether any operator spills to disk (warehouse too small → scale up), and whether a join is shuffling or skewed (reorder, filter earlier, broadcast the small side). If the result is reused by multiple reports, I would also precompute it as a materialized view.

**Q5. When would you use a materialized view versus a regular view or a table built by a job?**
> A regular view recomputes on every query, so it is only suitable for cheap logic or when always-fresh results matter. A materialized view stores the computed result and refreshes incrementally, which is ideal for expensive, widely shared aggregations behind dashboards without hand-writing refresh orchestration. A job-built table gives full control (custom logic, complex dependencies, non-SQL steps) at the cost of owning scheduling and failure handling. I prefer materialized views when the logic is pure SQL and the refresh semantics fit.

**Q6. How do you control and attribute SQL warehouse cost?**
> Right-size per workload rather than sharing one giant warehouse, set auto-stop appropriately (short on serverless), cap max clusters, and separate warehouses by team or workload type so spend is attributable. Tag warehouses and use billing system tables to report DBUs per warehouse and tag. Finally, review the most expensive queries in Query History — often a few unoptimized queries or an unnecessarily aggressive dashboard refresh schedule dominate spend.
