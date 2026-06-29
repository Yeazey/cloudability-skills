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

## Architecture Reference

Read `/Users/kingyeazey/.kiro/skills/cldy/ARCHITECTURE.md` for design decisions, rationale, and how the system works together.

## MCP Servers (3 configured, 1 primary)

### 1. `cldy-mcp-local` — **PRIMARY** ⭐
- **Binary**: `/Users/kingyeazey/.local/bin/cldy-mcp-local`
- **Package**: `cldy_mcp_local-0.2.0` (installed via `uv tool install` from `~/Downloads/cldy-mcp-local/`)
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
- **Why primary**: Unified server covering ALL Cloudability domains including Kubecost container allocation. Replaces both the Node.js and Python MCP servers for day-to-day queries.

### 2. Node.js MCP — `cloudability` (legacy, still available)
- **Path**: `/Users/kingyeazey/Projects/bob/cldy-mcp-server-main/`
- **Runtime**: Node.js
- **Covers**: Cost reporting, views, budgets, anomalies, business mappings, rightsizing, forecasts, estimates, account groups, users
- **Config**: `~/.kiro/settings/mcp.json` → `cloudability` entry
- **Key tools**: `cldy_cost_report_run`, `cldy_cost_report_enqueue`, `list_views`, `list_budgets`, `cldy_anomalies_list`, `cldy_rightsizing_list`, `cldy_forecast_get`
- **Note**: No longer required for dashboard generation. Only kept for reference. Use `cldy-mcp-local` for all interactive queries.

### 3. Python MCP — `cloudability-containers` (legacy, limited)
- **Path**: `/Users/kingyeazey/Projects/bob/cloudability-mcp-server-python/`
- **Runtime**: Python 3.14+ via `uv`
- **Covers**: Budget management, account listing, estimates, forecasts
- **Config**: `~/.kiro/settings/mcp.json` → `cloudability-containers` entry
- **Note**: The container-specific endpoints (clusters, usage, labels) are **410 Gone**. Use `cldy-mcp-local` `get_kubecost_workload_costs` for container data instead.

## Environments

Reference doc: `/Users/kingyeazey/cloudability-env-keys.md`

| Environment | Env ID | Status | Notes |
|-------------|--------|--------|-------|
| **cldydemo.main** | `YOUR_ENVIRONMENT_ID` | **Active** | Full demo data, 50+ K8s clusters, multi-cloud |
| **mhmmercy.com** | `YOUR_ENVIRONMENT_ID` | Inactive | Azure-only, no container provisioning |

### To Switch Environments
1. Update `CLOUDABILITY_OPEN_TOKEN` and `CLOUDABILITY_ENVIRONMENT_ID` in `~/.kiro/settings/mcp.json` (all MCP entries: `cldy-mcp-local`, `cloudability`, and `cloudability-containers`)
2. Update `~/cloudability-env-keys.md` to mark active env
3. Restart Kiro CLI

### Token Notes
- Opentokens expire — if you get `401 unauthorized / invalid opentoken`, ask the user for a new one
- All MCP servers use the same token + env ID
- `cldy-mcp-local` uses env var `CLOUDABILITY_OPEN_TOKEN` (with underscore), Node.js uses `CLOUDABILITY_OPENTOKEN` (no underscore)

## GitHub Repos

| Repo | What | Local Path |
|------|------|-----------|
| `Yeazey/cloudability-kiro-skills` | All Kiro skills (cldy, execdash, archdash, containersdash, dailycheckin) | `~/.kiro/skills/` |
| `Yeazey/executive_cloud_summary_CLDYMCP` | Executive dashboard project | `~/cloudability-executive-dashboard/` |
| `Yeazey/Arch_Dash_CLDYMCP` | Multi-cloud architecture dashboard project | `~/cloudability-multicloud-dashboard/` |
| `Yeazey/kubernetes-container-cost-dashboard` | Container cost dashboard + HTML | `~/container-dashboard.html` |
| `Yeazey/FinOps_Checkin_CLDYMCP` | Daily check-in multi-agent project | `~/cloudability-dailycheckin/` |
| `Yeazey/cloudability-dashboards` (TBD) | Unified Python dashboard generators | `~/cloudability-dashboards/` |

## Available Skills (4)

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `/execdash` | exec dashboard, cloud cost summary | Generates executive dashboard via `cldy-dash executive` |
| `/archdash` | multi-cloud, architecture, chip breakdown | Generates multi-cloud dashboard via `cldy-dash multicloud` |
| `/containersdash` | container dashboard, k8s costs, idle resources | Generates container dashboard via `cldy-dash containers` |
| `/dailycheckin` | daily checkin, finops standup | Runs daily standup via `cldy-dash checkin` |

