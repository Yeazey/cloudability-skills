---
name: cldy
description: Load full Cloudability MCP context — environments, auth, tools, workflows, and architecture decisions. Use at session start or when working with any Cloudability data.
---

# Cloudability MCP Context

Load this skill at the start of any session involving Cloudability data. It provides full context on the MCP setup, environments, available tools, and established workflows.

## 🔥 Active Priority: Agentic FinOps

Read `/Users/kingyeazey/.kiro/skills/cldy/AGENTIC-FINOPS-PLAN.md` — this is the primary initiative. It defines the architecture for building a proactive, multi-agent FinOps system using Cloudability MCP + Slack + Jira + PagerDuty + Terraform MCP servers. Key context:

- **Google's 5-Layer Reference Architecture** adapted for Cloudability
- **4-Phase Roadmap**: Single-agent → Multi-agent ticketing → Remediation loop → Policy governance
- **5 Workflow Patterns**: Anomaly triage, budget breach prevention, monthly close, rightsizing pipeline, tagging governance
- **Capability gaps identified**: No event-driven triggers, no policy RAG, no infrastructure write-back (yet)
- **External MCP servers**: Atlassian, Slack, PagerDuty, Terraform, GitHub — all confirmed production-ready

When working on any Cloudability feature, consider how it fits into the Agentic FinOps roadmap.

### Slack Integration (VALIDATED ✅)

- **Workspace**: Configured in `~/.kiro/settings/mcp.json` → `slack` entry
- **Auth**: `SLACK_MCP_XOXB_TOKEN` env var (bot token, `xoxb-` prefix)
- **Scopes confirmed**: `chat:write` (can post), missing `channels:read` (cannot list channels)
- **Status**: Connected and posting successfully

To post to Slack:
```bash
SLACK_TOKEN=$(cat ~/.kiro/settings/mcp.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['mcpServers']['slack']['env']['SLACK_MCP_XOXB_TOKEN'])")
curl -s -X POST -H "Authorization: Bearer $SLACK_TOKEN" -H "Content-Type: application/json" \
  -d '{"channel":"YOUR_CHANNEL_ID","text":"message here"}' \
  "https://slack.com/api/chat.postMessage"
```

## Architecture Reference

Read `/Users/kingyeazey/.kiro/skills/cldy/ARCHITECTURE.md` for design decisions, rationale, and how the system works together.

## MCP Servers (3 configured, 1 primary)

### 1. `cldy-mcp-local` — **PRIMARY** ⭐
- **Binary**: `/Users/kingyeazey/.local/bin/cldy-mcp-local`
- **Package**: `cldy_mcp_local-0.2.0` (installed via `uv tool install`)
- **Runtime**: Python (FastMCP)
- **Config**: `~/.kiro/settings/mcp.json` → `cldy-mcp-local` entry
- **Auth env vars**: `CLOUDABILITY_OPEN_TOKEN`, `CLOUDABILITY_ENVIRONMENT_ID`
- **Covers**: Cost reporting, usage reporting, Kubecost container allocation, rightsizing, RI planning, RI portfolio, anomaly detection, governance, business mappings, data freshness, views, tags
- **Key tools**:
  - `run_cost_report` / `run_usage_report` — Cost and usage reporting
  - `get_kubecost_workload_costs` — Kubernetes cost allocation (cluster, namespace, pod, node, label)
  - `kubecost_list_windows` — List valid time windows for Kubecost queries
  - `get_rightsizing_recommendations` — Multi-vendor rightsizing (AWS, Azure, GCP, Containers)
  - `list_anomalies` / `get_anomaly` — Anomaly detection
  - `list_views` / `get_view` — View management
  - `list_business_dimensions` / `list_business_metrics` — Business mappings
  - `get_ri_portfolio_summary` / `get_ri_utilization` / `list_ri_recommendations` — RI management
  - `list_governance_policies` — Governance and compliance
  - `get_data_freshness_summary` / `get_pipeline_failures` — Data pipeline health
  - `list_tag_mappings` — Tag normalization rules
  - `search_dimension_values` — Dimension value lookup for filters
  - `list_cost_measures` / `list_usage_measures` — Available dimensions and metrics
