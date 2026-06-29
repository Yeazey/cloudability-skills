---
name: execdash
description: Generate and open the Cloudability Executive Dashboard. Use when the user asks for their executive dashboard, exec dash, or cloud cost summary.
---

# Executive Dashboard

When triggered, run the executive dashboard generator and open it in Chrome:

```bash
cd /Users/kingyeazey/cloudability-dashboards && uv run cldy-dash executive
```

This project lives at `/Users/kingyeazey/cloudability-dashboards/` and is the unified Python dashboard CLI.

The dashboard:
- Connects to Cloudability MCP to pull live cost data
- Generates a self-contained HTML file at `output/executive_dashboard.html`
- Automatically opens in Chrome when generation completes
- Includes: MTD spend by team, MoM trends, 12-month history, rightsizing recommendations, anomalies, budgets, AI spend, and commitment data
- Uses view ID `1706692` (Product Hierarchy) as the primary organizational view

## MCP Data Source

- **Dashboard generation** (`uv run cldy-dash executive`): Uses the `cloudability` MCP server internally
- **Follow-up queries in chat**: Use `cldy-mcp-local` tools directly:
  - `run_cost_report` for cost data
  - `get_rightsizing_recommendations` for optimization
  - `list_anomalies` for anomaly investigation
  - `get_ri_portfolio_summary` for commitment coverage
