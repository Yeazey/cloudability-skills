# Agentic FinOps — Workflow Definitions

## Overview

Each workflow is a sequence of MCP tool calls orchestrated by an LLM agent. Workflows are composable — the output of one can trigger another.

---

## Workflow A: Daily FinOps Standup

**Trigger:** Cron (morning) or on-demand via CLI  
**Phase:** 1 (Implemented ✅)  
**Delivery:** Slack channel

### Steps

```
1. [Cloudability] run_cost_report → MTD spend by vendor, WoW comparison
2. [Cloudability] run_cost_report → Top movers by service (WoW change)
3. [Cloudability] list_anomalies → Active anomalies count and top items
4. [Cloudability] get_rightsizing_recommendations → Open savings pipeline
5. [Cloudability] list_budgets → Budget health and at-risk items
6. [Agent]        Format as Slack Block Kit message
7. [Slack]        Post to designated channel
```

### Output Format

- Spend snapshot (MTD, daily rate, projection, MoM/WoW change)
- Provider breakdown with change indicators
- Key movers (services with >20% WoW change)
- Attention items (anomalies, new services, sharp changes)
- Optimization summary (rightsizing count, savings potential)

---

## Workflow B: Automated Anomaly Triage

**Trigger:** Scheduled (every 4 hours) or post-daily-standup  
**Phase:** 2 (Planned)  
**Delivery:** Jira ticket + Slack notification + PagerDuty (if critical)

### Steps

```
1. [Cloudability] list_anomalies (filter: state=open, last 24h)
2. For each new anomaly:
   a. [Cloudability] get_anomaly → full details (dimension, amount, expected)
   b. [Cloudability] run_cost_report → drill into root cause
   c. [Cloudability] get_rightsizing_recommendations → check actionable recs
   d. [Agent]        Classify severity: critical / warning / info
   e. [Agent]        Generate RCA summary with:
                     - What changed (service, region, account)
                     - Magnitude ($ and % above expected)
                     - Probable cause
                     - Recommended action
   f. [Atlassian]   Create Jira ticket with RCA, savings estimate, assignee
   g. [Slack]       Notify channel with summary
   h. [PagerDuty]   If severity == critical → create incident, page on-call
```

### Severity Classification

| Severity | Criteria | Action |
|----------|----------|--------|
| Critical | >$10K/day above expected OR >50% spike | PagerDuty + Jira + Slack |
| Warning | >$1K/day above expected OR >25% spike | Jira + Slack |
| Info | Any other detected anomaly | Slack only |

---

## Workflow C: Proactive Budget Breach Prevention

**Trigger:** Weekly (Monday) or when forecast crosses 90% of budget  
**Phase:** 2 (Planned)  
**Delivery:** Slack DM to budget owner + Jira epic

### Steps

```
1. [Cloudability] cldy_forecast_get → projected spend for current period
2. [Cloudability] list_budgets → get all budget thresholds
3. [Agent]        Compare: if projected > 90% of any budget threshold
4. For each at-risk budget:
   a. [Cloudability] run_cost_report → identify top cost drivers in that view
   b. [Cloudability] get_rightsizing_recommendations → calculate available savings
   c. [Agent]        Generate action plan:
                     - Projected overage amount
                     - Top 5 cost drivers
                     - Available quick wins (rightsizing)
                     - Recommended actions with effort/savings
   d. [Atlassian]   Create epic with individual tasks per recommendation
   e. [Slack]       DM budget owner with forecast + action plan link
```

---

## Workflow D: Rightsizing Pipeline Management

**Trigger:** Weekly (Tuesday) or on-demand  
**Phase:** 2–3 (Planned)  
**Delivery:** Jira tickets + Slack notifications + GitHub PRs (Phase 3)

### Steps

```
1. [Cloudability] get_rightsizing_recommendations → all recs sorted by savings
2. [Atlassian]   Search Jira → find existing tickets for these resources
3. [Agent]       Diff: identify new recs without tickets
4. For each new recommendation:
   a. [Atlassian]   Create Jira ticket with:
                     - Current instance type/size
                     - Recommended instance type/size
                     - Estimated monthly savings
                     - Resource identifier and account
                     - Assigned to account owner
   b. [Slack]       Notify team channel with weekly pipeline summary
5. (Phase 3 — with Terraform):
   a. [GitHub]      Create branch with instance type variable change
   b. [Terraform]   Run plan to validate no breaking dependencies
   c. [GitHub]      Create PR with plan output
   d. [Slack]       Notify engineer → await approval
```

---

## Workflow E: Monthly FinOps Close / Chargeback Report

**Trigger:** 1st business day of month  
**Phase:** 2 (Planned)  
**Delivery:** Confluence page + Slack post to leadership channel

### Steps

```
1. [Cloudability] run_cost_report → allocated costs by business dimension (prior month)
2. [Cloudability] list_business_metrics → apply surcharge/unit economics
3. [Cloudability] list_budgets → compare actuals vs thresholds
4. [Agent]        Generate monthly close report:
                  - Total spend by business unit
                  - Budget variance (over/under)
                  - Unit economics (cost per transaction, per user, etc.)
                  - MoM trends
                  - Savings delivered vs target
5. [Atlassian]   Update/create Confluence page with report
6. [Slack]       Post executive summary to leadership channel
```

---

## Workflow F: New Service Detection & Tagging Governance

**Trigger:** Daily (as part of standup) or weekly  
**Phase:** 2 (Planned)  
**Delivery:** Jira ticket + Slack notification to team lead

### Steps

```
1. [Cloudability] run_cost_report → services appearing this week with no prior spend
2. [Cloudability] list_business_dimensions → check if new service is mapped
3. [Cloudability] list_tag_mappings → check if tags are configured for this service
4. [Agent]        Classify: is this service properly allocated?
5. If unmapped:
   a. [Atlassian]   Create Jira task: "Tag and allocate new service: {name}"
   b. [Slack]       Notify team lead responsible for that account
```

---

## Workflow Composition

Workflows can chain:

```
Daily Standup (A) → detects anomaly → triggers Anomaly Triage (B)
Budget Prevention (C) → identifies savings → feeds Rightsizing Pipeline (D)
New Service Detection (F) → creates tag task → validates in next Monthly Close (E)
```

---

## Error Handling

All workflows follow these patterns:

1. **Token expiry (401)** → Log error, notify operator, stop workflow (don't retry with stale auth)
2. **API rate limit** → Exponential backoff, max 3 retries
3. **Slack post failure** → Retry once, then log and continue (don't block data collection)
4. **Empty data** → Report "no data" rather than failing (e.g., 0 anomalies is a valid state)
5. **Partial failure** → Complete what you can, report what failed (don't rollback successful steps)
