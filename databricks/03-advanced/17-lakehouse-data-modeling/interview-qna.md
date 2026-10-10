# Interview Q&A — Lakehouse Data Modeling

**Q1. Why do dimensional modeling on a lakehouse at all? Why not just query wide tables?**
> Wide tables are fine for a single, stable use case, but at enterprise scale they duplicate attributes, make it hard to keep one definition per metric, and complicate history handling. A star schema separates events (facts) from descriptive context (dimensions), gives shared conformed dimensions across domains, and maps naturally to how BI tools and business users ask questions. I use it as the governed Gold core and derive wide tables or materialized views from it where a dashboard needs speed.

**Q2. How do you decide the grain of a fact table?**
> I ask what one row represents in business terms, such as "one order line" or "one account per day", and fix that before choosing any columns. Everything in the fact must be true at that grain, and every dimension key must be single-valued at that grain. Mixing grains in one table is the most common modeling mistake and produces double-counted measures.

**Q3. Explain SCD Type 1, 2 and 3 and when you would pick each.**
> Type 1 overwrites the value, so no history; I use it for corrections or attributes nobody reports historically. Type 2 inserts a new row per change with validity dates, preserving full history; I use it when reports must show the attribute as it was at the event time, such as the customer's region when the sale happened. Type 3 keeps only a previous-value column, for the rare case where just the last change matters. Many dimensions mix them per attribute.

**Q4. How do you implement SCD2 in Delta?**
> Either a MERGE with the "union trick" or Delta Live Tables `APPLY CHANGES`. In the MERGE approach I compute a hash of the tracked attributes, then build a source that contains each changed record twice: once with the real key to close the current row, and once with a NULL merge key so it cannot match and is inserted as the new version. DLT's `apply_changes` with `stored_as_scd_type=2` does this declaratively and also handles out-of-order records using a sequence column.

**Q5. How do you join facts to an SCD2 dimension efficiently?**
> I resolve the surrogate key at fact load time, using a point-in-time lookup against `valid_from`/`valid_to`, and store the dimension's surrogate key in the fact. Reporting queries then use a simple equality join on an integer key. Doing the range join in every report is slower and easy to get wrong.

**Q6. Are primary and foreign keys enforced in Delta?**
> `NOT NULL` and `CHECK` constraints are enforced, but `PRIMARY KEY` and `FOREIGN KEY` constraints in Unity Catalog are informational. They document relationships for BI tools and the optimizer but do not reject violating rows. So uniqueness and referential integrity must be enforced by the load logic and verified by data quality tests.

**Q7. What are the trade-offs of identity columns for surrogate keys?**
> Identity columns are convenient and guarantee uniqueness, but values are not contiguous and identity columns can restrict concurrent writes to the same table. If I need parallel loads or consistent keys across environments, I use deterministic hash-based keys from the business key instead. I decide per table based on concurrency and whether keys must be reproducible.

**Q8. What do you do when a fact arrives before its dimension record?**
> I insert an inferred member into the dimension with the real business key and default attributes such as "Unknown", so the fact load succeeds with a valid foreign key. When the real dimension record arrives, I update the inferred row (a Type 1 overwrite for that placeholder) so reports are corrected. Without this pattern, facts either fail or get attached to a generic unknown key permanently.
