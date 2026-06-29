# Agentic FinOps — System Architecture

## Design Principles

1. **MCP-native** — All integrations use the Model Context Protocol. No custom API wrappers.
2. **Read-first, act-second** — Agents default to read-only operations. Write actions require explicit enablement.
3. **Human-in-the-loop** — No infrastructure changes without human approval. Slack/Jira serve as approval gates.
4. **Composable** — Each MCP server is independent. Add/remove servers without changing the orchestrator.
5. **Pull-based** — Agents are triggered on-demand or via cron. No event-driven triggering (Cloudability MCP is pull-only).

---

## Layer Architecture (Adapted from Google's 5-Layer Model)

### Layer 5: Data Foundation — Cloudability MCP

The data layer is fully managed by Cloudability. No ETL, no BigQuery exports, no schema maintenance.

**Capabilities:**
- Cost reporting with arbitrary dimensions/metrics/filters
- Container/Kubernetes allocation (Kubecost integration)
- Business dimensions for custom allocation
- Tag normalization across cloud providers
- RI/SP portfolio management and recommendations

**Key advantage over Google's approach:** Zero data engineering. The hardest layer is pre-built.

### Layer 4: Context & Governance

**Available now:**
- Budget tracking and thresholds (Cloudability)
- Business metrics / unit economics (Cloudability)
- Account groups / org hierarchy (Cloudability)
- Governance policies (Cloudability)
- Tag compliance rules (Cloudability)

**Gap — requires custom build:**
- Corporate policy RAG (vector DB + doc ingestion)
- Compliance rule enforcement beyond tags

### Layer 3: Action & Execution

**Available now:**
- Anomaly detection and alerting (Cloudability)
- Rightsizing recommendations (Cloudability, multi-vendor)
- Budget alert management (Cloudability)
- Forecast/estimate generation (Cloudability)

**Available via external MCP servers:**
- Jira ticket creation (Atlassian MCP)
- Slack notifications (Slack MCP)
- PagerDuty incidents (PagerDuty MCP)
- Terraform plan/apply (Terraform MCP, disabled by default)
- GitHub PRs (GitHub MCP)

**Gap:**
- Direct infrastructure remediation (must go through Terraform)
- Commitment purchase execution (advisory only)

### Layer 2: Multi-Agent Core

**Current implementation:** Kiro CLI with specialized sub-agents defined via prompt templates.

**Agent roster:**
| Agent | Responsibility | Primary MCP Tools |
|-------|---------------|-------------------|
| Cost Analyst | Spend analysis, trend detection, drill-downs | `run_cost_report`, `search_dimension_values` |
| Anomaly Triage | Detect, classify, assign anomalies | `list_anomalies`, `get_anomaly`, `run_cost_report` |
| Rightsizing | Surface and prioritize optimization recs | `get_rightsizing_recommendations` |
| Forecast & Budget | Projected spend, budget health | `cldy_forecast_get`, `list_budgets` |
| Operations | RI portfolio, data freshness, governance | `get_ri_portfolio_summary`, `get_data_freshness_summary` |
| Orchestrator | Merge findings, prioritize actions, deliver | All tools (routing) |

### Layer 1: Interaction

**Current:** Kiro CLI (chat interface) + Slack (delivery channel)

**Planned:**
- Slack bidirectional (post reports + receive approval reactions)
- Jira status transitions as approval gates
- Email digest (via Slack or direct)

---

## Data Flow: Daily Standup

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│ Cron / User │────▶│  Orchestrator    │────▶│   Slack     │
│  Trigger    │     │                  │     │  Channel    │
└─────────────┘     │  1. Cost report  │     └─────────────┘
                    │  2. Anomalies    │
                    │  3. Rightsizing  │
                    │  4. Budgets     │
                    │  5. Format       │
                    │  6. Post         │
                    └──────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Cloudability │
                    │   MCP API   │
                    └─────────────┘
```

## Data Flow: Anomaly Triage (Phase 2)

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Anomaly    │────▶│  Triage Agent    │────▶│    Jira     │
│  Detected   │     │                  │     │   Ticket    │
└─────────────┘     │  1. Get anomaly  │     └─────────────┘
                    │  2. Drill down   │            │
                    │  3. Check recs   │            ▼
                    │  4. Classify     │     ┌─────────────┐
                    │  5. Create ticket│     │   Slack     │
                    │  6. Notify       │     │  #alerts    │
                    └──────────────────┘     └─────────────┘
                           │                       │
                    ┌──────▼──────┐         ┌──────▼──────┐
                    │ Cloudability │         │  PagerDuty  │
                    │   MCP API   │         │ (if critical)│
                    └─────────────┘         └─────────────┘
```

---

## Integration Patterns

### Pattern: Post Report to Slack

```
1. Generate report data via Cloudability MCP tools
2. Format as Slack Block Kit message (sections, dividers, context)
3. POST to Slack API via bot token with channel ID
4. Confirm delivery (check `ok: true` in response)
```

### Pattern: Anomaly → Ticket

```
1. list_anomalies (filter by date, state)
2. For each new anomaly:
   a. get_anomaly (full details)
   b. run_cost_report (drill into root cause)
   c. get_rightsizing_recommendations (check if actionable)
   d. Create Jira ticket (Atlassian MCP)
   e. Post summary to Slack
   f. If severity > threshold → PagerDuty incident
```

### Pattern: Budget Breach Prevention

```
1. cldy_forecast_get (projected spend)
2. Compare forecast vs budget thresholds
3. If projected > threshold:
   a. run_cost_report (top cost drivers)
   b. get_rightsizing_recommendations (potential savings)
   c. Create action plan
   d. DM budget owner via Slack
```

---

## Security Model

- **No secrets in this repo** — Tokens, channel IDs, and workspace details are in local MCP config only
- **Read-only default** — All Cloudability operations are read-only. Write operations (create view, update budget) are explicit.
- **Terraform gated** — `ENABLE_TF_OPERATIONS=true` must be explicitly set. Default is plan-only.
- **Bot scopes minimal** — Slack bot uses `chat:write` only (no message reading, no admin)
- **Token rotation** — OpenTokens expire. System must handle 401 gracefully and prompt for refresh.

---

## Configuration Requirements

Each deployment needs these configured in the MCP settings (local, not in repo):

| Variable | Purpose |
|----------|---------|
| `CLOUDABILITY_OPEN_TOKEN` | Cloudability API access |
| `CLOUDABILITY_ENVIRONMENT_ID` | Target environment |
| `SLACK_MCP_XOXB_TOKEN` | Slack bot token for posting |
| Slack channel ID | Target channel for reports (configured per-deployment) |

Phase 2 will additionally need:
- Atlassian OAuth 2.1 credentials
- PagerDuty API token
- Terraform Enterprise token (Phase 3)

---

## Comparison: Cloudability MCP vs Alternatives

| Dimension | Google (BigQuery MCP) | AWS Bedrock | Cloudability MCP |
|-----------|----------------------|-------------|-----------------|
| Data engineering required | High (billing exports, schema) | Medium (CloudFormation) | **None** |
| Multi-cloud | Must ingest each | AWS only | AWS, Azure, GCP, OCI native |
| Hallucination risk | Higher (NL2SQL) | Low | **Low** (discoverable params) |
| Governance built-in | Must build | Minimal | Views, business dims, budgets |
| Unit economics | Must build | None | ✅ Business metrics |
| Setup time | Weeks | Days | **Hours** (already configured) |
