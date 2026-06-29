# Cloudability Project Rules

## Environment
- This is a Python project using `uv` for dependency management
- Python 3.10+ required
- Dashboard generator lives in `dashboards/` subdirectory
- Run `cd dashboards && uv sync` before any Python operations

## Commands
- Generate dashboards: `cd dashboards && uv run cldy-dash {executive|multicloud|containers|checkin}`
- Verify imports: `cd dashboards && uv run python -c "import cloudability_dashboards"`
- Run CLI help: `cd dashboards && uv run cldy-dash --help`

## API Credentials
- Requires: CLOUDABILITY_OPEN_TOKEN and CLOUDABILITY_ENVIRONMENT_ID
- Never hardcode tokens in source files
- Use environment variables or dashboards/.env file
- If you get HTTP 401 errors, the token has expired — ask the user for a new one

## Code Style
- Type hints on all functions
- httpx for HTTP calls (not requests, not urllib)
- Jinja2 for HTML templating
- Try/except around every API call with graceful degradation
- No Node.js, no npm, no subprocess spawning

## Architecture
- `dashboards/src/cloudability_dashboards/client.py` — shared API client
- `dashboards/src/cloudability_dashboards/generators/` — one file per dashboard
- `dashboards/src/cloudability_dashboards/templates/` — Jinja2 HTML templates
- All templates extend `base.html.j2` (dark theme, Chart.js, tabs)
