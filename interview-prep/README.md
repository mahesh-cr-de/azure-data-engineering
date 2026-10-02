# Azure Data & AI Interview Prep

A growing collection of my answers, talking points, and diagrams for Azure data engineering, platform leadership and agentic AI interview questions. Used both for interview prep and as source material for LinkedIn posts and YouTube content.

## Structure

```
azure-ai-interview-prep/
├── README.md
└── questions/
    └── 01-agentic-ai-architecture-azure/
        ├── question.md          # the question as asked
        ├── full-answer.md       # the complete, detailed answer
        ├── talking-points.md    # condensed version to memorize / deliver verbally
        └── diagrams/
            ├── three-pillars.png
            └── request-flow.png
```

## Adding a new question

1. Create a new folder under `questions/`, numbered sequentially: `02-<short-slug>/`
2. Add `question.md` and `full-answer.md` at minimum
3. Add `talking-points.md` once you've condensed it for verbal delivery
4. Drop any diagrams in a `diagrams/` subfolder
5. Add `linkedin-post.md` if/when you turn it into a post

## Index

| # | Question | Topics |
|---|----------|--------|
| 01 | [Architecting an enterprise-grade agentic AI system on Azure](questions/01-agentic-ai-architecture-azure/question.md) | Azure OpenAI, MCP, Unity Catalog, Entra ID, APIM |
| 02 | [Metadata-driven ingestion framework on ADF + Databricks](questions/02-metadata-driven-ingestion-adf-databricks/question.md) | ADF, Databricks, control tables, incremental load, idempotency |
| 03 | [Medallion lakehouse with Unity Catalog on Azure](questions/03-medallion-lakehouse-unity-catalog/question.md) | Bronze/Silver/Gold, Unity Catalog, data contracts, RBAC |
| 04 | [Streaming Event Hubs to Delta with exactly-once guarantees](questions/04-streaming-event-hubs-delta-exactly-once/question.md) | Event Hubs, Structured Streaming, watermarking, MERGE, DLQ |
| 05 | [Data quality and observability framework](questions/05-data-quality-observability-framework/question.md) | DQ expectations, SLOs, lineage, data contracts, incident process |
| 06 | [Cutting Databricks cost by 30% without breaking SLAs](questions/06-databricks-cost-optimization-finops/question.md) | FinOps, cluster policies, job clusters, spot, chargeback |
| 07 | [CI/CD for Azure Databricks](questions/07-cicd-databricks-asset-bundles-terraform/question.md) | Asset Bundles, Terraform, GitHub Actions, testing, promotion, rollback |
