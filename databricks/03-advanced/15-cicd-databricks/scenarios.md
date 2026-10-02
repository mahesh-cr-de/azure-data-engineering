# Scenarios — CI/CD for Databricks

### Scenario 1 — "Migrate 200 UI-created jobs into version control"

**Setup:** A team has 200 jobs created by hand in the production workspace. Nobody is sure what is deployed, and changes are made live.

**How to reason through it:**
1. Inventory first: export job definitions (via the CLI/API) and group them by owning team, criticality and shared libraries.
2. Do not migrate everything at once. Start with the most critical or most frequently broken jobs, converting each into a bundle resource and verifying the generated definition matches production behavior.
3. Move code into Git (Git folders → repositories), extract business logic from notebooks into tested modules as each job is migrated.
4. Freeze UI edits for migrated jobs by tightening permissions so the bundle is the only way to change them.
5. Track migration progress as a visible metric (jobs under CI/CD vs total) and retire the manual path once coverage is high.

### Scenario 2 — "A hotfix has to reach production within an hour"

**Setup:** A pipeline is producing wrong totals and the fix is a one-line change.

**How to reason through it:**
1. Use the same pipeline, but a fast lane: branch from the production tag, make the fix, run unit tests and a targeted integration test, get one reviewer's approval.
2. Deploy to staging for a short smoke test, then deploy to production through the normal approval gate. Skipping the pipeline is what causes the next incident.
3. Fix forward and tag the release; if the fix fails, redeploy the previous tag.
4. Afterwards, add a regression test for the bug and review why existing tests did not catch it.

### Scenario 3 — "Staging passes but production behaves differently"

**Setup:** A job succeeded in staging and failed in production on the first run.

**How to reason through it:**
1. Compare the bundle targets: differences in cluster configuration, runtime version, catalog/schema names, permissions or secret scopes are the usual cause, not the code (the artifact is identical).
2. Check data differences: production has volumes, skew, nulls or schema variations that staging data does not.
3. Check identity: the production `run_as` service principal may lack a grant that the staging principal has.
4. Fix by making staging more production-like (representative data subset, same runtime and policies) and encode the missing grant/config in Terraform or the bundle, never as a manual change.
