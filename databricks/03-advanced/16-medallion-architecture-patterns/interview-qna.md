# Interview Q&A — Medallion Architecture

**Q1. Explain the medallion architecture and why it is useful, beyond "three layers".**
> It organizes data into layers of increasing quality, each with a clear contract and owner. Bronze is a faithful, replayable copy of the source, Silver is validated and conformed entities, Gold is business-ready data products. The usefulness is operational: if a transformation has a bug, I rebuild Silver and Gold from the immutable Bronze; quality problems are caught at a defined gate; and consumers know exactly what level of trust and structure each layer provides.

**Q2. What belongs in Bronze, and what must never be there?**
> Raw data exactly as received plus ingestion metadata (timestamp, source file, batch id), stored append-only and tolerant of schema changes. Business logic, deduplication and filtering do not belong there, because they destroy the ability to replay and audit what the source actually sent.

**Q3. How do you handle bad records between Bronze and Silver?**
> I validate against explicit rules (nulls on keys, types, ranges, referential checks) and route failing rows to a quarantine table that records the rule, the batch and the reason, rather than dropping them silently or failing the whole pipeline. Rule severity decides the behavior: warn and keep, drop to quarantine, or fail the run for critical violations. Quarantine volumes are monitored, since a spike is itself a signal that an upstream change happened.

**Q4. How do you implement upserts and history in Silver?**
> For current-state entities I deduplicate to the latest record per business key and apply a Delta `MERGE`, guarding on a timestamp or version so late, older records do not overwrite newer ones. When history matters I implement SCD Type 2 with validity columns, or use Delta Live Tables `APPLY CHANGES INTO`, which handles ordering and SCD1/SCD2 for change feeds declaratively.

**Q5. Would you ever skip a layer or add one?**
> Yes, if it earns its place. Small, trusted, low-volume sources can feed Silver-like tables with minimal transformation, and some very simple use cases do not need a separate Gold. I would add a layer only when there is a distinct contract, owner and consumer for it. Extra layers add latency, storage and operational burden, so "Platinum" tables without a clear purpose are an anti-pattern.

**Q6. Streaming or batch between layers?**
> It depends on the freshness requirement and cost. Delta supports streaming, triggered incremental (`availableNow`) and batch against the same tables. I start from the business SLA: if minute-level freshness is enough, scheduled incremental runs are far cheaper than a 24x7 stream. I use continuous streaming only where latency is genuinely critical.

**Q7. How do you stop Gold from becoming a mess of duplicated metrics?**
> By treating Gold as governed data products: named owners, documented definitions, one canonical version of each metric, freshness SLAs and review of changes. Shared metrics live in a shared Gold schema or materialized views that teams reference rather than copy, and Unity Catalog lineage shows who depends on what before anything changes.

**Q8. How do you reprocess after discovering a logic bug in Silver?**
> Because Bronze is immutable and complete, I fix the logic, then rebuild the affected Silver tables from Bronze (full or by date range), and let Gold refresh from the corrected Silver. I do it in a way that is idempotent, use a backfill parameter or a separate table with a swap, and communicate the correction window to consumers. Delta time travel provides a safety net if the rebuild itself goes wrong.
