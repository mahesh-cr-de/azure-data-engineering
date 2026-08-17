# Azure Data Factory — Interview-Ready Notes

A structured, visual, end-to-end knowledge base covering Azure Data Factory (ADF) from absolute basics to real-world enterprise scenarios. Built so that anyone preparing for a Data Engineering / Azure interview can read module-by-module and walk in ready.

Each topic file includes: a plain-English explanation, an architecture diagram, the exact configuration options you'd set in the ADF portal, a hands-on step-by-step where relevant, common interview Q&A, and common pitfalls/gotchas.

**New topics are added daily (5 per day)** as the learning path builds out from fundamentals → intermediate scenarios → advanced/enterprise patterns → troubleshooting & interview drills.

---

## 📚 Learning Path

### Module 01 · Fundamentals ✅ *(complete)*
| # | Topic |
|---|---|
| 01 | [What is Azure Data Factory? (Core Architecture)](01-fundamentals/01-what-is-adf.md) |
| 02 | [Linked Services](01-fundamentals/02-linked-services.md) |
| 03 | [Datasets](01-fundamentals/03-datasets.md) |
| 04 | [Pipelines & Activities Overview](01-fundamentals/04-pipelines-and-activities.md) |
| 05 | [Integration Runtime Types](01-fundamentals/05-integration-runtime.md) |

### Module 02 · Core Scenarios ✅ *(complete)*
| # | Topic |
|---|---|
| 06 | [Incremental Load Patterns](02-core-scenarios/01-incremental-load-patterns.md) |
| 07 | [Watermark-Based CDC — End-to-End Build](02-core-scenarios/02-watermark-cdc.md) |
| 08 | [Metadata-Driven (Parametrized) Pipelines](02-core-scenarios/03-metadata-driven-pipelines.md) |
| 09 | [Error Handling & Retries](02-core-scenarios/04-error-handling-and-retries.md) |
| 10 | [Triggers Deep-Dive](02-core-scenarios/05-triggers-deep-dive.md) |

### Module 03 · Data Transformation ✅ *(in progress)*
| # | Topic |
|---|---|
| 11 | [Mapping Data Flows Overview](03-data-transformation/01-mapping-data-flows.md) |
| 12 | [Wrangling Data Flows](03-data-transformation/02-wrangling-data-flows.md) |
| 13 | [Databricks Notebook Integration](03-data-transformation/03-databricks-integration.md) |
| 14 | [Schema Drift Handling](03-data-transformation/04-schema-drift.md) |
| 15 | [Slowly Changing Dimensions (SCD) in Data Flows](03-data-transformation/05-scd-patterns.md) |

### Module 04 · Enterprise & Governance *(coming soon)*
CI/CD (Git + ARM/Bicep deployment), monitoring & alerting, cost optimization, security (Managed Identity, Private Endpoints, Key Vault), Unity Catalog-style governance patterns.

### Module 05 · Interview Drills *(coming soon)*
Scenario-based system design questions, whiteboard architecture exercises, common "design a pipeline for X" prompts with model answers.

---

## 🗂️ Repo Structure

```
azure-data-factory/
├── README.md                      ← you are here
├── 01-fundamentals/
│   ├── README.md                  ← module index
│   ├── 01-what-is-adf.md
│   ├── 02-linked-services.md
│   ├── 03-datasets.md
│   ├── 04-pipelines-and-activities.md
│   ├── 05-integration-runtime.md
│   └── images/                    ← diagrams used in this module's topics
├── 02-core-scenarios/
│   ├── README.md                  ← module index
│   ├── 01-incremental-load-patterns.md
│   ├── 02-watermark-cdc.md
│   ├── 03-metadata-driven-pipelines.md
│   ├── 04-error-handling-and-retries.md
│   ├── 05-triggers-deep-dive.md
│   └── images/
├── 03-data-transformation/
│   ├── README.md                  ← module index
│   ├── 01-mapping-data-flows.md
│   ├── 02-wrangling-data-flows.md
│   ├── 03-databricks-integration.md
│   ├── 04-schema-drift.md
│   ├── 05-scd-patterns.md
│   └── images/
└── 04-... (future modules)
```

## ✅ How to Use This Repo for Interview Prep

1. Read modules **in order** — later topics assume you know the fundamentals.
2. For each topic, don't just read — say the **TL;DR** out loud as if answering an interviewer.
3. Pay special attention to the **"Configuration Options"** tables — interviewers love asking *"what would you actually configure to solve X?"*
4. Use the **Common Pitfalls** sections as a checklist before a system-design round — these are the details that separate senior candidates from junior ones.

---
*Last updated: 2026-07-27*
