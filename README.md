# Cloudability FinOps Toolkit

One repo, any AI tool. Dashboard generators + MCP integration for IBM Cloudability.

## Works With

| Tool | How | Setup |
|------|-----|-------|
| **Any agent** (28+ tools) | Reads `AGENTS.md` at root | Just clone the repo |
| **OpenAI Codex** | `AGENTS.md` (read natively) + MCP config | Copy `mcp/codex.toml` into `~/.codex/config.toml` |
| **IBM Bob** | `.bob/skills/` + `.bob/rules/` | Clone → open in Bob → skills auto-load |
| **Claude Code** | `CLAUDE.md` + MCP config | See `mcp/claude.json` |
| **Kiro CLI** | `skills/` → copy to `~/.kiro/skills/` | See Kiro section below |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Automatic |
| **Cursor** | `AGENTS.md` + `.cursor/mcp.json` | Copy `mcp/cursor.json` |
| **VS Code** | `AGENTS.md` + `.vscode/mcp.json` | Copy `mcp/vscode.json` |

## Quick Start

```bash
git clone https://github.com/Yeazey/cloudability-skills.git
cd cloudability-skills
./setup.sh
```

Or manually:
```bash
cd dashboards && uv sync
export CLOUDABILITY_OPEN_TOKEN="your-token"
export CLOUDABILITY_ENVIRONMENT_ID="your-env-id"
uv run cldy-dash --help
```

## Skills

| Skill | Trigger Phrases | What It Produces |
|-------|----------------|-----------------|
| **AI Model Intelligence Report** | "AI model report", "show AI spend by model", "AI benchmarks" | 4-tab HTML: model benchmarks, PTU commitments, consumers, 7 AI insights |
| **Executive Dashboard** | "executive dashboard", "cloud cost summary" | Executive HTML dashboard with MTD spend, trends, anomalies |
| **Multi-Cloud Architecture** | "multi-cloud", "architecture dashboard", "chip breakdown" | Vendor/IaaS/PaaS/AI/chip breakdown dashboard |
| **Container Dashboard** | "container dashboard", "k8s costs", "idle resources" | Kubernetes cost allocation, idle analysis, optimization |
| **Daily Check-in** | "daily checkin", "finops standup", "morning briefing" | Markdown standup with priority actions |

### AI Model Intelligence Report (NEW)

Generates a comprehensive AI spend analysis report with 4 tabs:

1. **Model Spend & Benchmarks** — Maps each AI model to Artificial Analysis quality scores, price tiers, and I/O ratios. Assigns efficiency verdicts (Optimal/Watch/Overpaying).
2. **AI Commitments & PTU** — Analyzes Azure PTU reservations, AWS Bedrock Provisioned Throughput, and GCP Vertex commitments. Shows reserved vs on-demand coverage.
3. **PTU Consumers** — Breaks down which applications/teams consume committed capacity.
4. **AI Insights** — 7 optimization signals: spend velocity, model sprawl, prompt caching %, batch eligibility, non-prod waste, workload classification, model version currency.

**Key features:**
- Uses `total_amortized_cost` (not unblended) to capture true commitment costs
- Multi-cloud: AWS Bedrock + Azure Foundry + GCP Vertex AI
- Auto-detects AI model dimensions; falls back to service_name + operation parsing
- Populates commitment tabs dynamically based on what's active

## Dashboards

| Command | Output | What it shows |
|---------|--------|---------------|
| `cldy-dash executive` | Executive dashboard | MTD spend, trends, rightsizing, anomalies, budgets |
| `cldy-dash multicloud` | Architecture dashboard | Vendor split, IaaS/PaaS/AI, chip breakdown |
| `cldy-dash containers` | Container dashboard | Cluster costs, idle analysis, Kubecost metrics |
| `cldy-dash checkin` | Markdown report | Daily standup with priority actions |

## Repository Structure

