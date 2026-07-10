---
name: discovery
description: Use when the user asks for a "discovery brief", "prospect research", "account intel", "prep for a call with [company]", "discovery dashboard", or wants to research a company before a demo, discovery call, or sales meeting. Generates a 7-tab HTML dashboard with cloud spend signals, tech footprint, FinOps buying signals, competitive intel, and tailored talking points for Cloudability sellers.
---

# /discovery — Sales Discovery Dashboard (Full Reference)

See the full SKILL.md at ~/.kiro/skills/discovery/SKILL.md for complete implementation.
This file documents the search strategies, scoring model, and report architecture.

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

Formula: `Annual Revenue × IT Spend % × Cloud Adoption % = Estimated Cloud Spend`

## Competitive Displacement Angles

| Competitor | Weakness | Cloudability Advantage |
|-----------|----------|----------------------|
| CloudHealth (Broadcom) | Acquisition uncertainty, price hikes | Stability, IBM investment |
| Native tools | Single cloud, no optimization | Multi-cloud, rightsizing, chargeback |
| Kubecost | K8s only | Full platform: cloud + containers + AI |
| Flexera | Legacy ITAM, weak cloud-native | Born-in-cloud, modern UX |
| CloudZero | Engineering-only, smaller | Enterprise-grade, finance + eng |
| In-house | Maintenance burden, gaps | Maintained platform, 150+ integrations |

## FinOps Job Posting Keywords (Buying Signals)

High-intent: "cloud cost optimization", "FinOps", "cost allocation", "showback",
"chargeback", "reserved instance strategy", "savings plans", "rightsizing",
"cloud waste", "cost governance", "tagging strategy"

## Discovery Question Bank (15 questions across 5 categories)

1. Validate Pain (4 questions)
2. Understand Process (3 questions)
3. Quantify Impact (3 questions)
4. Competitive/Current State (3 questions)
5. Timeline/Urgency (2 questions)

See full question bank in the local SKILL.md.
