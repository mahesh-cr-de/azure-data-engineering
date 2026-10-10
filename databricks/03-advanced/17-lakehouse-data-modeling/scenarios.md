# Scenarios — Lakehouse Data Modeling

### Scenario 1 — "Sales by region doesn't match last quarter's report after a territory change"

**Setup:** Sales territories were reorganized in July. Re-running the Q2 report today shows different regional totals than the version published in June.

**How to reason through it:**
1. Identify the cause: the customer or sales-rep dimension is Type 1, so the reorg overwrote the region and historical facts now roll up under the new region.
2. Decide with the business which question matters: "sales by the region as it was then" (Type 2) or "sales by today's region" (current view). Often both are needed.
3. Convert the relevant attribute to SCD Type 2 (or Type 6: Type 2 rows plus a `current_region` column) and resolve the version key at fact load time.
4. Backfill history where source data allows, and document the cutover date from which history is trustworthy.
5. Add a regression test that reruns a closed period and expects stable totals.

### Scenario 2 — "A dashboard double-counts revenue after a new join was added"

**Setup:** Revenue doubled after an analyst joined the sales fact to a customer-accounts table.

**How to reason through it:**
1. Check grain: joining a fact at one row per order line to a table with multiple rows per customer (many-to-many) multiplies fact rows.
2. Fix the model, not the query: introduce a bridge table with allocation weights if the many-to-many is real, or restrict the join to the primary account via a flag.
3. Add a grain test in the pipeline (row count and sum of net amount before/after joins) so fan-out is caught automatically.
4. Document the grain of each Gold table in the catalog so consumers know what is safe to join.

### Scenario 3 — "The customer dimension has 400 million versions and queries are slow"

**Setup:** A fast-changing attribute (last login timestamp) is tracked as Type 2, creating a new row on every change.

**How to reason through it:**
1. Question whether the attribute needs history at all. Volatile attributes like "last login" should be Type 1, or moved to a fact/snapshot table.
2. Split the dimension: keep slowly changing attributes in the Type 2 dimension, and move rapidly changing ones to a mini-dimension (banded values such as activity tier) or a separate Type 4 history table.
3. Rebuild with `hash_diff` computed only over truly tracked attributes so non-meaningful changes do not create versions.
4. Apply clustering on the business key and `is_current`, and compact with `OPTIMIZE`; measure query time before and after.
