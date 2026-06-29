# cloudability-dashboards

Unified Python project for generating Cloudability FinOps dashboards. Replaces the previous Node.js dashboard generators with a single, standardized Python implementation.

## What it generates

| Command | Output | Description |
|---------|--------|-------------|
| `cldy-dash executive` | `output/executive_dashboard.html` | Executive cloud cost summary with MTD spend, trends, rightsizing, anomalies, budgets |
| `cldy-dash multicloud` | `output/multicloud_dashboard.html` | Multi-cloud architecture breakdown: vendor split, IaaS/PaaS/AI classification, chip architecture |
| `cldy-dash containers` | `output/container_dashboard.html` | Kubernetes container cost dashboard with idle analysis, cluster costs, efficiency metrics |
| `cldy-dash checkin` | stdout (markdown) | Daily FinOps standup report with priority actions, anomalies, optimization pipeline |

## Architecture

```
cloudability-dashboards/
├── pyproject.toml                          # Single dependency manifest
├── src/cloudability_dashboards/
│   ├── client.py                           # Direct Cloudability V3 API client (httpx)
│   ├── classifications.py                  # Service → IaaS/PaaS/AI, instance → chip arch
│   ├── cli.py                              # CLI entry point (cldy-dash command)
│   ├── generators/
│   │   ├── executive.py                    # Executive dashboard generator
│   │   ├── multicloud.py                   # Multi-cloud architecture generator
│   │   ├── containers.py                   # Container cost generator
│   │   └── checkin.py                      # Daily check-in (markdown)
│   └── templates/
│       ├── base.html.j2                    # Shared dark theme, Chart.js, tab structure
│       ├── executive.html.j2               # Executive dashboard template
│       ├── multicloud.html.j2              # Multi-cloud template
│       └── containers.html.j2             # Container template
└── output/                                 # Generated files land here
```

## Design Principles

- **One language**: Python everywhere. No Node.js, no subprocess spawning.
- **Direct API calls**: Uses httpx to call Cloudability V3 API directly. No MCP server dependency for generation.
- **Shared templates**: Jinja2 base template provides consistent dark theme, Chart.js CDN, responsive layout.
- **Minimal dependencies**: Only `httpx` + `jinja2`. That's it.
- **Self-contained output**: Each generated HTML file is standalone with embedded data and CDN chart library.

## Setup

```bash
cd cloudability-dashboards
uv sync

# Set credentials
export CLOUDABILITY_OPEN_TOKEN="your-token"
export CLOUDABILITY_ENVIRONMENT_ID="your-env-id"

# Or copy .env.example to .env and fill in
cp .env.example .env
```

## Usage

```bash
# Generate and open a specific dashboard
uv run cldy-dash executive
uv run cldy-dash containers
uv run cldy-dash multicloud

# Daily standup (prints markdown to stdout)
uv run cldy-dash checkin
uv run cldy-dash checkin --json    # JSON output for programmatic use

# Or if installed as a tool:
cldy-dash executive
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CLOUDABILITY_OPEN_TOKEN` | Yes | Cloudability API opentoken |
| `CLOUDABILITY_ENVIRONMENT_ID` | Yes | Cloudability environment UUID |
| `OUTPUT_DIR` | No | Override output directory (default: `./output/`) |

## Relationship to cldy-mcp-local

This project generates dashboards by calling the Cloudability API directly. It does NOT depend on or spawn `cldy-mcp-local`.

`cldy-mcp-local` remains the MCP server for interactive Kiro CLI queries. This project is for batch dashboard generation.

## Replaces

- ~~`cloudability-executive-dashboard/`~~ (Node.js)
- ~~`cloudability-multicloud-dashboard/`~~ (Node.js)
- ~~`cloudability-dailycheckin/`~~ (Node.js)
- ~~Container dashboard inline generation~~ (now standardized)
