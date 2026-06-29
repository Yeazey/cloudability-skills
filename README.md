# Cloudability FinOps Toolkit

One repo, any AI tool. Dashboard generators + MCP integration for IBM Cloudability.

## Works With

| Tool | How | Setup |
|------|-----|-------|
| **Any agent** (28+ tools) | Reads `AGENTS.md` at root | Just clone the repo |
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
├── .bob/                        ← IBM Bob
│   ├── rules/cloudability.md    ← Auto-loaded project rules
│   └── skills/                  ← Bob skills (same SKILL.md format)
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
├── mcp/                         ← MCP config templates (per-tool)
├── setup.sh                     ← One-command bootstrap
└── README.md
```

## IBM Bob Setup

Bob reads everything automatically when you open this repo:
1. **Rules** (`.bob/rules/cloudability.md`) — loaded into every conversation
2. **Skills** (`.bob/skills/`) — activated on demand by description matching
3. **AGENTS.md** — loaded as workspace context

To add the MCP server for live Cloudability queries in Bob:
1. Open Bob Settings → MCP → Add Server
2. Use values from `mcp/bob.json`: command=`cldy-mcp-local`, env vars for token/env-id
3. Or run: `uv tool install cldy-mcp-local` to install the binary

## Kiro CLI Setup

```bash
# Copy skills to Kiro's skill directory
cp -r skills/* ~/.kiro/skills/

# Copy MCP config (or merge into existing)
cp mcp/kiro.json ~/.kiro/settings/mcp.json
```

## MCP Server

All tools can connect to `cldy-mcp-local` for live Cloudability data (cost reports, rightsizing, anomalies, Kubecost, etc.). See `mcp/README.md` for per-tool setup instructions.

## Prerequisites

- Python 3.10+ with [`uv`](https://docs.astral.sh/uv/)
- Cloudability API credentials (opentoken + environment ID)
- Your preferred AI coding tool

## License

MIT
