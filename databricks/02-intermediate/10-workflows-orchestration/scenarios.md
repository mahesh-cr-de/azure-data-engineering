# Scenarios — Databricks Workflows & Job Orchestration

### Scenario 1 — "A nightly job pipeline takes 3 hours and the business wants it done in under 1"

**Setup:** A multi-task Databricks Workflow ingests from five source systems, cleans each into Silver, then builds ten Gold tables, all currently defined as one long linear chain of tasks.

**How to reason through it:**
1. First diagnostic step: pull up the job's DAG and run history — check whether tasks are actually structured with real dependencies, or whether they were just defined in the order someone thought of them, forcing sequential execution where parallel execution would be correct.
2. Identify genuine independence: the five source ingestions almost certainly don't depend on each other, and many of the ten Gold tables likely depend only on specific Silver tables, not on every other Gold table — restructure the DAG so independent branches run in parallel rather than sequentially, which is often the single largest win available without touching any actual Spark logic.
3. Check cluster allocation: if all tasks share one job cluster sized for the heaviest single task, parallel branches will contend for the same limited compute — evaluate whether some tasks should get their own appropriately-sized cluster so parallelism at the DAG level actually translates into parallelism at the compute level, rather than tasks queuing behind each other on a saturated shared cluster.
4. Only after fixing orchestration structure would I look at task-level Spark tuning (Topic 07/13 concerns) — reframing the DAG is usually the higher-leverage, lower-risk fix compared to re-tuning ten different transformation jobs individually, and it's the answer that shows orchestration-level thinking rather than jumping straight to Spark internals.

### Scenario 2 — "One flaky upstream API causes the whole nightly pipeline to fail about twice a week"

**Setup:** A task early in the DAG calls a third-party API to pull reference data; it fails intermittently with timeouts, and every failure currently kills the entire downstream pipeline, requiring someone to manually re-run it the next morning.

**How to reason through it:**
1. First, add an appropriately bounded retry policy (e.g., 3 retries with exponential backoff) on that specific task — this alone likely resolves a meaningful fraction of the "twice a week" failures if they're genuinely transient network blips rather than sustained outages.
2. Consider whether the pipeline's correctness actually requires same-day-fresh reference data, or whether falling back to yesterday's cached copy for one run (with an alert, not a silent failure) would be an acceptable degradation — if so, redesign the task to attempt a fresh pull but fall back gracefully rather than hard-failing the entire downstream DAG on any API hiccup.
3. Address the operational pain point directly: configure job-level failure alerting (email/Slack) scoped specifically to this task so the team knows immediately rather than discovering it the next morning, and consider whether the job's schedule has enough buffer before the pipeline's SLA that an automatic retry-the-whole-job-once policy at the job level (not just task-level retries) is a reasonable safety net.
4. Root-cause framing for a senior answer: a single external dependency with no fallback sitting early in a critical DAG is itself a design risk worth naming explicitly, not just a retry-tuning problem — the conversation should end with "should this reference data even be pulled live every run, or should it be cached/refreshed on its own decoupled schedule."

### Scenario 3 — "Design the orchestration for a pipeline that spans an on-prem SQL Server, ADLS, Databricks transformations, and a Power BI refresh"

**Setup:** An interviewer describes a pipeline crossing several systems and asks how you'd split responsibility between ADF and Databricks Workflows.

**How to reason through it:**
1. Propose ADF as the top-level orchestrator: it has native, well-supported connectors for on-prem SQL Server (via Self-Hosted Integration Runtime, ADF Topic 05) and for triggering a Power BI dataset refresh at the end — neither of which Databricks Workflows is built to do directly, so trying to force the entire thing into Workflows would mean reinventing connectors ADF already provides.
2. Have ADF's pipeline do the cross-system parts it's suited for: copy from SQL Server into ADLS raw, then invoke a Databricks Workflow (via ADF's Databricks activity, or REST API call + polling) to run the actual multi-task Spark transformation DAG (Bronze → Silver → Gold), then trigger the Power BI refresh once the Databricks job reports success.
3. Inside that Databricks Workflow, apply everything from this topic — task-level DAG structuring, parallel Gold-layer branches, job clusters, retries — since once execution is inside Databricks, Workflows is the more natural, tightly-integrated tool for that portion.
4. Call out the failure-propagation design explicitly: ADF's pipeline needs to treat the Databricks Workflow invocation as a real dependency (fail the ADF pipeline, and skip the Power BI refresh, if the Databricks job fails) rather than firing-and-forgetting the trigger — this cross-system dependency handling is exactly the kind of detail that separates a working demo from a production-grade design in this kind of question.
