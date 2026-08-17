# Scenarios — Databricks Architecture & Workspace Fundamentals

### Scenario 1 — "Our security team is blocking the Databricks rollout"

**Setup:** Your InfoSec team is refusing to approve Azure Databricks adoption because they assume "Databricks is a SaaS vendor, so our data goes into someone else's cloud."

**How to respond in an interview:**
1. Explain the control plane / data plane split explicitly: the *processing* (cluster VMs) and the *data* (ADLS Gen2) live inside the customer's own Azure subscription and VNet — Databricks' company-owned infrastructure only holds control-plane metadata (notebook source, job definitions, query text, cluster configs), not the underlying data itself, for classic (non-serverless) compute.
2. Offer VNet injection (bring-your-own-VNet) so the managed resource group deploys into a VNet the customer already controls, with their own NSGs, UDRs, and private endpoints to ADLS.
3. Flag the one carve-out honestly: **serverless** compute (SQL warehouses, serverless jobs) *does* run in Databricks-managed infrastructure — so if the security requirement is "zero exceptions, ever," serverless SKUs are off the table and you'd standardize on classic clusters with VNet injection + Private Link.

### Scenario 2 — "Our all-purpose cluster costs are out of control"

**Setup:** A finance review shows Databricks costs 3x'd last quarter. You're asked to diagnose.

**How to think through it out loud:**
1. First question: are production pipelines running on **all-purpose** clusters instead of **job clusters**? This is the #1 cause — teams prototype on an interactive cluster, then just point the job scheduler at that same always-on cluster instead of switching to ephemeral job clusters.
2. Check auto-termination settings — clusters left with no idle timeout (or a very long one) burn DBUs overnight/weekends with nobody attached.
3. Check for cluster sprawl — many small clusters instead of pooled/shared clusters for interactive work (each cluster pays its own startup + minimum runtime cost).
4. Check whether Photon is enabled where it should be — for SQL/DataFrame-heavy jobs, Photon often reduces wall-clock time enough that the *net* cost is lower despite a higher per-DBU rate, because the job finishes faster.
5. Longer-term fix: move ad hoc BI-style querying to serverless SQL warehouses (scale-to-zero) instead of keeping all-purpose clusters warm for occasional queries.

### Scenario 3 — "Choose the right compute type for three different workloads"

**Setup:** You're designing compute strategy for: (a) a nightly ETL pipeline, (b) 20 analysts running ad hoc SQL against gold tables, (c) 5 data scientists doing exploratory notebook work during business hours.

**Expected answer:**
- (a) **Job cluster**, sized appropriately, triggered by a Databricks Workflow — ephemeral, no idle cost, and isolated per run so one job's resource contention never affects another.
- (b) **Serverless SQL Warehouse** with scale-to-zero and auto-scaling — bursty, unpredictable usage pattern is exactly what serverless is priced for, and analysts get sub-second warehouse start times.
- (c) A **Shared-mode all-purpose cluster** (or a small cluster pool) with autoscaling and a short auto-termination window (e.g. 30–60 min) — collaborative interactive work benefits from a shared cluster, but you cap idle burn with aggressive auto-termination.

### Scenario 4 — "Explain to a skeptical DBA why this isn't 'just another data warehouse'"

**Setup:** A traditional SQL Server DBA on your team keeps asking "why not just use Synapse dedicated pools, this seems like the same thing."

**Talking points to hit:**
- Lakehouse architecture: one copy of data in open-format Delta tables in ADLS Gen2, queried by SQL, Python, Scala, R, and ML workloads alike — no separate ETL-into-warehouse step and no data duplication between "the lake" and "the warehouse."
- Storage/compute are fully decoupled and independently scaled — a warehouse's compute doesn't dictate how the data is stored, unlike a dedicated pool's tightly coupled model.
- Openness: Delta Lake is an open table format (Parquet + transaction log), so data isn't locked into a proprietary engine — other engines (Presto, Trino, Synapse Serverless) can also read it.
