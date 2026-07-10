# SC Skills

Skills designed to support Solutions Consultants in their day-to-day work. These do **NOT** depend on the Cloudability MCP server — they use web search, public data, and general-purpose tools.

## Skills

| Skill | Trigger | What It Does |
|-------|---------|--------------|
| **discovery** | "prep for a call with [company]", "discovery brief", "prospect research" | 7-tab HTML dashboard with ICP scoring, cloud spend estimation, competitive intel, and tailored talking points |

## How to Use

### IBM Bob
These skills auto-load when the repo is open (Bob reads `.bob/skills/` which includes a reference). Or copy `sc-skills/` into your Bob project.

### Kiro CLI
```bash
cp -r sc-skills/discovery ~/.kiro/skills/discovery
```

### Any AI Agent
The SKILL.md files are portable markdown instructions. Any AI agent with web search can execute them — just reference the file in conversation.

## What Goes Here vs CLDY Skills

| Folder | Requires MCP? | Purpose |
|--------|---------------|---------|
| `skills/` (CLDY) | ✅ Yes — needs `cldy-mcp-local` | Cloudability data queries, reports, dashboards |
| `sc-skills/` | ❌ No — web search only | Pre-sales, discovery, general SC productivity |

## Future SC Skills Ideas

- `/competitor-battle-card` — Generate competitive comparison for a specific deal
- `/demo-prep` — Tailor demo environment to prospect's tech stack
- `/proposal-assist` — Draft proposal sections based on discovery findings
- `/objection-handler` — Research and counter specific objections with data
