# Cloudability MCP Architecture & Decisions

Living document of design decisions, rationale, and how things fit together. Update this as the system evolves.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Kiro CLI                                                        │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │ cldy-mcp-local (PRIMARY) ⭐                             │     │
│  │ FastMCP / Python                                         │     │
│  │                                                          │     │
│  │ Cost/Usage Reports    Kubecost Allocation                │     │
│  │ Rightsizing            RI Planning & Portfolio            │     │
│  │ Anomaly Detection     Governance                         │     │
│  │ Business Mappings     Data Freshness                     │     │
│  │ Views/Tags            Dimension Search                   │     │
│  └───────────────────────────┬─────────────────────────────┘     │
│                              │                                    │
│  ┌───────────────┐  ┌───────┴──────────────┐                    │
│  │ Node.js MCP   │  │ Python MCP           │                    │
│  │ (cloudability) │  │ (cloudability-       │                    │
│  │ [LEGACY]      │  │  containers)         │                    │
│  │               │  │ [LEGACY]             │                    │
│  │ Used by:      │  │                      │                    │
│  │ - npm generate│  │ Container endpoints  │                    │
│  │   dashboards  │  │ are 410 Gone         │                    │
│  └───────┬───────┘  └──────────┬───────────┘                    │
│          │                     │                                 │
│          ▼                     ▼                                 │
│  ┌──────────────────────────────────────┐                        │
│  │  Cloudability V3 API                 │                        │
│  │  api.cloudability.com/v3             │                        │
│  │  + /kubecost/model/allocation        │                        │
│  │  Auth: apptio-opentoken + env-id     │                        │
│  └──────────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Decision Log

### D001: Two MCP Servers, Not One
**Date**: 2026-06-29  
**Decision**: Run Node.js and Python MCP servers side by side  
**Rationale**:
- The original Node.js server covers cost reporting, views, budgets, anomalies, rightsizing — broad but lacks advanced container APIs
- The Python server (eelzinaty/cloudability-mcp-server) implements `POST /v3/containers/report` which replaces the deprecated GET endpoints
- Merging them would require rewriting one or the other; running both is low-effort and each can evolve independently
- No tool name collisions between the two servers

**Tradeoff**: Two processes running, slightly more memory. Acceptable for a dev workstation.

---

### D002: Container Data via Cost Reports vs Containers Report API
**Date**: 2026-06-29  
**Decision**: Use BOTH paths depending on the question  
**Rationale**:
- **Cost reports** (`container_cluster_name` + `container_namespace` dimensions): Give billing-reconciled costs, include "IDLE RESOURCES" namespace, work with all standard metrics. Best for: "how much is this cluster costing us?"
- **Containers report** (`POST /v3/containers/report`): Give fairshare-allocated workload costs, efficiency metrics, label-based grouping. Best for: "which team's workloads are consuming resources?"
- They answer different questions and don't reconcile 1:1

**Rule of thumb**:
- Use cost reports for billing, idle analysis, cluster-level totals
- Use containers_report for workload attribution, team chargeback, efficiency

---

### D003: Patching Python MCP for OPENTOKEN env var
**Date**: 2026-06-29  
**Decision**: Patched `resolve_authorization()` to read `CLOUDABILITY_OPENTOKEN` from env  
**Rationale**:
- Original server only supported Frontdoor API keys or explicit `authorization` param per tool call
- MCP protocol doesn't support auto-injecting params into tool calls
- Reading from env matches how the Node.js server works
- Minimal patch, easy to maintain across upstream updates

**File**: `cloudability-mcp-server-python/cloudability_tools.py`, function `resolve_authorization`

---

### D004: Dashboard Generation Pattern
**Date**: 2026-06-22 → ongoing  
**Decision**: Generate self-contained HTML files, open in browser  
**Rationale**:
- No server to maintain, works offline after generation
- Chart.js via CDN for interactivity (tabs, hover, tooltips)
- Single file = easy to share via Slack, email, or GitHub
- Dark theme matches the "FinOps cockpit" aesthetic
- Each dashboard project has its own `npm run generate` or is built inline by the skill

**Pattern**:
1. Collect data via MCP tools
2. Build HTML with embedded data + Chart.js
3. Write to file
4. `open` the file in browser

---

### D005: Environment Switching via MCP Config
**Date**: 2026-06-29  
**Decision**: Env switching requires editing `~/.kiro/settings/mcp.json` + restart  
**Rationale**:
- MCP servers read env vars at startup, not per-request
- No hot-reload mechanism in Kiro CLI for MCP configs
- The env-keys doc (`~/cloudability-env-keys.md`) serves as the source of truth
- Future improvement: could build a CLI script that swaps + restarts

---

### D006: Skills as Workflow Triggers
**Date**: 2026-06-22 → ongoing  
**Decision**: Each major workflow gets its own Kiro skill  
**Rationale**:
- Skills are self-documenting: describe what they do, how to trigger, what they produce
- Can be shared via GitHub repos
- Compose well: `/cldy` loads context, then `/containersdash` runs the workflow
- Skills live in `~/.kiro/skills/<name>/SKILL.md`

---

### D007: Daily Check-in as Multi-Agent Pipeline
**Date**: 2026-06-23  
**Decision**: Built the daily check-in as a multi-agent orchestration  
**Rationale**:
- Each FinOps domain (cost analysis, optimization, anomalies, forecasts, operations) is a specialist agent
- Orchestrator merges findings into a single prioritized report
- Outputs JSON that can be formatted as markdown in chat for follow-up
- Enables deep-dive by asking Kiro questions about findings using live MCP data