```
├── AGENTS.md                    ← Universal AI agent instructions (28+ tools)
├── CLAUDE.md                    ← Claude Code specific
├── .bob/                        ← IBM Bob (auto-loads on repo open)
│   ├── rules/cloudability.md    ← Auto-loaded project rules
│   └── skills/                  ← Bob skills (SKILL.md format)
│       ├── ai-model-intelligence-report/  ← NEW: AI benchmarks + PTU + insights
│       ├── cldy-executive/
│       ├── cldy-multicloud/
│       ├── cldy-containers/
│       └── cldy-checkin/
├── .github/
│   └── copilot-instructions.md  ← GitHub Copilot
├── dashboards/                  ← Python project (the actual code)
│   ├── pyproject.toml
│   └── src/cloudability_dashboards/
│       ├── client.py            ← Cloudability V3 API (httpx)
│       ├── cli.py               ← cldy-dash entry point
│       ├── generators/          ← One per dashboard
│       └── templates/           ← Jinja2 (shared dark theme)
├── skills/                      ← Kiro CLI skills (copy to ~/.kiro/skills/)
│   └── ai-model-intelligence-report/
│       ├── SKILL.md             ← Full base skill + model mapping tables
│       ├── COMMITMENT-ENHANCEMENT.md  ← Multi-cloud PTU detection logic
│       └── INSIGHTS-ENGINE.md   ← 7 AI insights documentation
├── mcp/                         ← MCP config templates (per-tool)
├── setup.sh                     ← One-command bootstrap
└── README.md
```

## IBM Bob Setup

Bob reads everything automatically when you open this repo:
1. **Rules** (`.bob/rules/cloudability.md`) — loaded into every conversation
2. **Skills** (`.bob/skills/`) — activated on demand by description matching
3. **AGENTS.md** — loaded as workspace context

**To use the AI Model Intelligence Report in Bob:**
1. Clone this repo and open it in Bob
2. Say "Generate an AI model intelligence report" or "Show me AI spend by model"
3. Bob matches the skill description and executes the steps automatically

**To add the MCP server for live Cloudability queries in Bob:**
1. Open Bob Settings → MCP → Add Server
2. Use values from `mcp/bob.json`: command=`cldy-mcp-local`, env vars for token/env-id
3. Or run: `uv tool install cldy-mcp-local` to install the binary

### Bob Skill Format

Each skill in `.bob/skills/<name>/SKILL.md` uses this format:
```markdown
---
name: skill-name
description: Trigger phrases and what the skill does.
---

# Skill Title

Step-by-step instructions the agent follows.
```

Bob activates skills when the user's request matches the `description` field.

## Kiro CLI Setup

```bash
# Copy skills to Kiro's skill directory
cp -r skills/* ~/.kiro/skills/

# Copy MCP config (or merge into existing)
cp mcp/kiro.json ~/.kiro/settings/mcp.json
```

**Note:** Kiro skills use the same SKILL.md format but are stored at `~/.kiro/skills/` globally.
The `skills/` folder in this repo contains the full reference versions with detailed model mapping
tables and documentation. The `.bob/skills/` versions are condensed for Bob's context window.

## Other IDE Setup

| IDE/Agent | Skill Location | How It Works |
|-----------|---------------|--------------|
| **IBM Bob** | `.bob/skills/` | Auto-detected from description on repo open |
| **Kiro CLI** | `~/.kiro/skills/` | Copy from `skills/` folder |
| **Claude Code** | Reads `CLAUDE.md` + `AGENTS.md` | Reference skills in conversation |
| **Cursor/Windsurf** | Reads `AGENTS.md` | Reference skills via @ mention |
| **Any MCP-capable agent** | Connect `cldy-mcp-local` | Skills are just prompts — paste or reference |

The skills are **portable markdown instructions** — any AI agent with access to the
Cloudability MCP tools can execute them. The format is:
1. YAML frontmatter with `name` and `description` (triggers)
2. Markdown body with numbered steps referencing MCP tool calls

## MCP Server

All tools can connect to `cldy-mcp-local` for live Cloudability data (cost reports, rightsizing, anomalies, Kubecost, etc.). See `mcp/README.md` for per-tool setup instructions.

Required environment variables:
```bash
CLOUDABILITY_OPEN_TOKEN="your-opentoken"
CLOUDABILITY_ENVIRONMENT_ID="your-environment-id"
```

## Prerequisites

- Python 3.10+ with [`uv`](https://docs.astral.sh/uv/)
- Cloudability API credentials (opentoken + environment ID)
- Your preferred AI coding tool

## License

MIT
