# Interview Q&A — Security & Networking

**Q1. Explain the control plane and compute plane, and why it matters for security.**
> The control plane is managed by Databricks (UI, APIs, scheduler, cluster manager); the compute plane is where data is processed. In the classic model, compute runs as VMs in the customer's subscription, so the customer's network controls apply directly; in serverless, compute runs in a Databricks-managed network and is controlled through account-level network configuration. It matters because the security questions split cleanly: who can reach the control plane, how compute reaches the control plane, and how compute reaches data and the internet.

**Q2. What is VNet injection and what problem does it solve?**
> It deploys the classic compute plane into a virtual network I own, using two delegated subnets and my own NSG and routing. That lets me connect to on-premises systems via peering, VPN or ExpressRoute, apply user-defined routes and firewalls, and control egress. The default managed network gives me none of that control. Planning subnet size is important, since it caps the number of nodes and undersized subnets cause cluster start failures.

**Q3. What is secure cluster connectivity (No Public IP)?**
> Cluster nodes get no public IP addresses and the network exposes no inbound ports; the compute plane initiates an outbound connection to the control plane. That removes a whole class of exposure and is the baseline for enterprise deployments.

**Q4. What is the difference between front-end and back-end Private Link?**
> Front-end Private Link is for user and API traffic to the workspace: it gives clients a private endpoint instead of reaching the web UI and REST APIs over the public internet. Back-end Private Link is for the compute plane's connection to the control plane. A fully private design uses both, plus private endpoints to storage and other data services, and disables public network access, with careful private DNS configuration.

**Q5. RBAC versus ACLs — explain the difference in a Databricks context.**
> RBAC assigns roles at Azure scopes (subscription, resource group, resource), for example who can create a workspace or has Storage Blob Data Contributor on an account; it is coarse and inherited. ACLs are per-object permission lists, such as CAN MANAGE on a job or cluster in the workspace, or POSIX ACLs on ADLS directories. For data, the preferred model with Unity Catalog is neither: grant access with Unity Catalog privileges to Entra ID groups, while a managed identity holds the storage permission, so users never need direct storage access.

**Q6. How do you handle identity and offboarding?**
> Entra ID is the source of truth, with SSO, MFA and conditional access. Users, groups and service principals are provisioned to the Databricks account through SCIM or automatic identity management, and all access is granted to groups. Offboarding is then disabling the account or removing group membership centrally, and access disappears everywhere including Unity Catalog. Automation uses service principals, not personal accounts or personal access tokens.

**Q7. How would you prevent data exfiltration from a workspace?**
> Layered controls: no public IPs and private endpoints to data services; egress through a firewall or NAT with an allowlist; Unity Catalog external locations so users cannot point compute at arbitrary storage; cluster policies restricting init scripts and access modes; row and column controls on sensitive data; restricted permissions to export or create external connections; and audit logs with alerts on unusual volumes of reads or permission changes.

**Q8. A team reports they cannot reach the workspace after you enabled Private Link. What do you check?**
> Almost always DNS and routing. I verify that the private DNS zone for the workspace resolves to the private endpoint's IP from the user's network, that conditional forwarding exists for on-premises clients, that the private endpoint is approved and in the right subnet, that NSG and firewall rules allow the traffic, and whether public network access is disabled for users who are not on the private path. I also check IP access lists if they are in use.
