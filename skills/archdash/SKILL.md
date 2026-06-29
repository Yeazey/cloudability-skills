---
name: multicloud
description: Generate and open the Multi-Cloud Architecture Dashboard. Use when the user asks for multi-cloud breakdown, architecture dashboard, chip breakdown, IaaS/PaaS/AI split, or cloud provider comparison.
---

# Multi-Cloud Architecture Dashboard

When triggered, generate the multi-cloud architecture dashboard and open it in Chrome:

```bash
cd /Users/kingyeazey/cloudability-dashboards && uv run cldy-dash multicloud
```

Project location: `/Users/kingyeazey/cloudability-dashboards/`

The dashboard shows 3 sections:
1. **Cloud Provider Breakdown** — Cost and % by vendor (AWS, Azure, OCI, GCP, Snowflake, Databricks, MongoDB)
2. **Service Type Breakdown** — Cost classified into IaaS, PaaS, Containers, AI/ML, and Other based on service-level mappings validated against vendor documentation
3. **Chip Architecture Breakdown** — Compute spend by processor: Intel, AMD, Graviton (ARM), NVIDIA GPU, ARM (Ampere/Other), classified by instance type regex patterns

Service and chip classifications are defined in the project's classification config and can be updated as new services or instance types are added.

## MCP Data Source

- **Dashboard generation** (`uv run cldy-dash multicloud`): Uses the `cloudability` MCP server internally
- **Follow-up queries in chat**: Use `cldy-mcp-local` tools directly:
  - `run_cost_report` with dimensions like `vendor`, `enhanced_service_name`, `instance_type` for provider/service/chip analysis
  - `search_dimension_values` to discover valid filter values
