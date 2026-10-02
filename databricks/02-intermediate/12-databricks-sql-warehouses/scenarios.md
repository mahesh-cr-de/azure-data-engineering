# Scenarios — Databricks SQL & SQL Warehouses

### Scenario 1 — "The executive dashboard times out every Monday morning"

**Setup:** 150 business users open the same Power BI report on Monday at 9 AM. The Pro SQL warehouse is a Medium with 1 max cluster. Queries sit queued, some time out.

**How to reason through it:**
1. Confirm the diagnosis in Query History: execution time per query is acceptable, but queued time is high only during the peak window. That points to concurrency, not query inefficiency.
2. Raise max clusters (for example 1 → 4) so the warehouse scales out under load and scales back in afterward; keep the size unchanged.
3. Reduce redundant work: most of those 150 users run the same few queries, so make sure the result cache can serve them (identical query text, data unchanged) and consider a materialized view for the heavy aggregation behind the report.
4. If startup latency at 9 AM is also a complaint, evaluate moving to serverless, or schedule a pre-warm query shortly before the peak on Pro.
5. Close the loop: re-check queued time the following Monday and right-size max clusters from the observed peak rather than guessing.

### Scenario 2 — "Migrating analysts off an always-on all-purpose cluster"

**Setup:** Analysts run SQL on a shared all-purpose cluster that runs 24x7. Cost is high and a few heavy queries starve everyone else.

**How to reason through it:**
1. Inventory what runs there: pure SQL (move to a warehouse) versus Python/ML notebooks (stay on a cluster/job).
2. Create separate warehouses by workload — e.g., `bi-dashboards` (serverless, auto-stop short, scale-out enabled) and `adhoc-analytics` (smaller, capped max clusters) — so one team's heavy query cannot starve dashboards.
3. Grant `CAN USE` to the right groups and keep data access governed by Unity Catalog grants rather than cluster configuration.
4. Tag each warehouse by team and report DBUs per tag from billing system tables so the savings and ownership are visible.
5. Decommission or schedule-shut the old cluster once usage drops to zero, and confirm no scheduled jobs still reference it.

### Scenario 3 — "Nightly aggregation job is reimplemented by every team"

**Setup:** Five dashboards each recompute the same `daily_revenue` aggregation from a 4-billion-row orders table, each taking minutes and scanning the full table.

**How to reason through it:**
1. Recognize the shared computation and centralize it as one `MATERIALIZED VIEW prod.gold.daily_revenue` owned by the data platform team.
2. Point all five dashboards at the materialized view; schedule `REFRESH` after the upstream Silver load completes (via Workflows) so freshness is predictable.
3. Ensure the underlying orders table is clustered/Z-ordered on the common filter column (e.g., `order_date`) so the incremental refresh scans little data.
4. Measure before/after in Query History (duration, bytes read) to quantify the improvement and justify the pattern to other teams.
