# Talking points — condensed for verbal delivery

**Opening line** (say this first, it frames everything else):

> "I'd separate the LLM's reasoning from the data execution environment — the model plans and asks, it never touches data directly."

![Three pillars overview for enterprise Agentic AI](./diagrams/three-pillars.png)

## Mnemonic: Think → Touch → Track

### 1. Think (orchestration)
- Azure OpenAI GPT-4o in our private VNet — data never leaves the tenant
- MCP is the key term to drop: expose the Gold layer as standardized MCP servers instead of custom integrations per source
- Agent discovers tools dynamically (`query_sales_data`, `get_customer_churn_metric`) and calls them via JSON-RPC

### 2. Touch (secure execution)
- "Never raw SQL against Gold" — strongest line, say it explicitly
- Build a semantic layer: curated, aggregated views, not direct table access
- Feed the agent a strict data dictionary in the system prompt to cut hallucinations
- Validation loop: bad syntax → agent self-corrects → retries, before the user ever sees it

![Secure execution flow for enterprise agentic AI](./diagrams/request-flow.png)

### 3. Track (governance)
- Entra ID pass-through — agent acts *on behalf of* the user, so Unity Catalog blocks unauthorized data at the source, not via agent logic
- APIM in front of the OpenAI endpoint — rate limits, per-user cost tracking, kills runaway agent loops
- Explainability — always return the SQL/steps with the answer, human-in-the-loop by design

**Closing line** (signals "manager," not just "engineer"):

> "My priority isn't just that this works — it's that it's safe and auditable by construction, not because we're trusting the model to behave."

## Delivery tip
Don't recite all three pillars evenly. Lead with whichever one matches the interviewer's company — security-heavy companies get Track first, AI-platform-heavy companies get Think first.

## Likely follow-ups to prep for
- How would you handle a tool call that returns too much data / a runaway aggregation?
- How do you version or test changes to the semantic layer views?
- What happens if Unity Catalog RBAC and the MCP server's own auth disagree?
- How would you extend this to write-back actions, not just read queries?
