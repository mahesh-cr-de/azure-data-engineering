# Scenarios — Medallion Architecture

### Scenario 1 — "Dashboards show different revenue numbers for different teams"

**Setup:** Finance and Marketing each built their own Gold revenue table from the same Silver orders, with slightly different rules (refunds, currency conversion). Leadership sees two numbers.

**How to reason through it:**
1. Identify the divergence by comparing the two transformations and lineage in Unity Catalog; list each rule difference (refund treatment, FX rate date, time zone).
2. Agree a **single business definition** with the metric owner (usually Finance) and implement it once in a governed shared Gold table or materialized view.
3. Repoint both dashboards to that definition; deprecate the duplicates with a notice period using lineage to find every consumer.
4. Prevent recurrence: named owner per metric, a review step for Gold changes, and documentation in the catalog.

### Scenario 2 — "An upstream team renamed a column and Silver broke at 3 AM"

**Setup:** A source system changed `cust_id` to `customer_id`. The Bronze ingest kept running, but the Silver job failed on a missing column.

**How to reason through it:**
1. Confirm Bronze behaved correctly: schema-tolerant ingest (rescue mode) kept the data, so nothing was lost and the failure is isolated to Silver.
2. Fix Silver with a mapping that handles both names during the transition, backfill the failed window from Bronze, and re-run idempotently.
3. Prevent the 3 AM surprise: a **data contract** with the producing team (change notification and versioning), schema drift alerts at Bronze, and a CI contract test.
4. Make the failure mode graceful: schema drift routes to quarantine or alerts instead of failing the entire downstream chain, depending on rule severity.

### Scenario 3 — "Storage and compute costs for Bronze keep growing"

**Setup:** Bronze keeps three years of raw events, queries scan too much data, and `VACUUM` has never been tuned.

**How to reason through it:**
1. Decide the real replay requirement with stakeholders; for example, 90 days hot in Delta and older history archived to cheaper storage tiers.
2. Partition or cluster Bronze by ingest date so incremental jobs read only recent data, and compact small files with `OPTIMIZE`.
3. Set a `VACUUM` and Delta log retention policy aligned with the time-travel needs rather than the default by accident.
4. Make downstream jobs incremental (read only new Bronze data) so cost scales with new data, not total history.
5. Measure storage and DBU spend per layer before and after to confirm the savings.
