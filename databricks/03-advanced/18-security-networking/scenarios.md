# Scenarios — Security & Networking

### Scenario 1 — "Security wants Databricks fully private within a month"

**Setup:** A regulated company has an existing workspace in the default managed network with public access. Security requires no public exposure for data or users.

**How to reason through it:**
1. Recognize the constraint: moving to VNet injection and some network settings may require a **new workspace**, so plan a migration rather than an in-place toggle. Inventory jobs, clusters, libraries, secrets and Unity Catalog objects.
2. Design the target: VNet-injected workspace with appropriately sized subnets, No Public IP, front-end and back-end Private Link, private endpoints to ADLS/Key Vault/Event Hubs, firewall egress allowlist, public network access disabled.
3. Because data is governed by Unity Catalog (same metastore across workspaces), data and permissions carry over; workload definitions move using bundles and Terraform, which is exactly what infrastructure-as-code buys here.
4. Validate DNS and connectivity from user networks and CI before cutover; migrate team by team with a rollback path.
5. Close the loop with audit evidence for the compliance team.

### Scenario 2 — "A departing engineer still has access to production data"

**Setup:** An engineer left; a review finds they still had direct storage permissions and personal grants.

**How to reason through it:**
1. Immediate: disable the Entra ID account (cuts SSO and token use), revoke personal access tokens, and review recent audit logs for their activity.
2. Identify why access outlived employment: individual grants and direct storage ACLs bypassed group-based governance.
3. Remediate structurally: move all grants to Entra groups, remove direct storage access in favor of the managed identity + external location model, enforce token expiry limits, and automate leaver processes via SCIM.
4. Add a recurring access review report from system tables and group membership.

### Scenario 3 — "Clusters fail to start with IP exhaustion errors"

**Setup:** After onboarding more teams, clusters intermittently fail to launch in a VNet-injected workspace.

**How to reason through it:**
1. Confirm the cause from the error and subnet metrics: the delegated subnets have run out of free IP addresses (each node consumes addresses in the subnets).
2. Short-term: terminate idle clusters, shorten auto-termination, use pools wisely, and limit max workers via cluster policies.
3. Long-term: subnet CIDR ranges generally cannot simply be expanded in place for a workspace, so plan a migration to larger ranges or a new workspace, and size future subnets using peak concurrent nodes plus headroom.
4. Add monitoring on subnet IP utilization and a capacity review as part of onboarding new teams.