## Projects & What They Do

### 0. Unified Dashboard Project (NEW)
- **Path**: `/Users/kingyeazey/cloudability-dashboards/`
- **Run**: `cd ~/cloudability-dashboards && uv run cldy-dash {executive|multicloud|containers|checkin}`
- **What it does**: Single Python project that generates all dashboards via direct Cloudability API calls
- **Architecture**: `client.py` (direct httpx HTTP) → `generators/*.py` (data collection + processing) → `templates/*.html.j2` (Jinja2 rendering) → `output/*.html`
- **Dependencies**: httpx, jinja2 (installed via uv sync)
- **Replaces**: All 3 Node.js dashboard projects + inline container generation

### 1. Executive Dashboard (`/execdash`)

> **⚠️ DEPRECATED**: Replaced by the unified Python project at `~/cloudability-dashboards/`. See section 0.

- **Path**: `/Users/kingyeazey/cloudability-executive-dashboard/`
- **GitHub**: `Yeazey/executive_cloud_summary_CLDYMCP`
- **Run**: `cd cloudability-executive-dashboard && npm run generate`
- **Output**: `output/executive_dashboard.html` → auto-opens in Chrome
- **What it shows**:
  - MTD spend by team (using Product Hierarchy view `1706692`)
  - Month-over-month trends and 12-month history
  - Rightsizing recommendations summary
  - Anomaly highlights
  - Budget status and at-risk budgets
  - AI/ML spend section
  - Commitment coverage and savings
- **Data source**: Node.js MCP (`cldy_cost_report_run`, `cldy_rightsizing_list`, `cldy_anomalies_list`, `cldy_forecast_get`, `list_budgets`). For interactive queries outside the dashboard, use `cldy-mcp-local` equivalents: `run_cost_report`, `get_rightsizing_recommendations`, `list_anomalies`.
- **Architecture**: `data-collector.mjs` pulls data → `insight-engine.mjs` analyzes → `dashboard-generator.mjs` builds HTML

### 2. Multi-Cloud Architecture Dashboard (`/archdash`)

> **⚠️ DEPRECATED**: Replaced by the unified Python project at `~/cloudability-dashboards/`. See section 0.

- **Path**: `/Users/kingyeazey/cloudability-multicloud-dashboard/`
- **Run**: `cd cloudability-multicloud-dashboard && npm run generate`
- **Output**: `output/multicloud_architecture_dashboard.html`
- **What it shows**:
  - Cloud provider breakdown (AWS, Azure, OCI, GCP, Snowflake, Databricks, MongoDB) with cost & %
  - Service type classification: IaaS, PaaS, Containers, AI/ML, Other
  - Chip architecture breakdown: Intel, AMD, Graviton (ARM), NVIDIA GPU, ARM (Ampere)
- **Data source**: Node.js MCP (`cldy_cost_report_run` by `enhanced_service_name`, `instance_type`). For interactive queries, use `cldy-mcp-local` `run_cost_report`.
- **Architecture**: `collector.mjs` pulls data → `classifications.mjs` maps services/instances to categories → `generate.mjs` builds HTML

### 3. Daily Check-in (`/dailycheckin`)

> **⚠️ DEPRECATED**: Replaced by the unified Python project at `~/cloudability-dashboards/`. See section 0.

- **Path**: `/Users/kingyeazey/cloudability-dailycheckin/`
- **Run**: `node src/main.mjs --json` (for markdown-in-chat formatting)
- **What it produces**: Multi-agent FinOps standup report with:
  - Priority actions ranked by cost-of-inaction
  - Spend snapshot (MTD, daily rate, projection)
  - Provider breakdown and WoW movers
  - Anomaly triage
  - Rightsizing pipeline and staleness
  - Budget health
  - FinOps maturity scoring
  - Meeting recommendations
- **Data source**: Node.js MCP (all tools). For follow-up queries in chat, use `cldy-mcp-local` tools directly.
- **Architecture**: 6 specialist agents (cost-analysis, anomaly-risk, optimization, forecast-budget, operations-strategy, actions-insights) + 1 orchestrator. Each agent has a prompt in `agents/`. The `collector.mjs` gathers data, agents process in parallel, orchestrator merges.

### 4. Container Cost Dashboard (`/containersdash`)

> **⚠️ DEPRECATED**: Replaced by the unified Python project at `~/cloudability-dashboards/`. See section 0.

