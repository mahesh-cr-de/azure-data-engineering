# Talking points — condensed for verbal delivery

**Opening line:**

> "I wouldn't start by cutting clusters. I'd start by making spend visible and attributable, then remove waste in order of size."

## Mnemonic: Measure → Remove waste → Redesign → Retain (guardrails)

### 1. Measure
- Mandatory tags via cluster policies; billing system tables for a ranked cost view
- Track **unit cost** (per run, per TB), not just the total

### 2. Remove waste (quick wins)
- Auto-terminate idle clusters; move scheduled work to job clusters
- Right-size from Spark UI utilization; autoscaling with sane bounds
- Spot workers with on-demand driver and fallback
- SQL warehouses: separate by workload, short auto-stop, capped scale-out

### 3. Redesign
- Faster code is cheaper code: skew, spill, shuffles, UDFs
- OPTIMIZE / clustering, incremental instead of full loads, smarter schedules

### 4. Retain
- Policies, budgets, anomaly alerts, showback/chargeback, monthly FinOps review

**Closing line:**

> "Every change is piloted on one workload with before/after numbers, so the 30% saving doesn't cost us an SLA."

## Delivery tip
Quote the Pareto idea: a handful of jobs and idle interactive clusters usually drive most of the bill, so you start there.

## Likely follow-ups to prep for
- How do you decide whether Photon is worth it for a workload?
- When is serverless cheaper, and when is it not?
- A team insists they need a large always-on cluster. How do you respond?
- How would you set up chargeback fairly for shared platform costs?
