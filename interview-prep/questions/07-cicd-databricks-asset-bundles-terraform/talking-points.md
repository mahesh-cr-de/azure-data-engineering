# Talking points — condensed for verbal delivery

**Opening line:**

> "Production should only ever be changed by a pipeline running as a service principal. No human edits in the prod UI."

## Mnemonic: Split → Test → Promote → Protect

### 1. Split
- Terraform for platform: workspaces, Unity Catalog, external locations, cluster policies
- Databricks Asset Bundles for workloads: jobs, pipelines, notebooks, per-environment targets
- Each resource has exactly one owner tool

### 2. Test
- Business logic in Python modules, notebooks only orchestrate
- PR: lint, mypy, pytest unit tests, `bundle validate`
- Dev: deploy + integration test on small seeded data

### 3. Promote
- Build the wheel once; the same artifact goes dev → staging → prod
- Manual approval before prod; separate workspace and catalog per environment

### 4. Protect
- Service principals via OAuth/OIDC, never personal tokens; prod jobs `run_as` a service principal
- Expand-contract schema changes; rollback by redeploying the previous tag
- Read-only prod UI and scheduled drift checks

**Closing line:**

> "The goal is that deploying to production is boring: the same steps, the same artifact, every time."

## Delivery tip
If asked "DABs or Terraform?", answer "both, with clear boundaries": Terraform for shared platform, bundles for team-owned workloads.

## Likely follow-ups to prep for
- How do you test PySpark code without a cluster?
- How do you handle a hotfix that must reach prod in an hour?
- How do you version and deploy shared libraries used by many jobs?
- How would you migrate 200 existing UI-created jobs into bundles?
