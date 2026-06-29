---
name: cldy-executive
description: Generate the Cloudability Executive Dashboard. Use when the user asks for an executive dashboard, exec dash, cloud cost summary, MTD spend, or FinOps overview.
---

Generate the executive FinOps dashboard:

1. Ensure the environment is set up:
   ```bash
   cd dashboards && uv sync
   ```

2. Generate the dashboard:
   ```bash
   cd dashboards && uv run cldy-dash executive
   ```

3. The dashboard will be generated at `dashboards/output/executive_dashboard.html` and opened in the browser.

The dashboard shows: MTD spend by team, month-over-month trends, 12-month history, rightsizing recommendations, anomalies, budget status, and commitment savings.
