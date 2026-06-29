---
name: cldy-checkin
description: Run the FinOps daily check-in standup report. Use when the user asks for a daily checkin, finops standup, morning briefing, cost standup, or what to focus on today.
---

Run the daily FinOps check-in:

1. Ensure the environment is set up:
   ```bash
   cd dashboards && uv sync
   ```

2. Run the check-in (markdown output):
   ```bash
   cd dashboards && uv run cldy-dash checkin
   ```

   For JSON output: `cd dashboards && uv run cldy-dash checkin --json`

3. Present the report to the user. The check-in includes:
   - Priority actions ranked by cost impact
   - Spend snapshot (MTD, daily rate, projection)
   - Provider breakdown with month-over-month changes
   - Rightsizing pipeline and top savings opportunities
   - Budget health and anomaly triage
   - Key insight / narrative takeaway
