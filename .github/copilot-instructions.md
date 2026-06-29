# Copilot Instructions — Cloudability FinOps Toolkit

This repository contains the Cloudability FinOps dashboard generator and AI assistant skills.

## Project Structure
- `dashboards/` — Python project (uv-managed) that generates HTML dashboards
- `skills/` — Kiro CLI skill definitions
- `.bob/` — IBM Bob skills and rules
- `mcp/` — MCP server config templates

## Setup
```bash
cd dashboards && uv sync
export CLOUDABILITY_OPEN_TOKEN="your-token"
export CLOUDABILITY_ENVIRONMENT_ID="your-env-id"
```

## Commands
- `uv run cldy-dash executive` — Executive dashboard
- `uv run cldy-dash multicloud` — Multi-cloud architecture
- `uv run cldy-dash containers` — Kubernetes containers
- `uv run cldy-dash checkin` — Daily standup markdown

## Conventions
- Python 3.10+, type hints, httpx for HTTP, Jinja2 for templates
- No Node.js dependencies
- Every API call wrapped in try/except
- Templates extend `base.html.j2`
- Self-contained HTML output with Chart.js CDN