- **Why primary**: Unified server covering ALL Cloudability domains including Kubecost container allocation.

### 2. Node.js MCP — `cloudability` (legacy, still available)
- **Runtime**: Node.js
- **Covers**: Cost reporting, views, budgets, anomalies, business mappings, rightsizing, forecasts, estimates, account groups, users
- **Note**: No longer required for dashboard generation. Use `cldy-mcp-local` for all interactive queries.

### 3. Python MCP — `cloudability-containers` (legacy, limited)
- **Runtime**: Python 3.14+ via `uv`
- **Covers**: Budget management, account listing, estimates, forecasts
- **Note**: The container-specific endpoints are **410 Gone**. Use `cldy-mcp-local` instead.

## Environments

Managed locally in `~/cloudability-env-keys.md`. Never commit env IDs or tokens to this repo.

### To Switch Environments
1. Update `CLOUDABILITY_OPEN_TOKEN` and `CLOUDABILITY_ENVIRONMENT_ID` in `~/.kiro/settings/mcp.json` (all MCP entries)
2. Update `~/cloudability-env-keys.md` to mark active env
3. Restart Kiro CLI

### Token Notes
- Opentokens expire — if you get `401 unauthorized / invalid opentoken`, ask the user for a new one
- All MCP servers use the same token + env ID
- `cldy-mcp-local` uses env var `CLOUDABILITY_OPEN_TOKEN` (with underscore), Node.js uses `CLOUDABILITY_OPENTOKEN` (no underscore)

## GitHub Repos

| Repo | What | Local Path |
|------|------|-----------|
| `Yeazey/cloudability-skills` | All Kiro skills (cldy, execdash, archdash, containersdash, dailycheckin, sprintplan) | `~/.kiro/skills/` |
| `Yeazey/cloudability-dashboards` | Unified Python dashboard generators | `~/cloudability-dashboards/` |

## Available Skills (5)

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `/execdash` | exec dashboard, cloud cost summary | Generates executive dashboard via `cldy-dash executive` |
| `/archdash` | multi-cloud, architecture, chip breakdown | Generates multi-cloud dashboard via `cldy-dash multicloud` |
| `/containersdash` | container dashboard, k8s costs, idle resources | Generates container dashboard via `cldy-dash containers` |
| `/dailycheckin` | daily checkin, finops standup | Runs daily standup via `cldy-dash checkin` |
| `/sprintplan` | sprint plan, monthly plan, what should we work on | Conversational FinOps sprint planning via `cldy-dash sprintplan` |

## Projects & What They Do

### 0. Unified Dashboard Project (CURRENT)
- **Path**: `/Users/kingyeazey/cloudability-dashboards/`
- **GitHub**: `Yeazey/cloudability-dashboards`
- **Run**: `cd ~/cloudability-dashboards && uv run cldy-dash {executive|multicloud|containers|checkin|sprintplan}`
- **What it does**: Single Python project that generates all dashboards via direct Cloudability API calls
- **Architecture**: `client.py` (direct httpx HTTP) → `generators/*.py` (data collection + processing) → `templates/*.html.j2` (Jinja2 rendering) → `output/*.html`
- **Dependencies**: httpx, jinja2 (installed via uv sync)
- **Commands**:
  - `cldy-dash executive` — Executive cost summary dashboard (HTML)
  - `cldy-dash multicloud` — Multi-cloud architecture dashboard (HTML)
  - `cldy-dash containers` — Kubernetes container cost dashboard (HTML)
  - `cldy-dash checkin [--json]` — Daily FinOps standup (markdown/JSON to stdout)
  - `cldy-dash sprintplan [--json]` — Sprint plan generator (markdown/JSON to stdout)

### 1. Sprint Planning Skill (`/sprintplan`)

