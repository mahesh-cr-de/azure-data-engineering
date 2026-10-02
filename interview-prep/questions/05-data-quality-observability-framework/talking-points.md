# Talking points — condensed for verbal delivery

**Opening line:**

> "I'd treat this as a trust problem: detect issues before consumers do, and make sure every issue has an owner."

## Mnemonic: Define → Detect → Deliver safely → Drive ownership

### 1. Define
- Quality dimensions plus an SLO per critical dataset ("refreshed by 7 AM, 99% of days")

### 2. Detect
- Checks at every boundary: contract, ingest, Silver gate, Gold reconciliation
- Severity levels: warn, drop to quarantine, fail the run
- Metrics table + anomaly detection for what nobody wrote a rule for

### 3. Deliver safely
- Gate Gold publishing; consumers keep the last known good snapshot with a delay banner
- Lineage turns an alert into an impact list

### 4. Drive ownership
- Named owner and on-call per dataset; alerts go to the owner
- Data contracts with producers; blameless postmortems
- Start with the datasets behind executive dashboards, then expand

**Closing line:**

> "Late and labeled beats on-time and wrong. That one rule rebuilds trust faster than any tool."

## Delivery tip
Lead with the incident-to-fix story (detect, contain, root cause, prevent). Managers are hired for the operating model, not just the checks.

## Likely follow-ups to prep for
- How do you prevent alert fatigue?
- A producing team refuses to adopt contracts. What do you do?
- How do you measure whether the framework is working?
- DLT expectations vs Great Expectations vs custom: how do you choose?
