# Talking points — condensed for verbal delivery

**Opening line:**

> "Medallion isn't three folders; it's three contracts. Each layer has an owner and a promise about quality."

## Mnemonic: Raw → Right → Ready

### 1. Raw (Bronze)
- Append-only, exactly as received plus ingest metadata, schema-tolerant, replayable
- No business logic here, ever

### 2. Right (Silver)
- Typed, deduplicated, conformed entities; MERGE; SCD2 where needed
- DQ gate with a quarantine table: bad rows are isolated, not silently lost, and don't block good data

### 3. Ready (Gold)
- Business marts and metrics with named owners and freshness SLAs
- Optimized for query patterns (clustering, OPTIMIZE)

### Governance in one breath
- Catalog per environment/domain, schema per layer, shared catalog for conformed reference data
- Managed identity + External Locations, no keys or mounts
- Grants to Entra groups; column masks and row filters on sensitive data; lineage for impact analysis

**Closing line:**

> "If Gold is wrong, I can point to the contract that broke, the owner, and replay from Bronze to fix it."

## Delivery tip
Don't list technologies first. Start with the contract per layer, then show Unity Catalog as the thing that enforces it.

## Likely follow-ups to prep for
- Would you ever skip Silver or add a fourth layer?
- How do you handle a breaking schema change from an upstream team?
- How do you share a Gold table across domains without copying it?
- How do you decide between DLT and hand-built notebooks/jobs?