- **Path**: `~/.kiro/skills/sprintplan/`
- **Files**: `SKILL.md` (workflow instructions) + `TEAM_CONTEXT.md` (customizable team config)
- **What it does**: Conversational FinOps sprint planning — collects live data, scores priorities, generates ranked backlog + meeting calendar + engagement plan
- **Data sources**: `run_cost_report`, `list_anomalies`, `get_rightsizing_recommendations`, `get_ri_portfolio_summary`, `get_kubecost_workload_costs`, `list_governance_policies`
- **Export options**: Slack, HTML dashboard, markdown file, Jira CSV
- **Key feature**: TEAM_CONTEXT.md allows each team to customize priority weights, stakeholders, KPI targets, sprint length, and recurring items
- **CLI**: `cd ~/cloudability-dashboards && uv run cldy-dash sprintplan --json`

### 2. Executive Dashboard (`/execdash`)
- **Tabs**: 📊 Overview | 🔧 Services | ⚡ Optimization | 📈 Trends
- **What it shows**: MTD spend, MoM trends, top accounts, services breakdown, rightsizing savings, anomalies, budgets, commitment coverage

### 3. Multi-Cloud Architecture Dashboard (`/archdash`)
- **Tabs**: ☁️ Providers | 🔧 Service Types | 🧮 Chip Architecture
- **What it shows**: Cloud provider breakdown, IaaS/PaaS/Containers/AI classification, chip architecture

### 4. Container Cost Dashboard (`/containersdash`)
- **Tabs**: 📊 Overview | 🏗️ Top Clusters | 📦 Namespaces | ⚡ Optimization | 📈 KPIs
- **What it shows**: Kubecost allocation, billing costs, idle analysis, vendor/region split, weekly trend, namespace breakdown

### 5. Daily Check-in (`/dailycheckin`)
- **What it produces**: Multi-agent FinOps standup report with priority actions, spend snapshot, anomaly triage, rightsizing pipeline, budget health

## Container Data Strategy

Use `cldy-mcp-local` for all container cost queries:

1. **Kubecost allocation**: `get_kubecost_workload_costs` — fairshare-allocated costs with idle/efficiency metrics
2. **Standard cost reports**: `run_cost_report` with `container_cluster_name` and `container_namespace` dimensions

## Cost Report Quick Reference

### Common Dimensions
`vendor`, `enhanced_service_name`, `region`, `vendor_account_name`, `container_cluster_name`, `container_namespace`, `date`, `year_week`, `year_month`, `instance_type`, `lease_type`

### Common Metrics
`unblended_cost`, `total_amortized_cost`, `public_on_demand_cost`, `usage_quantity`, `usage_hours`

### Filter Syntax
`filters: ["dimension_name==value"]` — operators: `==`, `!=`, `>`, `<`, `>=`, `<=`

## Workflow Patterns

### End-of-Session Checklist
1. **Update SKILL.md** — If new tools, environments, projects, or workflows were added
2. **Update env-keys doc** — If tokens or environment IDs changed (`~/cloudability-env-keys.md`)
3. **Push to GitHub** — `Yeazey/cloudability-skills` and `Yeazey/cloudability-dashboards`
4. **⚠️ Never push env IDs, tokens, or secrets to GitHub** — keep those in local files only

### Standard Workflows
1. **Quick cost check**: Use `run_cost_report` with dimensions/metrics
2. **Container analysis**: `get_kubecost_workload_costs` or `run_cost_report` with container dimensions
3. **Dashboard generation**: `cldy-dash {executive|multicloud|containers|checkin|sprintplan}`
4. **Anomaly investigation**: `list_anomalies` with date range and optional filters
5. **Rightsizing**: `get_rightsizing_recommendations` for multi-vendor recommendations
6. **RI analysis**: `get_ri_portfolio_summary`, `list_ri_recommendations`, `get_ri_utilization`
7. **Data freshness**: `get_data_freshness_summary`, `get_pipeline_failures`
8. **Sprint planning**: `/sprintplan` skill or `cldy-dash sprintplan --json`
