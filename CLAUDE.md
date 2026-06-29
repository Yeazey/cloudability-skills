# CLAUDE.md

See AGENTS.md for full project context. This file adds Claude Code-specific guidance.

## Project

Cloudability FinOps toolkit — dashboard generators (Python/Jinja2) + MCP integration skills.

## Setup

```bash
cd dashboards && uv sync
export CLOUDABILITY_OPEN_TOKEN="..."
export CLOUDABILITY_ENVIRONMENT_ID="..."
```

## Key Commands

- `uv run cldy-dash executive` — Generate executive dashboard
- `uv run cldy-dash multicloud` — Generate multi-cloud dashboard
- `uv run cldy-dash containers` — Generate container dashboard
- `uv run cldy-dash checkin` — Daily standup (markdown output)

## Architecture

`client.py` (httpx → Cloudability API) → `generators/*.py` (collect + process) → `templates/*.html.j2` (Jinja2 render) → `output/*.html`

## When Editing

- Run `cd dashboards && uv run python -c "import cloudability_dashboards"` to verify imports after changes
- Templates extend `base.html.j2` — edit the base for theme changes
- Each generator is self-contained: data collection + processing + template rendering
- Classifications (service→category, instance→chip) are in `generators/multicloud.py`

## Style

- Type hints on all functions
- Docstrings on public functions
- `_private_helper()` naming for internal functions
- Try/except around every API call with fallback defaults

## MCP Server

For interactive Cloudability queries in Claude, configure `cldy-mcp-local` in your Claude settings. See `mcp/claude.json` for the config template.
