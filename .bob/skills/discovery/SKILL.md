---
name: discovery
description: Use when the user asks for a "discovery brief", "prospect research", "account intel", "prep for a call with [company]", "discovery dashboard", or wants to research a company before a demo, discovery call, or sales meeting. Generates a 7-tab HTML dashboard with cloud spend signals, tech footprint, FinOps buying signals, competitive intel, and tailored talking points for Cloudability sellers.
---

# /discovery — Sales Discovery Dashboard

Generate a comprehensive HTML discovery brief for any company. Purpose-built for
IBM Cloudability sellers — surfaces cloud spend signals, FinOps buying indicators,
competitive tool usage, and generates a testable hypothesis with tailored discovery questions.

## Prerequisites

- Web search capability (`web_search`, `web_fetch`)
- No MCP or API keys required — uses public data only

## Process

1. Get company name (optionally: ticker, URL, call context)
2. Run 12 parallel web searches across 4 tracks:
   - Company basics + cloud provider detection
   - FinOps signals + tech stack
   - Strategy + migration signals
   - Ecosystem + competitive intel
3. Optionally deep-fetch 2-3 pages (10-K, careers page, earnings transcript)
4. Compute ICP score (0-100) from weighted signals
5. Estimate cloud spend (revenue x IT% x cloud% by industry)
6. Generate testable hypothesis + "why now" trigger
7. Assess FinOps maturity (Crawl/Walk/Run)
8. Build 7-tab HTML report with PDF export
9. Present inline summary in chat

## 7-Tab HTML Report

| Tab | Content |
|-----|---------|
| Executive Brief | Hypothesis, trigger, ICP score, 3 discovery questions, recommended opener |
| Cloud Spend | Estimated spend, named providers, earnings quotes, capex signals |
| Tech Footprint | Cloud providers, data platforms, containers, IaC, observability, AI/ML |
| FinOps Signals | Open roles, hiring keywords, org signals, maturity, buying stage |
| Competitive Intel | Current tools, displacement angles, partner ecosystem |
| Fundamentals | Revenue, size, industry, growth, news, key execs |
| Talking Points | Tailored questions, value prop angles, objection handling, next step |

## ICP Scoring (0-100)

| Signal | Points |
|--------|--------|
| Cloud spend >$5M | +20 |
| Multi-cloud | +15 |
| FinOps hiring | +15 |
| Kubernetes at scale | +10 |
| Cloud migration | +10 |
| No FinOps tool / native only | +10 |
| Cost mandate (CEO/CFO) | +10 |
| Large org (2000+) | +5 |
| Competitor tool in use | +5 |

## PDF Export

Built-in Export PDF button uses window.print() with @media print CSS.
All tabs render vertically, page breaks between sections, professional layout.

## Full reference: see skills/discovery/SKILL.md for search queries and appendices.
