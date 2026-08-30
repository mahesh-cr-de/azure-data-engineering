# Scenarios — Structured Streaming & Auto Loader

### Scenario 1 — "A streaming job's checkpoint directory was accidentally deleted"

**Setup:** During a cleanup script, someone accidentally deleted the checkpoint directory for a long-running production streaming job. The job needs to be restarted, but the team is worried about data loss or duplication.

**How to reason through it:**
1. Explain the actual consequence first: without the checkpoint, Spark has no record of which offsets were already processed, so on restart it has no choice but to start from whatever default the source defines (for a file-based Auto Loader source, that typically means treating every file currently in the path as "new" again).
2. Assess the blast radius based on the sink: if the sink is Delta and the pipeline uses `MERGE` with a natural key (idempotent upsert) rather than plain append, reprocessing already-seen files will just re-upsert the same rows with no duplication — the correctness impact may be limited even though the checkpoint is gone. If the sink uses plain append writes, reprocessing will create true duplicates that need identifying and removing after the fact.
3. If some files must be explicitly skipped (e.g., a huge historical backlog that was already processed and shouldn't be re-ingested), Auto Loader supports explicitly setting a starting point (e.g., `cloudFiles.includeExistingFiles` set appropriately, or seeding a new checkpoint) rather than defaulting to full reprocessing.
4. Close with the process fix: this is exactly the kind of incident that argues for treating checkpoint directories as protected, versioned/access-controlled infrastructure — not a folder a cleanup script should ever be able to touch — and for designing sinks to be idempotent (MERGE-based) wherever duplication from a checkpoint loss would be costly.

### Scenario 2 — "Late-arriving mobile events are being silently dropped from an hourly rollup"

**Setup:** A streaming aggregation computes hourly event counts using a 5-minute watermark. The team notices numbers are consistently a bit lower than a batch reconciliation job computes the next day, and traces it to mobile clients that sync data after being offline for 20–30 minutes.

**How to reason through it:**
1. Name the mechanism directly: a 5-minute watermark means any window is finalized (and its state dropped) 5 minutes after the window's end passes in event time — events arriving later than that, even if their event_time is legitimately within an already-closed window, are dropped rather than incorporated.
2. Confirm this is actually watermark-driven and not a different bug: check whether the discrepancy correlates with known offline/reconnect patterns (a 20–30 minute gap matching a specific client behavior is a strong signal) rather than being a uniform undercount, which would point elsewhere.
3. Propose the trade-off explicitly rather than just widening the watermark blindly: increasing the watermark to, say, 45 minutes to accommodate this lateness pattern means all window state for that aggregation is held roughly 45 minutes longer, increasing streaming state size and the latency before a window's numbers are considered "final" for downstream consumers who might be expecting near-real-time output.
4. If the business genuinely needs both fast preliminary numbers *and* eventual correctness, propose a two-tier design: keep the streaming aggregation's tighter watermark for near-real-time dashboards explicitly labeled as "preliminary," and rely on the existing daily batch reconciliation job as the source of truth for finalized numbers — rather than trying to make one streaming watermark serve both needs perfectly.

### Scenario 3 — "Design an ingestion pipeline for a landing zone receiving millions of small JSON files per day, with an evolving schema"

**Setup:** An interviewer describes IoT-style ingestion: millions of small JSON files landing in ADLS Gen2 daily, upstream device firmware occasionally adds new fields, and the team wants low-latency, reliable ingestion into a Bronze Delta table.

**How to reason through it:**
1. Start with file discovery: at millions of files per day, plain directory listing will become a bottleneck fast — recommend Auto Loader in file notification mode from the start, accepting the one-time setup cost of the cloud event infrastructure in exchange for discovery cost that doesn't scale with total file count in the landing zone.
2. Address schema evolution deliberately: since firmware occasionally adds fields, recommend `cloudFiles.schemaEvolutionMode` set to either `addNewColumns` (if the team is comfortable with new fields flowing through automatically and Bronze is meant to be a permissive raw layer) or `rescue`-based handling if new/unexpected fields should be visible but not silently merged into the primary schema — and note this decision should differ from what you'd choose for a Silver/Gold table, where schema stability usually matters more.
3. Address small-file fallout downstream: even with efficient ingestion, millions of small JSON files becoming many small Bronze Delta files is a real risk — recommend scheduled `OPTIMIZE` on the Bronze table as a standard maintenance job (Topic 08), and consider whether `trigger(availableNow=True)` on a scheduled job cluster is more cost-effective than an always-on stream if near-real-time latency isn't actually required for this particular use case.
4. Mention idempotency: given file-based ingestion at this volume, some files landing twice (retries, duplicate uploads from edge devices) is realistic — writing Bronze via `MERGE` on a natural/dedup key, or at minimum deduplicating on a unique event id with `dropDuplicatesWithinWatermark`, avoids silent double-counting downstream.
