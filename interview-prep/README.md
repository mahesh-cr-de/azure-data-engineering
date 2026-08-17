# Azure AI Interview Prep

A growing collection of my answers, talking points, and diagrams for Azure and agentic AI interview questions. Used both for interview prep and as source material for LinkedIn posts and YouTube content.

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
