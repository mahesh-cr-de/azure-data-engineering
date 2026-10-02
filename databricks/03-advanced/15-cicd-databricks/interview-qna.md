# Interview Q&A — CI/CD for Databricks

**Q1. What is a Databricks Asset Bundle and why use it instead of exporting notebooks?**
> A bundle is a declarative, version-controlled definition of a project: jobs, pipelines, notebooks, libraries and permissions in `databricks.yml` and resource files. The CLI validates and deploys it to a chosen target (dev/staging/prod), with per-target overrides for cluster size, schedule, catalog and identity. Exporting notebooks only moves code, not the surrounding job, cluster, schedule and permission configuration, and it gives no repeatable, reviewable deployment path. Bundles make the whole workload reproducible.

**Q2. Terraform or Asset Bundles for deploying jobs?**
> Both, with clear ownership. Terraform manages shared platform resources that change slowly and need central control: workspaces, networking, Unity Catalog objects, cluster policies, groups. Bundles manage team-owned workloads that change often: jobs, pipelines, notebooks and packaged code, deployed in the developer workflow. The important rule is that each resource has exactly one owner tool, because managing the same job from both leads to drift and conflicting applies.

**Q3. How do you promote code from dev to production?**
> Build the artifact once in CI (for example a versioned Python wheel), deploy that exact artifact to staging, run smoke and data tests, then deploy to production behind a manual approval. Only configuration differs between environments (cluster sizes, catalogs, schedules, identities), defined as bundle targets. Rebuilding for each environment would mean production runs code that was never tested.

**Q4. How should CI authenticate to Databricks?**
> With a service principal, using OAuth machine-to-machine credentials, or better OIDC federation from GitHub or Azure DevOps to Entra ID so there is no long-lived secret. Separate service principals per environment with least privilege, and production jobs run as a service principal. Personal access tokens are avoided because they belong to a person, are long-lived and are hard to audit or rotate.

**Q5. How do you unit test PySpark code that normally runs on Databricks?**
> I keep transformation logic in plain Python modules that take and return DataFrames, so tests can run in CI with a local Spark session or through Databricks Connect against a remote cluster. Notebooks only call those functions. Small, explicit input DataFrames make tests fast and deterministic; integration tests then run the deployed job in a dev workspace on seeded data.

**Q6. What does `mode: development` do in a bundle?**
> It makes deployments safe for individual developers: resources are prefixed with the deploying user's name so multiple engineers can deploy the same bundle without colliding, and scheduled triggers are paused so experimental deployments do not start running on a timer. `mode: production` applies stricter validation and expects deliberate settings such as the identity jobs run as.

**Q7. How do you roll back a bad deployment?**
> Code rollback is redeploying the previous tagged version through the same pipeline, which is quick because every version is an immutable artifact. Data rollback is a separate decision: Delta time travel and `RESTORE` can revert a table, but I would assess downstream consumers first. Schema changes use expand-contract so a code rollback does not break the schema it expects.

**Q8. How do you stop people from changing production in the UI?**
> Restrict edit permissions in the production workspace so humans are read-only and only the deployment service principal can modify resources, then detect drift with scheduled `bundle validate` or `terraform plan` jobs and alert on differences. A documented break-glass process covers real emergencies, and any emergency change is back-ported to Git afterwards.
