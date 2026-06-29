# MCP Server Configuration Templates

Drop-in configs for connecting `cldy-mcp-local` (Cloudability MCP server) to your AI coding tool.

## Prerequisites

1. Install the MCP server:
   ```bash
   uv tool install cldy-mcp-local
   ```

2. Set your credentials:
   ```bash
   export CLOUDABILITY_OPEN_TOKEN="your-opentoken"
   export CLOUDABILITY_ENVIRONMENT_ID="your-env-id"
   ```

## Pick Your Tool

| Tool | Config File | Copy To |
|------|-------------|---------|
| Kiro CLI | `kiro.json` | `~/.kiro/settings/mcp.json` |
| Claude Code | `claude.json` | `~/.claude/settings.json` (merge mcpServers block) |
| IBM Bob | `bob.json` | Bob Settings → MCP → Add Server (use values from JSON) |
| Cursor | `cursor.json` | `.cursor/mcp.json` in your workspace |
| VS Code (Copilot) | `vscode.json` | `.vscode/mcp.json` in your workspace |

## Notes

- `cldy-mcp-local` is a stdio-based MCP server (Python/FastMCP)
- The binary installs to `~/.local/bin/cldy-mcp-local`
- Auth is via environment variables (not hardcoded in config)
- Tokens expire — if you get 401 errors, get a new opentoken from Cloudability
