# Scenarios — Azure Ecosystem Integration

### Scenario 1 — "A notebook has a storage account key hardcoded and it was committed to Git"

**Setup:** A security scan finds an ADLS account key in a notebook in a Databricks Repo.

**How to reason through it:**
1. Treat the key as compromised: rotate it immediately in the storage account and invalidate any SAS tokens derived from it, before cleaning up the code.
2. Remove it from the notebook and from Git history (history rewrite or secret-scanning remediation), and check access logs for unexpected use during the exposure window.
3. Replace the pattern: grant an Access Connector managed identity access to the storage account, create a Storage Credential and External Location in Unity Catalog, and read data via `abfss://` paths governed by UC grants — no key anywhere.
4. For any remaining secrets (APIs, JDBC passwords), use a Key Vault-backed secret scope and `dbutils.secrets.get`.
5. Add prevention: pre-commit/secret scanning in CI and disable account-key access on the storage account (`allowSharedKeyAccess = false`) once nothing depends on it.

### Scenario 2 — "ADF triggers a Databricks notebook nightly; it fails intermittently with cluster start errors"

**Setup:** The Notebook activity uses a new job cluster each run and occasionally fails before the notebook starts.

**How to reason through it:**
1. Read the failure detail: errors during cluster creation usually indicate capacity (VM SKU/quota in the region), subnet IP exhaustion with VNet injection, or an overly strict policy — not notebook logic.
2. Mitigations: use an **instance pool** with idle pre-warmed instances to cut start time and avoid repeated capacity requests; allow alternative node types; confirm subscription vCPU quota and subnet size.
3. Add retry on the ADF activity (e.g., 2 retries with a delay) for transient provisioning failures, while making the notebook idempotent so a retry never duplicates data (MERGE or overwrite by partition).
4. If the nightly job is Databricks-only, consider moving the DAG into Workflows and triggering it from ADF through a single job-run call, gaining task-level repair and retries.

### Scenario 3 — "Real-time order stream from Event Hubs is falling behind"

**Setup:** A Structured Streaming job reading Event Hubs via the Kafka endpoint shows growing input lag during peak hours.

**How to reason through it:**
1. Check partition count: parallelism is capped by it. If there are 4 partitions, adding cluster cores beyond 4 concurrent read tasks will not increase ingestion throughput.
2. Check micro-batch metrics (input rate vs processing rate, batch duration). If processing rate is lower than input rate, the bottleneck is in the transformation or sink — inspect the Spark UI for skew, expensive joins, or small-file writes to Delta.
3. Use `maxOffsetsPerTrigger` to bound batch size and smooth load; tune the trigger interval to avoid tiny, frequent batches that produce small Delta files.
4. If throughput is truly partition-limited, plan an Event Hub with more partitions (and migrate producers/consumers), as partition count generally cannot be raised in place on all tiers.
5. Confirm the checkpoint location is on durable ADLS storage so restarts after scaling changes resume cleanly without reprocessing.