- **Path**: `/Users/kingyeazey/container-dashboard.html`
- **GitHub**: `Yeazey/kubernetes-container-cost-dashboard`
- **Run**: Generated inline by skill (no npm project) — pulls data via MCP, builds HTML, opens in browser
- **What it shows**:
  - Overview: KPI cards, vendor donut (AWS/OCI), region bar chart, weekly trend
  - Top Clusters: ranked bar chart + table with vendor/region badges
  - Optimization: idle vs utilized stacked bar, top idle namespaces, $950K savings callout
  - KPIs: metrics cards, cost distribution, WoW changes
- **Data source**: `cldy-mcp-local` (`get_kubecost_workload_costs` for Kubecost allocation, `run_cost_report` with `container_cluster_name`, `container_namespace` dimensions for billing costs)
- **Status**: Use `get_kubecost_workload_costs` for workload-level/fairshare data; `run_cost_report` for billing-reconciled idle analysis
- **Design**: Dark gradient theme, Chart.js, 4 tabs, single self-contained HTML file

## Container Data Strategy

The Cloudability container endpoints (`/containers/clusters`, `/containers/usage`, etc.) are **deprecated (410 Gone)**. Use `cldy-mcp-local` for all container cost queries:

1. **Kubecost allocation** (`cldy-mcp-local`): Use `get_kubecost_workload_costs` with aggregate dimensions (cluster, namespace, pod, node, label, controller). Supports time windows like "7d", "30d", "month", "lastmonth". Returns fairshare-allocated costs with idle/efficiency metrics.
2. **Standard cost reports** (`cldy-mcp-local`): Use `run_cost_report` with `container_cluster_name` and `container_namespace` dimensions for billing-reconciled costs. The "IDLE RESOURCES" namespace represents idle cost.

**Rule of thumb**:
- Use `get_kubecost_workload_costs` for workload attribution, team chargeback, efficiency analysis, pod/label-level breakdowns
- Use `run_cost_report` with container dimensions for billing reconciliation, idle analysis, cluster-level totals

## Cost Report Quick Reference

### Common Dimensions
`vendor`, `enhanced_service_name`, `region`, `vendor_account_name`, `container_cluster_name`, `container_namespace`, `date`, `year_week`, `year_month`, `instance_type`, `lease_type`

### Common Metrics
`unblended_cost`, `total_amortized_cost`, `public_on_demand_cost`, `usage_quantity`, `usage_hours`

### Filter Syntax
`filters: ["dimension_name==value"]` — operators: `==`, `!=`, `>`, `<`, `>=`, `<=`

### Key View
- Product Hierarchy view ID: `1706692` (used by executive dashboard)

## Workflow Patterns

### End-of-Session Checklist
After any session that modifies the Cloudability system:
1. **Update ARCHITECTURE.md** — Add new decisions (D00X format) with date, rationale, tradeoffs
2. **Update SKILL.md** — If new tools, environments, projects, or workflows were added
3. **Update env-keys doc** — If tokens or environment IDs changed (`~/cloudability-env-keys.md`)
4. **Push to GitHub** — Any modified projects that have repos:
   - `Yeazey/executive_cloud_summary_CLDYMCP` (exec dashboard)
   - `Yeazey/kubernetes-container-cost-dashboard` (container dashboard + skill)
   - Create new repos for new projects as needed
5. **Commit skill changes** — If SKILL.md or ARCHITECTURE.md changed, note it for the user

### Standard Workflows
1. **Quick cost check**: Use `run_cost_report` (cldy-mcp-local) with dimensions/metrics
2. **Container analysis**: Use `get_kubecost_workload_costs` (cldy-mcp-local) for fairshare/workload costs, or `run_cost_report` with `container_cluster_name`/`container_namespace` for billing costs
3. **Dashboard generation**: `cldy-dash {executive|multicloud|containers|checkin}` — unified Python CLI, generates HTML → opens in browser
4. **Anomaly investigation**: `list_anomalies` (cldy-mcp-local) with date range and optional filters
5. **Rightsizing**: `get_rightsizing_recommendations` (cldy-mcp-local) for multi-vendor recommendations
6. **RI analysis**: `get_ri_portfolio_summary`, `list_ri_recommendations`, `get_ri_utilization` (cldy-mcp-local)
7. **Data freshness**: `get_data_freshness_summary`, `get_pipeline_failures` (cldy-mcp-local)
8. **New dashboard/tool**: Build it → create a skill → push to GitHub → update this doc
