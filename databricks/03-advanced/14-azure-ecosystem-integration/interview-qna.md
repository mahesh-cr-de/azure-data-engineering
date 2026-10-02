# Interview Q&A — Azure Ecosystem Integration

**Q1. How should Databricks authenticate to ADLS Gen2 in a new Unity Catalog-enabled workspace?**
> Use an Access Connector for Azure Databricks (a managed identity), grant it `Storage Blob Data Contributor` on the storage account, create a Storage Credential from it, and bind it to paths via External Locations. Users and groups then get `READ FILES` / `WRITE FILES` through Unity Catalog GRANTs. This keeps credentials out of notebooks and cluster configs, makes access auditable per user, and revoking access is a GRANT change rather than a credential rotation.

**Q2. What is wrong with using DBFS mounts to access ADLS?**
> Mounts are workspace-wide: anyone who can use a cluster with the mount typically gets the same storage access regardless of their individual entitlements, and they sit outside Unity Catalog governance and auditing. The credentials behind them are configured at mount time and are harder to rotate and attribute. They are a legacy pattern; External Locations replace them with identity-aware, centrally governed access.

**Q3. Key Vault-backed secret scope versus Databricks-backed scope?**
> A Key Vault-backed scope is a read-only reference to an Azure Key Vault: secrets are created and rotated in Key Vault under the organization's central security controls, and Databricks reads them at runtime. A Databricks-backed scope stores secrets inside Databricks. I prefer Key Vault-backed for production since rotation, access policies, and auditing stay in the central vault. In either case, I restrict scope permissions to the groups that need them, because notebook output redaction is not a security boundary.

**Q4. How do you pass parameters from ADF to a Databricks notebook and get a result back?**
> In the Notebook activity, set `baseParameters` (key/value pairs); the notebook reads them with `dbutils.widgets.get`. To return a value, the notebook ends with `dbutils.notebook.exit(<string>)`, and ADF reads it downstream as `@activity('<name>').output.runOutput`. For structured results I serialize JSON in the exit string and parse it with `json()` in ADF expressions.

**Q5. ADF or Databricks Workflows for orchestration?**
> It depends on the scope of the pipeline. ADF is stronger when the process spans many heterogeneous systems (on-prem via self-hosted integration runtime, SAP, REST, SQL) and needs business-friendly scheduling and monitoring. Workflows is stronger for Databricks-centric pipelines: native task dependencies, per-task retries and repair runs, and simpler cluster/job configuration. A common pattern is ADF as the outer scheduler and ingestion layer that triggers a Databricks job for the transformation DAG.

**Q6. How do you ingest from Event Hubs, and what governs your parallelism?**
> Either through the Kafka-compatible endpoint (Standard tier or above) using Spark's Kafka source with SASL_SSL and the connection string held in a secret scope, or via the native Event Hubs connector. Parallelism is bounded by the number of Event Hub partitions, since Spark reads roughly one task per partition, so partition count must be planned up front for expected throughput. I use a dedicated consumer group per application and a Structured Streaming checkpoint on durable storage so restarts resume exactly where they left off and Delta writes remain exactly-once.

**Q7. When would you use Event Hubs Capture plus Auto Loader instead of a streaming read?**
> When latency requirements are minutes rather than seconds and you want cheaper, simpler, replayable ingestion. Capture writes events as Avro files to ADLS automatically, and Auto Loader incrementally picks up new files with schema evolution support, often run on a triggered (available-now) schedule so compute only runs when needed instead of a 24x7 streaming cluster.
