#!/usr/bin/env bash
set -euo pipefail

echo "╔══════════════════════════════════════════════════╗"
echo "║  Cloudability FinOps Toolkit — Setup             ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Check for uv
if ! command -v uv &>/dev/null; then
    echo "📦 Installing uv (Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install Python dependencies
echo "📦 Installing dashboard generator dependencies..."
cd "$(dirname "$0")/dashboards"
uv sync
echo ""

# Check for credentials
if [ -z "${CLOUDABILITY_OPEN_TOKEN:-}" ] || [ -z "${CLOUDABILITY_ENVIRONMENT_ID:-}" ]; then
    echo "⚠️  Credentials not set. Before generating dashboards, run:"
    echo ""
    echo "    export CLOUDABILITY_OPEN_TOKEN=\"your-token\""
    echo "    export CLOUDABILITY_ENVIRONMENT_ID=\"your-env-id\""
    echo ""
    echo "   Or create dashboards/.env with those values."
else
    echo "✅ Credentials detected."
fi

echo ""
echo "✅ Setup complete! Available commands:"
echo ""
echo "    cd dashboards"
echo "    uv run cldy-dash executive     # Executive dashboard"
echo "    uv run cldy-dash multicloud    # Multi-cloud architecture"
echo "    uv run cldy-dash containers    # Kubernetes containers"
echo "    uv run cldy-dash checkin       # Daily standup report"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "For MCP server setup, see mcp/README.md"
echo "For IBM Bob:   Copy .bob/ contents to your project"
echo "For Kiro CLI:  Copy skills/* to ~/.kiro/skills/"
echo "For Claude:    See CLAUDE.md + mcp/claude.json"
