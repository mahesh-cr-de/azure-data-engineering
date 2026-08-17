# Interview Q&A — Databricks Architecture & Workspace Fundamentals

**Q1. Explain the Control Plane vs Data Plane in Azure Databricks. Why does it matter for a customer?**
> The control plane (UI, job scheduler, notebook source, cluster manager, REST API) lives in Databricks' managed Azure subscription. The data plane — the cluster VMs and the actual customer data in ADLS Gen2 — lives inside the customer's own Azure subscription and VNet. This matters because it means customer data never physically leaves their tenant/subscription for standard (non-serverless) compute, which is central to compliance and data-residency arguments, and it also explains why customers see cluster VM costs directly in their own Azure billing separate from the Databricks DBU charge.

**Q2. What's the difference between an All-Purpose cluster and a Job cluster?**
> All-purpose clusters are long-lived, multi-user, interactive clusters typically used from notebooks; they're billed at a higher DBU rate and keep running (and costing money) until manually terminated or an auto-termination timeout hits. Job clusters are created automatically when a scheduled job starts and are torn down immediately after the job completes — they're cheaper per DBU and are the right choice for production pipelines since you never pay for idle time.

**Q3. What is DBFS and why is it being deprecated in favor of Unity Catalog Volumes?**
> DBFS is a distributed filesystem abstraction Databricks layers over cloud storage (backed by a storage account in the managed resource group), mounted at `/dbfs`. It predates Unity Catalog and has no fine-grained governance — anyone with cluster access could historically read/write DBFS root. Unity Catalog Volumes provide the same "work with files, not just tables" capability but with proper catalog/schema-level access control, audit logging, and lineage, which is why Databricks now recommends Volumes over DBFS root for new workloads.

**Q4. What is Photon and does it require code changes?**
> Photon is Databricks' native, vectorized C++ execution engine that replaces the JVM-based Spark execution engine for supported SQL/DataFrame operators. It requires no code changes — you enable it at the cluster/warehouse level and Spark transparently uses Photon-accelerated operators where possible, falling back to standard Spark execution for unsupported operations (e.g., certain UDFs, RDD APIs).

**Q5. What's the difference between "Single User" and "Shared" cluster access modes, and why would you pick one over the other?**
> Single User mode dedicates the cluster to one identity (user or service principal) and supports the full language/API surface including RDDs. Shared mode allows multiple users to attach to the same cluster simultaneously with per-user credential passthrough and enforced Unity Catalog permissions, but restricts some lower-level APIs for isolation reasons. You'd pick Shared for cost-efficient interactive development across a team with proper governance, and Single User for jobs/service principals or workloads needing unsupported APIs.

**Q6. A workspace is created — where does the compute actually run, physically?**
> Inside a Databricks-managed resource group that Azure creates within the *customer's* subscription (naming pattern like `databricks-rg-<workspace-name>-<random-suffix>`). This resource group contains the VNet, subnets, NSGs, the cluster VMs, and (for the legacy setup) a storage account backing DBFS root. Customers generally shouldn't manually modify resources inside this managed RG.

**Q7. What is a DBU and how does Databricks pricing actually work?**
> A DBU (Databricks Unit) is a unit of processing capability billed per second of usage, on top of the underlying Azure infrastructure cost (VMs, storage, networking) which is billed separately by Azure. Total cost = Azure VM/infra cost + DBU cost, and the DBU rate itself varies by workload type (all-purpose vs. jobs vs. SQL vs. serverless) and tier (Standard/Premium).

**Q8. When would you use Serverless compute instead of provisioning your own cluster?**
> When you want to eliminate cluster startup latency and cluster-sizing decisions entirely — Databricks manages a warm pool of infrastructure in its own environment and bills per-second of actual query/job execution. Trade-off: serverless compute runs in Databricks-managed infrastructure rather than your VNet, so if you have strict network-isolation requirements (e.g., data must never leave a customer-managed VNet) you'd stick with classic clusters.
