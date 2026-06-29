# Agentic FinOps with Cloudability MCP

A **proactive, multi-agent FinOps system** using Cloudability MCP as the core data layer, with Slack delivery, Jira ticketing, PagerDuty escalation, and Terraform remediation.

## What This Is

This project defines the architecture and implementation plan for moving from reactive FinOps dashboards to an autonomous "Observe → Reason → Act" agent system. Inspired by Google Cloud's 5-Layer Proactive Billing Agent architecture (June 2026) and adapted for Cloudability's MCP tooling.

## Key Documents

| Document | Description |
|----------|-------------|
| [PLAN.md](./PLAN.md) | Full architecture & planning document — reference architecture, capability mapping, workflows, roadmap, risk assessment |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System architecture overview, integration patterns, and how MCP servers compose |
| [WORKFLOWS.md](./WORKFLOWS.md) | Detailed workflow definitions for each agent pattern |

## Current Status (Phase 1 — Complete)

| Phase | Status | What It Does |
|-------|--------|-------------|
| **Phase 1**: Single-Agent FinOps Analyst | ✅ Complete | Daily standups, ad-hoc cost queries, Slack delivery |
| **Phase 2**: Multi-Agent with Ticketing | 🔲 Planned | Anomaly → triage → Jira ticket → Slack notify → PagerDuty |
| **Phase 3**: Remediation Loop | 🔲 Planned | Rightsizing → Terraform PR → human approval |
| **Phase 4**: Policy-Aware Governance | 🔲 Planned | RAG over corporate policies for grounded recommendations |

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         INTERACTION LAYER                                  │
│              Slack / CLI / Email / Dashboards                              │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────────┐
│                      ORCHESTRATOR (LLM Agent)                              │
│                                                                           │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│  │ Cost Analyst│ │Anomaly Triage│ │ Rightsizing  │ │  Governance  │     │
│  │  Sub-Agent  │ │  Sub-Agent   │ │  Sub-Agent   │ │  Sub-Agent   │     │
│  └─────────────┘ └──────────────┘ └──────────────┘ └──────────────┘     │
└────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┘
     │          │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼          ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│Cloudabil-││Atlassian││  Slack  ││PagerDuty││Terraform││ GitHub  │
│ity MCP   ││  MCP    ││  MCP    ││  MCP    ││  MCP    ││  MCP    │
└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘
```

## MCP Server Stack

| Server | Role | Status |
|--------|------|--------|
| **Cloudability MCP** | Cost data, anomalies, rightsizing, budgets, containers, RI planning | ✅ Validated |
| **Slack MCP** | Deliver reports, notifications, alerts to channels | ✅ Validated |
| **Atlassian MCP** | Create/manage Jira tickets, update Confluence | 🔲 Phase 2 |
| **PagerDuty MCP** | Escalate critical anomalies, page on-call | 🔲 Phase 2 |
| **Terraform MCP** | Plan/apply infrastructure changes for rightsizing | 🔲 Phase 3 |
| **GitHub MCP** | Create PRs for IaC changes | ✅ Available |

## Setup

This is an architecture-first project. Implementation uses:
- **Kiro CLI** as the current orchestrator
- **MCP protocol** for all tool connections
- **Slack Bot Token** (`xoxb-`) with `chat:write` scope for delivery
- **Cloudability OpenToken** for API access

Configuration lives in your local MCP settings (not committed to this repo). See the plan document for required environment variables and auth setup.

## Related

- [Skills](../skills/) — Kiro CLI skills for dashboard generation and daily check-ins
- [Dashboards](../dashboards/) — Dashboard skill definitions
- Google's reference: [The Future of Cloud Governance](https://discuss.google.dev/t/the-future-of-cloud-governance-building-a-proactive-billing-agent-with-agent-platform/369751)
- AWS's approach: [Build a FinOps Agent Using Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/build-a-finops-agent-using-amazon-bedrock-with-multi-agent-capability-and-amazon-nova-as-the-foundation-model/)
