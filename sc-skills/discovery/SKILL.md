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
| 🎯 Executive Brief | Hypothesis, trigger, ICP score, 3 discovery questions, recommended opener |
| 💰 Cloud Spend | Estimated spend, named providers, earnings quotes, capex signals |
| 🔧 Tech Footprint | Cloud providers, data platforms, containers, IaC, observability, AI/ML |
| 👥 FinOps Signals | Open roles, hiring keywords, org signals, maturity, buying stage |
| ⚔️ Competitive Intel | Current tools, displacement angles, partner ecosystem |
| 📊 Fundamentals | Revenue, size, industry, growth, news, key execs |
| 💬 Talking Points | Tailored questions, value prop angles, objection handling, next step |

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

## Search Strategy (12 queries in 4 batches)

### Batch 1 — Company + Cloud
1. `"[Company]" revenue employees industry cloud`
2. `"[Company]" "AWS" OR "Azure" OR "GCP" OR "cloud" annual report OR 10-K`
3. `"[Company]" earnings call cloud OR AI OR infrastructure 2025 OR 2026`

### Batch 2 — FinOps + Tech
4. `"[Company]" FinOps OR "cloud cost" OR "cloud financial management" job`
5. `"[Company]" Snowflake OR Databricks OR Kubernetes OR Terraform OR "multi-cloud"`
6. `"[Company]" "CloudHealth" OR "Cloudability" OR "Kubecost" OR "Flexera" OR "Spot.io"`

### Batch 3 — Strategy + Migration
7. `"[Company]" cloud migration OR digital transformation 2025 OR 2026`
8. `"[Company]" CTO OR CIO OR "VP Engineering" OR "VP Infrastructure" cloud`
9. `"[Company]" "cost reduction" OR "operational efficiency" OR "margin improvement"`

### Batch 4 — Ecosystem + Depth
10. `"[Company]" Deloitte OR Accenture OR Capgemini OR "consulting" cloud`
11. `"[Company]" site:sec.gov OR "SEC filing" "cloud computing" OR "hosting"`
12. `"[Company]" G2 OR Gartner "cloud cost" OR "FinOps" OR "cloud management"`

## Cloud Spend Estimation

| Industry | IT % of Revenue | Cloud Adoption % |
|----------|----------------|-----------------|
| Technology / SaaS | 10-15% | 60-80% |
| Financial Services | 7-10% | 30-50% |
| Healthcare | 4-6% | 25-40% |
| Retail / E-commerce | 3-5% | 40-60% |
| Manufacturing | 2-3% | 20-35% |
| Media / Entertainment | 5-8% | 50-70% |

Formula: `Annual Revenue x IT Spend % x Cloud Adoption % = Estimated Cloud Spend`

## Competitive Displacement Angles

| Competitor | Weakness | Cloudability Advantage |
|-----------|----------|----------------------|
| CloudHealth (Broadcom) | Acquisition uncertainty, price hikes | Stability, IBM investment |
| Native tools | Single cloud, no optimization | Multi-cloud, rightsizing, chargeback |
| Kubecost | K8s only | Full platform: cloud + containers + AI |
| Flexera | Legacy ITAM, weak cloud-native | Born-in-cloud, modern UX |
| CloudZero | Engineering-only, smaller | Enterprise-grade, finance + eng |
| In-house | Maintenance burden, gaps | Maintained platform, 150+ integrations |

## PDF Export

Built-in "Export PDF" button uses window.print() with @media print CSS.
All tabs render vertically, page breaks between sections, professional layout.
Shareable with AEs, leadership, or attached to Salesforce opportunities.

## FinOps Job Posting Keywords (Buying Signals)

**High-intent:** "cloud cost optimization", "FinOps", "cost allocation",
"showback", "chargeback", "reserved instance strategy", "savings plans",
"rightsizing", "cloud waste", "cost governance", "tagging strategy"

**Tool mentions (competitive):** "Cloudability", "CloudHealth", "Spot.io",
"Flexera", "Kubecost", "CloudZero", "Finout", "nOps", "ProsperOps",
"Vantage", "Cast AI", "Zesty"

## Discovery Question Bank

### Validate Pain:
1. "How do you currently track and allocate cloud costs across your teams?"
2. "When was the last time your cloud bill surprised you?"
3. "What percentage of your cloud spend can you confidently attribute to a product or team?"

### Understand Process:
4. "Who owns the cloud budget today — finance, engineering, or shared?"
5. "How do you handle commitment purchases (RIs, Savings Plans)?"
6. "Do you have a formal FinOps practice?"

### Quantify Impact:
7. "If you could save 20-30% on cloud, what would that free up?"
8. "How much time does your team spend on manual cost reporting?"

### Competitive:
9. "What tools are you using today for cloud cost visibility?"
10. "What's working well? What's not?"

### Timeline:
11. "Is there a budget cycle this needs to align with?"
12. "What would need to be true for you to make a change this quarter?"
