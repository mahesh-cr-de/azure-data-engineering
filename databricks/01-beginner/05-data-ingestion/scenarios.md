# Scenarios — Data Ingestion Basics

### Scenario 1 — "Ingestion job is falling behind as file volume grows"

**Setup:** A `COPY INTO`-based hourly batch job ingesting vendor files has worked fine for a year, but as the vendor's file volume tripled, the job started missing its hourly SLA and sometimes overlaps with the next scheduled run.

**How to reason through it:**
1. First diagnose whether the slowdown is from **file count growth** (more small files = more per-file overhead) or **data volume growth** (same file count, bigger files) — these call for different fixes.
2. If it's file-count driven, this is a strong signal to **migrate from `COPY INTO` to Auto Loader**, specifically with file notification mode rather than directory listing — `COPY INTO`'s per-run file-tracking overhead and directory-scan cost both grow less gracefully at high file counts than Auto Loader's event-driven discovery.
3. Consider whether the ingestion cadence itself should change — moving from hourly batch to a continuously-running (or more frequent `availableNow` triggered) Auto Loader stream smooths out load instead of concentrating it into an hourly spike that's now too large for its window.
4. Flag the overlapping-runs risk explicitly: if the old job can genuinely still be running when the next scheduled run fires, that's a correctness risk (concurrent writes to the same bronze table, potential duplicate processing) independent of the SLA issue — worth fixing job concurrency settings (e.g., "skip if already running") regardless of which ingestion tool is used going forward.

### Scenario 2 — "A vendor changed their file schema without warning and broke the pipeline"

**Setup:** An upstream partner added a new required field and renamed an existing column; the nightly ingestion job either failed outright or (worse) silently ingested nulls where the renamed column used to have data.

**How to walk through the response:**
1. Immediate triage: determine whether the ingestion layer has schema enforcement (fails loudly) or schema evolution/inference (may have silently "handled" it in a way that's actually wrong) — the "silently ingested nulls" symptom suggests the pipeline treated a renamed column as a *dropped* old column plus a *new* unrelated column, which schema evolution alone won't catch as a "problem," since technically nothing failed.
2. Recommend adding an explicit **schema contract check** at ingestion — before or alongside Auto Loader's own schema evolution, validate incoming files against an expected schema definition and route mismatches to a quarantine location with an alert, rather than relying purely on "evolution" to silently absorb any change.
3. Distinguish for the interviewer: schema evolution is a *convenience* feature for legitimately new, additive columns; it is not a substitute for a *data contract* with upstream partners — a renamed/dropped column is a breaking change that should ideally trigger a loud failure and human review, not a silent auto-adapt.
4. Long-term fix: formalize an SLA/contract with the vendor (versioned schema, deprecation notice period) and add automated schema-diff alerting comparing each incoming batch's schema against the last known-good schema.

### Scenario 3 — "Design ingestion for three very different sources: a nightly SFTP drop, a partner's real-time event stream, and ad hoc analyst-uploaded CSVs"

**Setup:** You need one coherent ingestion strategy for three different source patterns feeding the same lakehouse.

**Expected design:**
1. **Nightly SFTP drop (bounded, predictable, low frequency):** land into a Volume via a scheduled process, then `COPY INTO` on a matching nightly cadence — this is exactly `COPY INTO`'s sweet spot, no need for streaming infrastructure overhead here.
2. **Partner real-time event stream (high frequency, continuous):** Auto Loader with file notification mode (if events land as files via an intermediate storage hop) or a native streaming source, writing continuously with a short/no trigger interval into a bronze table — near-real-time latency requirement justifies the always-on streaming approach.
3. **Ad hoc analyst-uploaded CSVs (irregular, low volume, human-driven):** land into a dedicated "uploads" Volume with tighter access control (since it's less automated/more error-prone than the other two sources), and either a manually-triggered `COPY INTO` or a lightweight scheduled Auto Loader in `availableNow` mode — explicitly call out that this path needs more defensive validation (schema contract checks, basic sanity checks on row counts) since humans uploading files are the most likely source of malformed/unexpected data among the three.
4. Tie it together: all three ultimately land in governed Volumes and feed bronze Delta tables, giving one consistent lineage/governance model even though the ingestion mechanics differ per source — worth stating explicitly, since "one strategy, three tools, not three different governance models" is the kind of synthesis interviewers are listening for at a senior/lead level.
