# AGENTS.md — Cloudability FinOps Toolkit

This repo contains IBM Cloudability FinOps tooling: dashboard generators, MCP server integration, and AI assistant skills.

## Quick Start

```bash
# 1. Install the dashboard generator
cd dashboards && uv sync

# 2. Set credentials
export CLOUDABILITY_OPEN_TOKEN="your-opentoken"
export CLOUDABILITY_ENVIRONMENT_ID="your-env-id"

# 3. Generate any dashboard
uv run cldy-dash executive     # Executive FinOps dashboard
uv run cldy-dash multicloud    # Multi-cloud architecture breakdown
uv run cldy-dash containers    # Kubernetes container costs
uv run cldy-dash checkin       # Daily standup report (markdown)
```

Or run the one-liner: `./setup.sh`

## Repository Layout

```
├── AGENTS.md              ← You are here (universal AI agent instructions)
├── dashboards/            ← Python project: all dashboard generators
│   ├── pyproject.toml     (dependencies: httpx, jinja2)
│   └── src/cloudability_dashboards/
│       ├── client.py      (Cloudability V3 API client — direct HTTP)
│       ├── cli.py         (cldy-dash CLI entry point)
│       ├── generators/    (executive, multicloud, containers, checkin)
│       └── templates/     (Jinja2 HTML templates, shared dark theme)
├── skills/                ← Kiro CLI skill definitions
│   ├── cldy/             (MCP context loader)
│   ├── execdash/         (executive dashboard trigger)
│   ├── archdash/         (multi-cloud dashboard trigger)
│   ├── containersdash/   (container dashboard trigger)
│   └── dailycheckin/     (daily standup trigger)
├── .bob/                  ← IBM Bob skills + rules
├── .github/               ← GitHub Copilot instructions
├── mcp/                   ← MCP server config templates (per-tool)
└── setup.sh              ← One-command bootstrap
```

## MCP Server: cldy-mcp-local

The Cloudability MCP server (`cldy-mcp-local`) provides live data access for interactive queries. Install it:

```bash
uv tool install cldy-mcp-local  # From wheel or PyPI
```

Environment variables required:
- `CLOUDABILITY_OPEN_TOKEN` — API opentoken (expires periodically)
- `CLOUDABILITY_ENVIRONMENT_ID` — Target environment UUID

See `mcp/` directory for config templates for your specific tool (Bob, Claude, Kiro, Cursor, etc.).

## Dashboard Generator (dashboards/)

A single Python project that generates all dashboards via direct Cloudability V3 API calls.

- **Language**: Python 3.10+
- **Dependencies**: httpx, jinja2 (installed via `uv sync`)
- **No MCP dependency**: Calls the API directly, no subprocess spawning
- **Output**: Self-contained HTML files with Chart.js CDN

### Commands

| Command | Output | Description |
|---------|--------|-------------|
| `cldy-dash executive` | `output/executive_dashboard.html` | MTD spend, trends, rightsizing, anomalies, budgets |
| `cldy-dash multicloud` | `output/multicloud_dashboard.html` | Vendor split, IaaS/PaaS/AI classification, chip architecture |
| `cldy-dash containers` | `output/container_dashboard.html` | Cluster costs, idle analysis, Kubecost efficiency |
| `cldy-dash checkin` | stdout (markdown) | Priority actions, spend snapshot, optimization pipeline |

## Cloudability API

- **Base URL**: `https://api.cloudability.com`
- **Auth headers**: `apptio-opentoken`, `apptio-environmentid`
- **Key endpoints**:
  - `GET /v3/reporting/cost/run` — Cost reports (dimensions, metrics, filters)
  - `GET /v3/reporting/usage/run` — Usage reports
  - `GET /v3/kubecost/model/allocation` — Kubernetes cost allocation
  - `GET /v3/rightsizing/{vendor}/{service}` — Rightsizing recommendations
  - `GET /v3/anomalies` — Spending anomalies
  - `GET /v3/budgets` — Budget tracking

## Code Conventions

- Python: type hints, pathlib over os.path, httpx for HTTP
- Templates: Jinja2 with shared `base.html.j2`, Chart.js for charts
- HTML: Self-contained, dark theme, no external dependencies beyond Chart.js CDN
- Error handling: Every API call wrapped in try/except, graceful degradation

## Do Not

- Do not hardcode API tokens in any file
- Do not modify `client.py` API endpoints without checking Cloudability V3 docs
- Do not add Node.js dependencies — this project is Python-only
- Do not commit `.env` files or output HTML files
