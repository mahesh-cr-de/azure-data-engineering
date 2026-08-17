# Scenarios — Clusters, Compute & Databricks Runtime

### Scenario 1 — "A job that used to take 20 minutes now takes 2 hours, no code changes"

**Setup:** A nightly ETL job's runtime suddenly quadrupled. No one touched the notebook or the job config recently.

**How to reason through it out loud:**
1. First question: did the **input data volume** change? Always rule out the boring explanation first — check row counts/file sizes for the run vs. historical baseline before suspecting infrastructure.
2. Check if the **Databricks Runtime version** changed — either an explicit bump, or the job was configured to use a "current" channel that silently moved forward. A DBR upgrade can change AQE defaults, shuffle behavior, or library versions in ways that regress a specific query plan.
3. Check the **cluster itself** — was it resized, moved to a different node pool, or is it now landing on a smaller/cheaper default VM SKU because of a policy change? Also check for **autoscaling starvation**: if max workers was lowered or a shared pool is now contended by other jobs, the job may simply be running with less parallelism than before.
4. Pull up the Spark UI for the slow run and compare stage-level timings against a historical run — look specifically for spill-to-disk (memory pressure signal) and skewed task durations (data skew signal) that wouldn't show up just from "runtime quadrupled."
5. Land the answer on: isolate whether it's data-volume, runtime/config drift, or resource contention — and mention that pinning DBR to a specific LTS version (Topic Q2) is exactly the kind of control that prevents silent runtime-driven regressions like this.

### Scenario 2 — "Design compute for a mixed team: heavy nightly ETL + interactive data science"

**Setup:** One team runs large nightly Delta MERGE-based ETL; a separate small data science group does exploratory pandas/PySpark work during business hours, occasionally training models.

**Expected design:**
1. ETL: dedicated **job clusters** (ephemeral, sized for the workload, likely memory-optimized given MERGE/shuffle-heavy operations), triggered by a Workflow, with DBR pinned to an LTS version. No autoscaling complexity needed if volume is predictable — fixed-size sized to typical peak avoids autoscale/shuffle-loss overhead on a job that's already tightly coupled.
2. Data science: a **shared, autoscaling all-purpose cluster** on the ML runtime variant (pre-installed frameworks + MLflow), with a short auto-termination window (e.g. 45 min) since usage is bursty and concentrated in business hours — combined with a cluster pool if startup latency during the day is a complaint.
3. Governance: apply a **cluster policy** to both groups so nobody can accidentally spin up an oversized, non-auto-terminating cluster — cap max workers and VM SKU choices per policy, tag-enforce for cost allocation between the two teams.
4. If model training needs GPUs occasionally, call out that this should be a *separate*, explicitly-requested GPU cluster (NC/ND-series) rather than a default on the shared interactive cluster — GPU nodes are expensive and shouldn't be the default for everyone's exploratory notebook work.

### Scenario 3 — "Autoscaling isn't actually saving money"

**Setup:** A team enabled autoscaling on their all-purpose cluster expecting cost savings, but the monthly bill barely moved.

**Diagnosis path:**
1. Ask: what's the **min worker count** set to? A common mistake is setting min=max-ish (e.g., min 8, max 10) which barely allows any scale-down — effectively paying for a near-fixed-size cluster while adding autoscaling overhead for nothing.
2. Ask whether **auto-termination** is even enabled — autoscaling only adjusts worker count while the cluster is running; a cluster left running idle overnight or on weekends (0 active queries but still "up") burns the same driver-node cost regardless of how low workers scaled.
3. Check for a **single long-running, tightly-coupled job** dominating the cluster's time — as discussed in concepts, autoscaling helps most when there are natural stage boundaries; a workload that's one continuous heavy shuffle won't scale down mid-execution no matter how idle-friendly the config is.
4. Recommend: lower the min worker floor meaningfully, verify/shorten auto-termination, and separate genuinely bursty interactive usage onto its own pooled+autoscaled cluster distinct from any steady-state scheduled workloads (which are usually cheaper as right-sized job clusters anyway).
