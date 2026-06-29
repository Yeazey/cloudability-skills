# dailycheckin

Run the multi-agent FinOps daily standup as a conversational markdown report. Use when the user asks for a "daily checkin", "finops standup", "morning briefing", "cost standup", "daily check-in", or "what should I focus on today".

## Steps

1. Run the daily check-in and capture JSON output:
   ```bash
   cd /Users/kingyeazey/cloudability-dashboards && uv run cldy-dash checkin --json 2>/dev/null
   ```

2. Format the JSON output as a comprehensive markdown report directly in the chat response, organized by FinOps phases:
   - **⚡ Priority Actions** — ranked by cost-of-inaction with owners, savings, blast radius
   - **👁️ INFORM** — Spend snapshot, provider breakdown, WoW movers, new services, deep dives, anomalies
   - **⚡ OPTIMIZE** — Rightsizing pipeline, savings by category, execution gap, chip architecture
   - **🏛️ OPERATE** — Budget health, maturity, governance gaps, team engagement, planning horizons
   - **📅 Meetings** — Recommended syncs for the week
   - **💡 Insight** — The #1 narrative takeaway

3. After presenting the report, remain conversational — the user can ask follow-up questions like:
   - "Tell me more about the Azure spike"
   - "What's happening in corp-legacy?"
   - "Drill into the EC2 anomalies"
   - "Who owns the stale recommendations?"
   - "Give me the to-do list by assignee"

   Use `cldy-mcp-local` MCP tools directly to answer follow-ups with live data:
   - `run_cost_report` — Drill into cost by any dimension
   - `list_anomalies` / `get_anomaly` — Investigate anomalies
   - `get_rightsizing_recommendations` — Check optimization opportunities
   - `get_kubecost_workload_costs` — Container/namespace cost breakdown
   - `get_ri_portfolio_summary` — Commitment coverage
   - `search_dimension_values` — Look up valid filter values

## What It Produces

A rich markdown standup rendered in chat with:
- Priority actions table (severity, title, savings, cost-of-inaction, owner, effort)
- Spend snapshot with MTD, daily rate, projection, annualized
- Provider breakdown with change vs prior month
- Top accounts and WoW movers with deep-dive breakdowns
- Anomaly triage (critical/warning counts and top items)
- Rightsizing pipeline with top 10 recs, savings by service, staleness metrics
- Chip architecture breakdown (Intel/AMD/Graviton/NVIDIA)
- Budget health and at-risk budgets
- FinOps maturity scoring and governance gaps
- Team engagement table (assignees, completion rates)
- Planning horizons (week/month/quarter)
- Meeting recommendations with day/who/topic/duration

## Options

- `uv run cldy-dash checkin` — Standard daily standup (markdown terminal output for quick scan)
- `uv run cldy-dash checkin --monday` — Extended Monday brief with weekly recap
- `uv run cldy-dash checkin --json` — Output raw JSON for markdown formatting in chat

## Why Markdown-in-Chat

The report is designed to be a jumping-off point for discussion. Presenting it in chat enables:
- Natural follow-up questions about any finding
- Direct MCP tool calls to drill deeper into live data
- Context retention across the conversation
- Copy/paste into Slack, email, or meeting notes
