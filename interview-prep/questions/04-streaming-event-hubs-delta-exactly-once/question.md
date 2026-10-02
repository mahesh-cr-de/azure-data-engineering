## Question

Design a near-real-time pipeline that ingests 50,000 order events per second from Azure Event Hubs into Delta Lake on Databricks. Events can arrive late, be duplicated, or have changing schemas. How do you guarantee correctness, handle failures and keep the pipeline observable?

**Topics:** Event Hubs, Structured Streaming, Delta Lake, exactly-once, watermarking, checkpointing, dead-letter handling

**Role context:** Engineering Manager (Data)