---

### D008: Deprecated Container Endpoints
**Date**: 2026-06-29  
**Decision**: Stop using `/containers/clusters`, `/containers/usage`, `/containers/counts`, `/containers/labels`  
**Rationale**:
- All return HTTP 410 Gone
- Cloudability migrated container data to:
  - Cost reports (billing view): `container_cluster_name`, `container_namespace` dimensions
  - Containers report (fairshare view): `POST /v3/containers/report`
  - Kubecost allocation: `/v3/kubecost/model/allocation` (used by `cldy-mcp-local`)
- The Node.js MCP server still has the old tools defined (they just error) — harmless, but don't use them

---

### D009: cldy-mcp-local as Primary MCP Server
**Date**: 2026-06-29  
**Decision**: Adopt `cldy-mcp-local` (v0.2.0) as the primary MCP server for all Cloudability queries  
**Rationale**:
- Single unified server covers ALL domains: cost reporting, usage reporting, Kubecost container allocation, rightsizing, RI planning, RI portfolio, anomaly detection, governance, business mappings, data freshness, views, tags
- Provides `get_kubecost_workload_costs` — the correct endpoint for Kubernetes cost allocation with fairshare, idle splitting, and efficiency metrics
- Supports aggregation by cluster, namespace, pod, node, controller, label with configurable time windows
- Built with FastMCP (Python), pre-packaged as a wheel, installed via `uv tool install`
- Uses same auth as other servers: `CLOUDABILITY_OPEN_TOKEN` + `CLOUDABILITY_ENVIRONMENT_ID`
- Node.js MCP remains for dashboard generator projects (they `npm run generate` using it internally)
- Python MCP (`cloudability-containers`) is effectively superseded

**Config**: `~/.kiro/settings/mcp.json` → `cldy-mcp-local` entry  
**Binary**: `/Users/kingyeazey/.local/bin/cldy-mcp-local`  
**Package source**: `~/Downloads/cldy-mcp-local/cldy_mcp_local-0.2.0-py3-none-any.whl`

**Tool preference order**:
1. Always use `cldy-mcp-local` tools for interactive queries
2. Fall back to Node.js MCP only for `npm run generate` dashboard workflows
3. Do not use `cloudability-containers` Python MCP for new work

---

### D010: Unified Python Dashboard Project
**Date**: 2026-06-29  
**Decision**: Consolidated all dashboard generators into a single Python project (`cloudability-dashboards`)  
**Rationale**:
- Three separate Node.js projects (executive, multicloud, dailycheckin) + inline container generation → one Python project
- All three Node.js projects did the same thing: spawn the Node.js MCP server as a subprocess, call tools, generate HTML
- The new project uses direct HTTP calls to the Cloudability V3 API (via httpx), eliminating the MCP subprocess pattern
- Jinja2 templates with a shared base provide consistent dark theme across all dashboards
- Two dependencies total (httpx + jinja2) vs three node_modules folders
- Single CLI entry point: `cldy-dash {executive|multicloud|containers|checkin}`
- Installed via uv, runs on Python 3.10+

**What it replaces**:
- ❌ `cloudability-executive-dashboard/` (Node.js, @modelcontextprotocol/sdk)
- ❌ `cloudability-multicloud-dashboard/` (Node.js, @modelcontextprotocol/sdk)
- ❌ `cloudability-dailycheckin/` (Node.js, @modelcontextprotocol/sdk)
- ❌ Inline container dashboard generation in Kiro skill

**Project**: `/Users/kingyeazey/cloudability-dashboards/`  
**CLI**: `uv run cldy-dash <command>` or install as tool: `cldy-dash <command>`  
**Dependencies**: httpx>=0.27.0, jinja2>=3.1.0

---

## Known Limitations

1. **Token expiry**: Opentokens expire. 401 errors mean "ask user for new token"
2. **`fairshare_cost` / `utilized_cost` / `idle_cost` metrics**: Only available in some environments via cost reports; not available in cldydemo.main. Use "IDLE RESOURCES" namespace or `get_kubecost_workload_costs` idle fields instead.
3. **No real-time data**: Cloudability data has ~24hr lag from cloud billing files
4. **Python 3.14 requirement**: The legacy containers MCP server needs Python 3.14+, but `cldy-mcp-local` uses whatever Python `uv tool` provides
5. **cldy-mcp-local env var naming**: Uses `CLOUDABILITY_OPEN_TOKEN` (with underscore between OPEN and TOKEN), while Node.js MCP uses `CLOUDABILITY_OPENTOKEN` (no underscore)

---

## Future Improvements

- [ ] Add env-switching CLI script (swap token + restart Kiro)
- [x] ~~Migrate dashboard generators to use `cldy-mcp-local` instead of Node.js MCP~~ → D010: consolidated into `cloudability-dashboards` with direct API calls
- [ ] Remove legacy Python MCP (`cloudability-containers`) from config once fully superseded
- [ ] Build a savings tracker dashboard (combine rightsizing + idle + commitments)
- [ ] Automate token refresh via Frontdoor API keys
- [ ] Explore `cldy-mcp-local` governance tools for policy-as-code workflows
