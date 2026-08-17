# Scenarios — Notebooks, Repos & Databricks CLI

### Scenario 1 — "Set up a clean dev → prod workflow for a team of 7 engineers"

**Setup:** You're joining as EM/lead and the team currently develops directly in ad hoc workspace notebooks with no source control, and "deploys" by manually copying a notebook into a "prod" folder.

**How to design the fix:**
1. Connect the workspace to a real git remote via **Repos** — every engineer works on a feature branch inside their own Repos checkout, commits, and opens a PR against `main`, same as any other codebase.
2. Move shared logic (common transformations, schema definitions, utility functions) out of individual notebooks and into **importable Python modules** checked into the same repo, so multiple notebooks and jobs share one source of truth instead of copy-pasted `%run` includes drifting apart.
3. Production jobs get repointed to run against a **specific branch or tag** (e.g. `main`, updated only via merged PRs) rather than an arbitrary developer's live workspace path — this is the single biggest risk in the "manually copy the notebook" approach: nothing stops an in-progress edit from silently becoming what production runs next.
4. Add a lightweight CI step (see Topic 15) that at minimum runs notebook/module unit tests and a lint check on PR before merge — even a modest automated check catches more than "someone eyeballed the diff."
5. Mention the cultural piece explicitly, since this is an EM-flavored scenario: rolling this out means retraining habits, not just flipping a switch — pair a senior engineer with anyone unfamiliar with git-based workflows for the first sprint rather than just mandating it and hoping.

### Scenario 2 — "A critical secret leaked because it was hardcoded in a notebook"

**Setup:** A postmortem reveals a database password was pasted directly into a notebook cell months ago; it's now sitting in notebook revision history and possibly in the connected git repo.

**How to walk through remediation:**
1. Immediate action: **rotate the leaked credential** — assume it's compromised the moment it's found in any accessible history, regardless of whether you can prove it was actually misused.
2. Root-cause fix: migrate to **`dbutils.secrets`** backed by an Azure Key Vault-backed secret scope, so credentials are referenced by scope/key at runtime and never appear in notebook source at all — the CLI/API can create these scopes so this is scriptable, not a one-off manual setup per notebook.
3. Address the **history problem**, not just the going-forward problem: notebook revision history inside the workspace and any git history in the connected Repo both need the secret purged (git history rewrite is disruptive — flag it honestly as a tradeoff to make with the team, not something to do silently) — and note that Databricks notebook version history retention/purge behavior is worth confirming with workspace admins as part of the incident response, since "delete it from the current cell" doesn't remove it from history.
4. Process fix: add a pre-commit or CI secret-scanning check on Repos-backed pipelines so a hardcoded credential pattern gets caught before merge next time, not after a postmortem.

### Scenario 3 — "New hire's notebook works for them, fails for everyone else running the same job"

**Setup:** A junior engineer wrote a notebook that runs fine when they click "Run All" interactively, but the scheduled job (same notebook) fails every night with a `NameError` / `AttributeError` a few cells in.

**How to reason through it:**
1. First hypothesis (see Q7): the engineer likely ran cells **out of order** while developing interactively, leaving some variable or import defined from an earlier ad hoc cell execution that isn't actually part of the notebook's linear top-to-bottom flow — the job always executes strictly in order on a fresh cluster attach, so it never benefits from that leftover state.
2. Verification: have them **detach and reattach the cluster** (or use a fresh cluster), then "Run All" top to bottom without any manual cell reordering — if it now reproduces the same failure interactively, the hypothesis is confirmed and it's a code-ordering bug, not an infrastructure issue.
3. Secondary check: confirm the **job cluster's DBR version and installed libraries** match what the engineer's personal interactive cluster has — a library installed ad hoc on their interactive cluster (via `%pip install` at the notebook level) won't automatically exist on a fresh job cluster unless it's declared properly (cluster-scoped library, `requirements.txt` in the Repo, or an init script) — this is a very common "works for me" gap for newer team members.
4. Use this as a coaching moment (fits the EM angle): this is exactly the kind of bug that a "always Run All from a clean cluster before considering a notebook done" habit prevents — worth adding to team onboarding/code-review norms rather than just fixing this one instance.
