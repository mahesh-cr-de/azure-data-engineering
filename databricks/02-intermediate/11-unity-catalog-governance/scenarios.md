# Scenarios — Unity Catalog & Data Governance

### Scenario 1 — "A contractor's access needs to be revoked immediately after their engagement ends"

**Setup:** A contractor was granted access to several tables across multiple workspaces for a three-month project. Their contract has ended and the security team wants confirmation that all their access is fully revoked, today.

**How to reason through it:**
1. If access was granted via Unity Catalog GRANTs to the contractor's individual user account across catalogs/schemas/tables in different workspaces attached to the same metastore, revoking is centralized — removing their user (or disabling their account at the identity provider, Azure AD/Entra ID) immediately cuts off access everywhere that metastore governs, rather than needing to hunt through per-workspace cluster ACLs or mount-point credentials one workspace at a time.
2. If the organization followed the recommended practice of granting access to groups rather than individuals, the actual fix is even simpler: remove the contractor from the relevant Azure AD group(s), and Unity Catalog's group-membership-based access reflects that immediately without touching a single GRANT statement.
3. Use this as the moment to flag a process gap if one exists: if it turns out the contractor was granted access via individual per-table GRANTs (not group membership) because it was "faster" during onboarding, that's exactly the anti-pattern that makes offboarding slow and error-prone — recommend migrating to group-based grants going forward specifically so offboarding becomes a single membership change.
4. Close the loop with verification: Unity Catalog's audit logs (queryable system tables) can confirm no further access events occur post-revocation, giving the security team concrete evidence rather than just a verbal assurance that access was removed.

### Scenario 2 — "Finance and Marketing both want their own catalog, but need to share three specific reference tables"

**Setup:** Two business units want strong separation of their own data (different owners, different sensitivity levels) but both need read access to shared reference tables (e.g., a company-wide product dimension, a currency exchange rate table).

**How to reason through it:**
1. Propose a structure with three catalogs: `finance`, `marketing`, and a `shared` (or `reference`) catalog holding the common tables — rather than putting the shared tables inside either business unit's catalog, which would create an awkward cross-catalog ownership/dependency in one direction.
2. Grant each business unit `USAGE` on their own catalog plus `SELECT` on the `shared` catalog's relevant schema, so both `finance` and `marketing` teams can read from `shared.reference.product_dim` using consistent GRANT statements, ideally scoped to groups rather than individuals per the standard practice.
3. Address governance ownership explicitly: decide who owns and can write to the `shared` catalog (likely a central data platform team, not either business unit), since letting either Finance or Marketing write to a table the other depends on creates exactly the kind of uncoordinated-change risk lineage and catalog separation are meant to prevent.
4. Mention this pattern scales cleanly to more business units without re-architecting — adding a fourth `catalog` for a new business unit doesn't require touching the `finance`/`marketing`/`shared` structure at all, which is worth stating as a benefit of the catalog-level boundary over a flatter schema-naming-convention approach.

### Scenario 3 — "An auditor asks for proof of who accessed a specific sensitive table over the past quarter, including exactly what columns they queried"

**Setup:** A compliance audit requires demonstrating not just that access controls exist on a sensitive customer table, but a concrete accounting of who actually queried it, when, and (ideally) which columns.

**How to reason through it:**
1. Point to Unity Catalog's centralized audit logging as the source of truth — because every query against the table is mediated by Unity Catalog regardless of which workspace, cluster, or SQL warehouse it came from, the audit trail is complete and consistent rather than needing to be reconstructed from multiple disparate per-cluster logs.
2. If the table has column masks applied to some fields (e.g., PII), note that the audit trail combined with the masking configuration itself is part of the evidence — it demonstrates not just "here's who queried the table" but "here's proof that unauthorized groups only ever received masked values, never the raw sensitive column," which is often exactly what a compliance audit is trying to establish.
3. For the column-level specificity the auditor wants, mention that lineage and query history system tables can be queried programmatically to produce a structured report (user, timestamp, table, and — depending on what's captured — columns referenced) rather than manually reviewing logs, which is both faster and more defensible as a reproducible, query-driven audit artifact.
4. Use this as an opportunity to state the broader principle clearly: centralizing governance in Unity Catalog isn't only an access-control convenience, it's what makes compliance audits tractable at all once an organization has many workspaces and clusters — trying to assemble equivalent proof from workspace-siloed, cluster-level ACLs after the fact is far harder and much easier to get wrong.
