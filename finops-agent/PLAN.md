# Agentic FinOps with Cloudability MCP: Architecture & Planning Document

**Date:** June 26, 2026  
**Status:** Research & Planning  
**Author:** FinOps Engineering  

---

## Executive Summary

This document outlines a plan to build a **proactive, multi-agent FinOps system** using **Cloudability MCP as the core driver**, inspired by Google Cloud's "Proactive Billing Agent" architecture (published June 2026). The system would enable autonomous cost anomaly triage, rightsizing execution, budget management, and cross-team notification — bridging the gap between "what happened?" and "here's how we fix it."

---

## 1. Reference Architecture: Google's 5-Layer Agentic FinOps

Source: [Google Dev Community — The Future of Cloud Governance](https://discuss.google.dev/t/the-future-of-cloud-governance-building-a-proactive-billing-agent-with-agent-platform/369751)

| Layer | Google's Implementation | Purpose |
|-------|------------------------|---------|
| 1. Interaction | Gemini Enterprise + Slack/Gmail/Jira | Natural language interface, workflow continuity |
| 2. Multi-Agent Core | ADK Orchestrator + Sub-agents | Divide-and-conquer reasoning, specialized agents |
| 3. Action & Execution | Managed BigQuery MCP Server | Structured, safe tool execution |
| 4. Context & Governance | RAG over corporate policies | Ground recommendations in org-specific rules |
| 5. Data Foundation | FOCUS billing data in BigQuery | Standardized cost data + observability metrics |

Their MVP uses NL2SQL against BigQuery billing exports. AWS's parallel implementation (published April 2025) uses Bedrock multi-agent with Cost Explorer + Trusted Advisor Lambda action groups.

### The "Observe-Reason-Act" Framework

The article defines a paradigm shift from reactive dashboards to:

1. **Observe** — Ingest billing data, detect anomalies, monitor utilization
2. **Reason** — Apply corporate policies, budget constraints, architecture context
3. **Act** — Propose/execute remediation: rightsizing, storage tiering, commitment purchases

---

## 2. Cloudability MCP Capability Mapping

### Layer 5 — Data Foundation ✅ STRONG COVERAGE

| Capability | Cloudability MCP Tool(s) | Status |
|------------|--------------------------|--------|
| Cost reporting (any dimension/metric) | `cldy_cost_report_run`, `cldy_cost_report_enqueue` | ✅ Validated |
| Available dimensions/metrics discovery | `cldy_cost_measures_list`, `cldy_cost_filters_list` | ✅ Validated |
| Saved reports | `cldy_cost_reports_list` | ✅ Validated |
| Container/K8s cost data | `cldy_containers_usage`, `cldy_containers_labels`, `cldy_containers_counts` | ✅ Validated |
| Views (filtered cost subsets) | `list_views`, `get_view`, `create_view` | ✅ Validated |
| Business dimensions (custom allocation) | `list_business_mappings`, `create_business_dimension` | ✅ Validated |

### Layer 4 — Context & Governance ⚠️ PARTIAL

| Capability | Cloudability MCP Tool(s) | Status |
|------------|--------------------------|--------|
| Budget tracking & thresholds | `list_budgets`, `get_budget`, `create_budget` | ✅ Validated |
| Business metrics (unit economics) | `cldy_business_metrics_list`, `cldy_business_metric_create` | ✅ Validated |
| Account groups (org hierarchy) | `list_account_groups`, `get_account_group` | ✅ Validated |
| User/permission context | `list_users`, `get_user`, `views_get_for_user` | ✅ Validated |
| **Corporate policy RAG** | ❌ Not available | 🔴 Gap |
| **Compliance rule enforcement** | ❌ Not available | 🔴 Gap |

### Layer 3 — Action & Execution ⚠️ PARTIAL

| Capability | Cloudability MCP Tool(s) | Status |
|------------|--------------------------|--------|
| Anomaly detection & triage | `cldy_anomalies_list`, `cldy_anomaly_get` | ✅ Validated |
| Anomaly alerting (create/manage) | `cldy_anomaly_subscription_create`, `_update`, `_delete` | ✅ Validated |
| Rightsizing recommendations | `cldy_rightsizing_list`, `cldy_rightsizing_delete` | ✅ Validated |
| Budget alerts (create/manage) | `cldy_budget_subscription_create`, `_update`, `_delete` | ✅ Validated |
| Forecast/estimate | `cldy_forecast_get`, `cldy_estimate_get` | ✅ Validated |
| **Infrastructure remediation** | ❌ Not available | 🔴 Gap |
| **Commitment purchase execution** | ❌ Not available | 🔴 Gap |

### Layer 2 — Multi-Agent Core ⚠️ REQUIRES BUILD

| Capability | Status |
|------------|--------|
| LLM orchestrator | Available via Kiro CLI, LangGraph, CrewAI, ADK, or Bedrock |
| Specialized sub-agents | Definable via prompt templates |
| Tool routing | MCP protocol handles natively |

### Layer 1 — Interaction ⚠️ REQUIRES INTEGRATION

| Capability | Status |
|------------|--------|
| CLI/Chat interface | ✅ Kiro CLI (current) |
| Slack delivery | ✅ **VALIDATED** — Slack MCP bot posting to designated channel |
| Jira ticket creation | ✅ Atlassian MCP Server exists (official) |
| PagerDuty alerting | ✅ PagerDuty MCP Server exists (official) |

---

## 3. Complementary MCP Servers (All Confirmed to Exist)

### Atlassian Rovo MCP Server

- **Maintainer:** Atlassian (official) — [github.com/atlassian/atlassian-mcp-server](https://github.com/atlassian/atlassian-mcp-server)
- **Stars:** 803 | **License:** Apache-2.0
- **Auth:** OAuth 2.1 or API tokens
- **Capabilities:**
  - Search, create, update Jira issues
  - Bulk create tickets from notes
  - Summarize and create Confluence pages
  - Query Compass service dependencies
- **Supported Clients:** Claude, ChatGPT, GitHub Copilot, Gemini CLI, VS Code, Cursor

### Slack MCP Server

- **Maintainer:** Slack/Salesforce (official) — [slack.com/help/articles/48855576908307](https://slack.com/help/articles/48855576908307)
- **Capabilities:**
  - Search messages, files, members, channels
  - Retrieve and send messages to any conversation
  - Manage canvases (create/read)
  - Access member profile information
- **Partner Apps:** Claude, ChatGPT, Cursor, Perplexity, Notion, and more

### PagerDuty MCP Server

- **Maintainer:** PagerDuty (official) — [github.com/PagerDuty/pagerduty-mcp-server](https://github.com/PagerDuty/pagerduty-mcp-server)
- **Auth:** API token
- **Capabilities:**
  - Manage incidents (create, acknowledge, resolve)
  - Manage services, schedules, event orchestrations
  - Page on-call engineers
  - Read service configuration

### Terraform MCP Server

- **Maintainer:** HashiCorp (official, GA v1.0.0) — [github.com/hashicorp/terraform-mcp-server](https://github.com/hashicorp/terraform-mcp-server)
- **Auth:** TFE token
- **Capabilities:**
  - Registry lookups (providers, modules, policies)
  - Workspace management (create, update, delete, list)
  - Run management (plan, apply with `ENABLE_TF_OPERATIONS=true`)
  - Private registry access
- **Note:** Apply operations disabled by default for safety

### GitHub MCP Server

- **Maintainer:** GitHub (official) — [github.com/github/github-mcp-server](https://github.com/github/github-mcp-server)
- **Capabilities:**
  - Issues and PR management
  - Repository operations
  - Code search

---

## 4. System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         INTERACTION LAYER                                  │
│              Slack / CLI / Email / Dashboards                              │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────────┐
│                      ORCHESTRATOR (LLM Agent)                              │
│              Kiro CLI / LangGraph / CrewAI / ADK / Bedrock                 │
│                                                                           │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│  │ Cost Analyst│ │Anomaly Triage│ │ Rightsizing  │ │  Governance  │     │
│  │  Sub-Agent  │ │  Sub-Agent   │ │  Sub-Agent   │ │  Sub-Agent   │     │
│  └─────────────┘ └──────────────┘ └──────────────┘ └──────────────┘     │
└────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┘
     │          │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼          ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│Cloudabil-││Atlassian││  Slack  ││PagerDuty││Terraform││ GitHub  │
│ity MCP   ││  MCP    ││  MCP    ││  MCP    ││  MCP    ││  MCP    │
│          ││         ││         ││         ││         ││         │
│• Costs   ││• Create ││• Send   ││• Create ││• Plan   ││• Create │
│• Anomaly ││  tickets││  alerts ││  incidents││• Apply ││  issues │
│• Forecast││• Search ││• Search ││• Ack    ││• List   ││• PRs    │
│• Rightsiz││  docs   ││  context││  resolve ││  state  ││         │
│• Budgets ││• Update ││• Notify ││• Page   ││         ││         │
│• Views   ││  status ││  teams  ││  on-call ││         ││         │
└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘
```

---

## 5. Agentic Workflow Examples

### Workflow A: Automated Anomaly Triage → Ticket → Notify

```
1. [Cloudability MCP] cldy_anomalies_list → detect cost spike
2. [Cloudability MCP] cldy_cost_report_run → drill into root cause (service, region, account)
3. [Cloudability MCP] cldy_rightsizing_list → check if there's an actionable recommendation
4. [Atlassian MCP]   Create Jira ticket with RCA, savings estimate, assignee
5. [Slack MCP]       Notify #finops-alerts channel with summary
6. [PagerDuty MCP]   If severity > threshold, page on-call engineer
```

### Workflow B: Proactive Budget Breach Prevention

```
1. [Cloudability MCP] cldy_forecast_get → detect projected overspend
2. [Cloudability MCP] cldy_cost_report_run → identify top cost drivers
3. [Cloudability MCP] cldy_rightsizing_list → calculate potential savings
4. [Atlassian MCP]   Create epic with rightsizing tasks per resource
5. [Slack MCP]       DM budget owner with forecast + action plan
6. [Terraform MCP]   (Optional) Generate plan for instance type change
```

### Workflow C: Monthly FinOps Close / Chargeback Report

```
1. [Cloudability MCP] cldy_cost_report_run → pull allocated costs by business dimension
2. [Cloudability MCP] cldy_business_metrics_list → apply surcharge/unit economics
3. [Cloudability MCP] list_budgets → compare actuals vs thresholds
4. [Atlassian MCP]   Update Confluence page with monthly report
5. [Slack MCP]       Post executive summary to #finance-leadership
```

### Workflow D: Rightsizing Pipeline Management

```
1. [Cloudability MCP] cldy_rightsizing_list → get all recs sorted by savings
2. [Atlassian MCP]   Search Jira → check which recs already have tickets
3. [Atlassian MCP]   Create tickets for new recs, assign by owner
4. [GitHub MCP]      Create PR with Terraform variable change for instance type
5. [Terraform MCP]   Validate plan doesn't break dependencies
6. [Slack MCP]       Notify engineer → await approval
```

### Workflow E: New Service Detection & Tagging Governance

```
1. [Cloudability MCP] cldy_cost_report_run (filter: new services this week)
2. [Cloudability MCP] list_business_mappings → check if service is mapped
3. [Atlassian MCP]   Create Jira task: "Tag and allocate new service X"
4. [Slack MCP]       Notify team lead responsible for that account
```

---

## 6. Confidence Levels

### ✅ HIGH CONFIDENCE (Validated)

| Item | Evidence |
|------|----------|
| Cloudability MCP has rich cost querying (arbitrary dimensions, filters, metrics) | Tools validated — `cldy_cost_report_run` accepts any dimensions/metrics |
| Cloudability MCP handles anomaly lifecycle (detect → alert → subscribe) | Full CRUD on anomalies and subscriptions confirmed |
| Cloudability MCP provides rightsizing pipeline | `cldy_rightsizing_list` with filters, sorting, view scoping |
| Cloudability MCP manages budgets end-to-end | Create, list, update, delete budgets + subscriptions |
| Atlassian MCP Server is official, production-ready | 803 stars, Apache-2.0, OAuth 2.1, multi-client support |
| Slack MCP Server is official and supports write actions | Confirmed: "send messages to any type of conversation" |
| PagerDuty MCP Server is official | On PyPI, GitHub, with full API documentation |
| Terraform MCP Server is GA (v1.0.0) | HashiCorp official, workspace + registry + run management |
| Multi-agent orchestration patterns are proven | AWS Bedrock, Google ADK, LangGraph all demonstrate this |

### 🟡 MEDIUM CONFIDENCE (Likely but needs validation)

| Item | What We Need to Verify |
|------|----------------------|
| Cloudability MCP multi-cloud dimension coverage | Test specific AWS/Azure/GCP dimensions via `cldy_cost_measures_list` |
| Commitment/RI/SP coverage in rightsizing tools | May only cover instance rightsizing, not purchase recommendations |
| Slack MCP bidirectional workflows (human approval in Slack → agent continues) | Posting confirmed; event-driven response handling likely needs Bolt framework |
| Real-time data freshness | Billing data typically has 24-48h latency; forecasts may be more current |
| Rate limits on Cloudability MCP | No documentation found |

### 🔴 LOW CONFIDENCE / GAPS (Unknown or missing)

| Item | Impact | Mitigation |
|------|--------|------------|
| FOCUS-format data exports from Cloudability MCP | Cross-platform standardization | Cloudability's native dimensions may suffice; FOCUS mapping TBD |
| Corporate policy RAG layer | Recommendations won't be grounded in org-specific policies | Must custom-build: vector DB + doc ingestion + custom MCP server |
| Event-driven agent triggering | Agents must be cron-triggered (pull) vs event-driven (push) | Use Cloudability email/PagerDuty anomaly subscriptions + webhook receiver |
| Infrastructure remediation write-back | Cannot resize/terminate resources via Cloudability | Terraform MCP fills this gap but requires IaC maturity |
| Approval/human-in-the-loop workflow state | No built-in approval gates in MCP protocol | Build with Slack interactive messages or Jira status transitions |

---

## 7. Cloudability MCP vs Alternatives

| Dimension | Google (BigQuery MCP) | AWS (Bedrock Multi-Agent) | Finout MCP | Cloudability MCP |
|-----------|----------------------|--------------------------|-----------|-----------------|
| **Query flexibility** | Unlimited (NL2SQL) | Bounded (Cost Explorer API) | 21 structured tools | Structured API (dimensions/metrics catalog) |
| **Hallucination risk** | Higher (invalid SQL) | Low (Lambda action groups) | Low (structured) | Low (discoverable parameters) |
| **Setup complexity** | High (billing exports, schema config, SQL grounding) | Medium (CloudFormation stack) | Low (2-click) | Low (already configured) |
| **Multi-cloud** | Must ingest each provider | AWS only | AWS, Azure, GCP, K8s, SaaS | AWS, Azure, GCP, Oracle native |
| **Governance built-in** | Must build (RAG + custom) | Minimal | Virtual tags, budgets | Views, business dimensions, budgets, business metrics |
| **Remediation** | Requires separate tooling | Trusted Advisor recs only | CostGuard recommendations | Rightsizing recs (execution via Terraform MCP) |
| **Chargeback/Showback** | Must build | Not included | ✅ Native | ✅ Business dimensions + metrics |
| **Unit economics** | Must build | Not included | ✅ Native | ✅ Business metrics |

**Key Cloudability advantage:** No data engineering required. The "Data Foundation" layer is already built and maintained. You skip the hardest, most expensive part of Google's architecture.

---

## 8. Implementation Roadmap

### Phase 1: Single-Agent FinOps Analyst (2-4 weeks)

**Objective:** AI agent that answers any FinOps question using Cloudability MCP.

| Task | Effort | Prerequisites | Status |
|------|--------|---------------|--------|
| Connect Cloudability MCP to orchestrator | Done | Cloudability API access | ✅ Done |
| Build FinOps-expert system prompts | 2-3 days | Domain knowledge | ✅ Done (cldy skill) |
| Create daily standup workflow | 1 week | Slack workspace admin | ✅ Done (cldy-dash checkin) |
| Add Slack MCP for delivery | 3-5 days | Slack MCP partner app setup | ✅ Done — Validated 2026-06-29 |
| Testing & iteration | 1 week | Sample queries, golden dataset | 🟡 In progress |

**Deliverable:** Agent that produces daily FinOps briefings, answers ad-hoc cost questions, and delivers via Slack.

### Phase 2: Multi-Agent with Ticketing (4-8 weeks)

**Objective:** Automated anomaly → triage → ticket → notify pipeline.

| Task | Effort | Prerequisites |
|------|--------|---------------|
| Add Atlassian MCP Server | 1 week | Jira Cloud, OAuth 2.1 setup |
| Add PagerDuty MCP Server | 3 days | PagerDuty account, API token |
| Build orchestrator workflow logic | 2-3 weeks | Workflow definitions, routing rules |
| Human-in-the-loop approval gates | 1-2 weeks | Approval process definition |
| Integration testing | 1-2 weeks | End-to-end test scenarios |

**Deliverable:** Anomalies automatically create Jira tickets, notify via Slack, escalate via PagerDuty based on severity.

### Phase 3: Remediation Loop (8-16 weeks)

**Objective:** Agent proposes infrastructure changes and creates PRs.

| Task | Effort | Prerequisites |
|------|--------|---------------|
| Add Terraform MCP Server | 1 week | TFE token, workspace config |
| Add GitHub MCP Server | 3-5 days | GitHub token, repo access |
| Build safety guardrails | 2-3 weeks | Approve-before-apply, dry-run |
| Connect observability for impact validation | 2-3 weeks | Monitoring integration |
| Pilot with low-risk resources | 4-6 weeks | Selected non-prod workloads |

**Deliverable:** Agent creates PRs for rightsizing changes, validates with Terraform plan, awaits human approval.

### Phase 4: Policy-Aware Governance (Ongoing)

**Objective:** RAG over corporate policies for grounded recommendations.

| Task | Effort | Prerequisites |
|------|--------|---------------|
| Deploy vector database | 1-2 weeks | Pinecone/Weaviate/pgvector |
| Build document ingestion pipeline | 2-3 weeks | Policy documents collected |
| Create custom RAG MCP server | 2-3 weeks | MCP SDK, embeddings model |
| Connect to Cloudability context | 1 week | Business dimension mapping |
| Policy versioning & conflict resolution | Ongoing | Governance team input |

**Deliverable:** All recommendations validated against live corporate policies before surfacing to users.

---

## 9. Critical Assumptions We Are NOT Making

1. **We are NOT assuming Cloudability MCP has an event/webhook system** for proactively triggering agents. Current tools are pull-based. A cron-triggered agent simulates push, but true event-driven architecture may require Cloudability's notification system + a webhook receiver.

2. **We are NOT assuming Terraform MCP can `apply` without explicit enablement.** `ENABLE_TF_OPERATIONS=true` is required and disabled by default for safety.

3. **We are NOT assuming Slack MCP supports bidirectional approval workflows.** Posting is confirmed; event-driven response handling (human approves in Slack → agent proceeds) likely requires Slack Bolt framework, not just MCP.

4. **We are NOT assuming all MCP servers compose in a single runtime** without configuration. Each needs its own auth tokens, and the orchestrator must be configured to route to all of them.

5. **We are NOT assuming Cloudability MCP exposes real-time data.** Billing data typically has 24-48h latency. Forecasts may be more current but need validation.

6. **We are NOT assuming Cloudability MCP covers RI/SP purchase recommendations.** Rightsizing is confirmed; commitment purchase advisory needs investigation.

---

## 10. Open Questions for Validation

| # | Question | Who Owns Answer | Priority |
|---|----------|----------------|----------|
| 1 | Does Cloudability MCP expose commitment/reservation utilization and purchase recommendations? | Cloudability product team | High |
| 2 | What are the API rate limits for Cloudability MCP tools? | Cloudability support | High |
| 3 | Can Cloudability anomaly subscriptions trigger a webhook (not just email/PagerDuty)? | Cloudability product team | High |
| 4 | What is the data freshness SLA for `cldy_cost_report_run`? | Cloudability support | Medium |
| 5 | Does FOCUS-format data pass through the MCP dimension catalog? | Cloudability product team | Medium |
| 6 | What is Atlassian MCP's rate limit for bulk ticket creation? | Atlassian docs | Medium |
| 7 | Can Terraform MCP's `apply` be scoped to specific resource types for safety? | HashiCorp docs | Medium |
| 8 | What orchestration framework best supports persistent multi-MCP workflows with state? | Engineering team evaluation | Low |

---

## 11. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Agent makes incorrect cost attribution | Medium | High | Human-in-the-loop for all actions; read-only default |
| Terraform apply breaks production | Low | Critical | `ENABLE_TF_OPERATIONS` off by default; plan-only until Phase 3 |
| Stale data leads to wrong recommendations | Medium | Medium | Always show data timestamps; validate against real-time metrics |
| MCP server auth token rotation causes outage | Low | Medium | Token monitoring; centralized secrets management |
| Agent hallucination on dimension names | Low | Low | Cloudability's `cldy_cost_measures_list` provides exact valid options |
| Slack notification fatigue | Medium | Medium | Configurable thresholds; digest mode vs. real-time |

---

## 12. Next Steps

1. **Validate** open questions (Section 10) with Cloudability product/support team
2. **Pilot** Phase 1 using current Kiro CLI + Cloudability MCP + Slack MCP
3. **Demo** daily standup workflow to stakeholders for buy-in
4. **Evaluate** orchestration frameworks (LangGraph vs CrewAI vs Bedrock vs ADK)
5. **Define** escalation policies and approval authorities for Phase 2+

---

## Appendix A: Tool Inventory

### Cloudability MCP — Full Tool List

| Category | Tools |
|----------|-------|
| Cost Reports | `cldy_cost_report_run`, `cldy_cost_report_enqueue`, `cldy_cost_report_results`, `cldy_cost_report_state`, `cldy_cost_reports_list` |
| Measures & Filters | `cldy_cost_measures_list`, `cldy_cost_filters_list` |
| Anomalies | `cldy_anomalies_list`, `cldy_anomaly_get` |
| Anomaly Subscriptions | `cldy_anomaly_subscription_create`, `_get`, `_update`, `_delete`, `cldy_anomaly_subscriptions_list` |
| Budgets | `create_budget`, `get_budget`, `list_budgets`, `update_budget`, `delete_budget` |
| Budget Subscriptions | `cldy_budget_subscription_create`, `_get`, `_update`, `_delete`, `cldy_budget_subscriptions_list` |
| Rightsizing | `cldy_rightsizing_list`, `cldy_rightsizing_delete` |
| Forecasting | `cldy_forecast_get`, `cldy_estimate_get` |
| Views | `create_view`, `get_view`, `list_views`, `update_view`, `delete_view` |
| Business Dimensions | `create_business_dimension`, `update_business_dimension`, `delete_business_dimension`, `list_business_mappings`, `get_business_mapping` |
| Business Metrics | `cldy_business_metric_create`, `_get`, `_update`, `_delete`, `cldy_business_metrics_list` |
| Account Groups | `create_account_group`, `get_account_group`, `list_account_groups`, `update_account_group`, `delete_account_group` |
| Users & Permissions | `list_users`, `get_user`, `update_user`, `views_get_for_user`, `views_get_for_multiple_users` |
| Containers | `cldy_containers_clusters_list`, `cldy_containers_cluster_deployment`, `cldy_containers_provision`, `cldy_containers_usage`, `cldy_containers_labels`, `cldy_containers_counts` |

### External MCP Servers

| Server | URL | Version |
|--------|-----|---------|
| Atlassian Rovo | github.com/atlassian/atlassian-mcp-server | Latest (82 commits) |
| Slack | Official (partner app integration) | GA |
| PagerDuty | github.com/PagerDuty/pagerduty-mcp-server | PyPI published |
| Terraform | github.com/hashicorp/terraform-mcp-server | v1.0.0 GA |
| GitHub | github.com/github/github-mcp-server | Latest |

---

## Appendix B: References

1. [Google Dev — The Future of Cloud Governance: Building a Proactive Billing Agent](https://discuss.google.dev/t/the-future-of-cloud-governance-building-a-proactive-billing-agent-with-agent-platform/369751)
2. [Google Cloud — FinOps Agent MVP (GitHub)](https://github.com/GoogleCloudPlatform/professional-services/tree/main/examples/FinOps-agent)
3. [AWS — Build a FinOps Agent Using Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/build-a-finops-agent-using-amazon-bedrock-with-multi-agent-capability-and-amazon-nova-as-the-foundation-model/)
4. [Finout — Introducing Finout's MCP Integration](https://www.finout.io/blog/introducing-finouts-mcp-integration)
5. [Atlassian MCP Server](https://github.com/atlassian/atlassian-mcp-server)
6. [Slack MCP Guide](https://slack.com/help/articles/48855576908307)
7. [PagerDuty MCP Server](https://github.com/PagerDuty/pagerduty-mcp-server)
8. [HashiCorp Terraform MCP Server](https://github.com/hashicorp/terraform-mcp-server)
9. [GitHub MCP Server](https://github.com/github/github-mcp-server)
10. [Microsoft — Orchestrating Multi-Agent Intelligence: MCP-Driven Patterns](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/orchestrating-multi-agent-intelligence-mcp-driven-patterns-in-agent-framework/4462150)
