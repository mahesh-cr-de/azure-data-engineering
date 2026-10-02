# Talking points — condensed for verbal delivery

**Opening line:**

> "Exactly-once is a property of the whole path: replayable source, durable checkpoint, idempotent sink. If one is missing, it's at-least-once."

## Mnemonic: Read → Remember → Write → Watch

### 1. Read
- Kafka endpoint on Event Hubs; partition count caps parallelism, so size it up front
- Dedicated consumer group; `maxOffsetsPerTrigger` to control batch size

### 2. Remember
- Checkpoint on durable ADLS storage
- Watermark bounds state; late events go to a late-arrivals table, not the void

### 3. Write
- Bronze: raw payload, append-only
- Silver: `foreachBatch` + MERGE on business key, so replays are harmless
- Bad records to a dead-letter table with reason and offset

### 4. Watch
- Input rate vs processing rate, batch duration, lag alerts
- Small-file control: auto-compaction + scheduled OPTIMIZE

**Closing line:**

> "I choose the trigger interval from the business SLA, because every second of latency I remove costs money and small files."

## Delivery tip
When asked about exactly-once, explicitly say "idempotent sink" — it's the phrase interviewers listen for.

## Likely follow-ups to prep for
- What happens if the checkpoint is lost or corrupted?
- How would you reprocess the last 7 days after a logic bug?
- How do you scale beyond the partition limit?
- Streaming vs triggered batch: how do you decide?
