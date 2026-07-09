---
name: ai-model-intelligence-report
description: Use when the user asks for an "AI model report", "AI model intelligence report", "show AI spend by model", or wants to understand how their cloud AI model spending compares to quality benchmarks. Pulls AI model spend from Cloudability and enriches it with Artificial Analysis benchmark context (quality index, price tier, input/output ratio, and efficiency verdict). Generates a 4-tab HTML report with model benchmarks, commitment analysis, PTU consumers, and AI-specific optimization insights.
---

# AI Model Intelligence Report

Produce a 4-tab HTML report that maps AI model spend against Artificial Analysis
benchmarks, analyzes PTU/commitment utilization, identifies consumers, and generates
7 AI-specific optimization insights.

## Prerequisites

- Cloudability MCP server (`cldy-mcp-local`) connected with valid token
- Tools needed: `run_cost_report`, `list_cost_measures`, `search_dimension_values`

---

## Step 0 — Load Customer Context

Read `.bob/active-customer.json` if it exists. Extract:
- `name` / `display_name` — report header
- `branding` — `primary_color`, `secondary_color`, `font_stack` (defaults: `#0068b5`, `#7c5cd8`, system-ui)
- `checkin_context.ai_service_filter` — custom filter (default: `service_name=@Bedrock`)

---

## Step 0b — Discover AI Dimension Names

Call `list_cost_measures`. Find dimensions with labels:
- `"AI Model"` → `$dim_ai_model`
- `"AI Model Family"` → `$dim_ai_family`
- `"Token Type"` → `$dim_token_type`

If none found → use fallback in Step 2e (service_name + operation).

---

## Step 1 — Date Range

Ask user: Last 7d / Last 30d (recommended) / Last 90d / Custom.

---

## Step 2 — Fetch AI Model Spend

### 2a-2d. Standard queries (when business dimensions exist)
See full mapping reference in skills/ai-model-intelligence-report/SKILL.md

### 2e. Multi-Cloud Fallback (when no AI Model dimensions)

Search for AI services across all clouds:
- `enhanced_service_name` containing "Bedrock", "Foundry", "Vertex"
- `service_name` containing "Bedrock" (AWS names models in service_name)

**Model identification by cloud:**
1. **AWS Bedrock** — `service_name` contains model names directly
   - `dimensions: service_name,operation` with `filters: ["service_name=@Bedrock"]`
2. **Azure Foundry** — `operation` encodes model + token direction
   - `dimensions: enhanced_service_name,operation` with `filters: ["enhanced_service_name=@Foundry"]`
   - Parse: "inp"/"Inpt" = input; "outpt"/"opt" = output; "cd"/"cchd"/"cached" = cached; "Batch" = batch
3. **GCP Vertex AI** — `dimensions: service_name,operation` with `filters: ["service_name==Vertex"]`

### 2f. Commitment Detection (CRITICAL — affects cost metric)

**Always use `total_amortized_cost` as primary metric.** Unblended only shows on-demand overflow.

```
run_cost_report:
  dimensions: lease_type
  filters: [<service_filter>]
  metrics: unblended_cost,total_amortized_cost,usage_quantity,public_on_demand_cost
```

- `lease_type == "Reserved"` → PTU commitment exists
- `lease_type == "On-Demand"` only → no commitments

If commitments exist, get reservation details:
```
run_cost_report:
  dimensions: lease_type,reservation_identifier
  filters: [<service_filter>, "reservation_identifier!=(not set)"]
  metrics: unblended_cost,total_amortized_cost,usage_quantity
```

Get consumer breakdown:
```
run_cost_report:
  dimensions: resource_identifier
  filters: [<service_filter>, "operation==Provisioned Managed Data Zone Unit"]
  metrics: unblended_cost,total_amortized_cost,usage_quantity
  sort: total_amortized_costDESC
```

### Commitment equivalents:
| Cloud | Type | Billing Signature |
|-------|------|------------------|
| Azure | PTU | `operation == "Provisioned Managed Data Zone Unit"`, `lease_type == "Reserved"` |
| AWS Bedrock | Provisioned Throughput | `lease_type == "Reserved"`, service_name shows model |
| GCP Vertex | Provisioned Throughput | `lease_type == "Reserved"`, service_name == "Vertex" |

---

## Step 3 — Enrich with Benchmarks

Map models to Artificial Analysis profiles. Full mapping tables in SKILL.md.

**Matching rules:** exact match → version-prefix → family → Unknown.

**Verdict rules:**
| Condition | Verdict |
|---|---|
| Premium + input >85% + quality >80 | ⚠ Overpaying |
| Premium + input 70-85% | △ Watch |
| Mid tier OR (Premium + input <70%) | ✓ Optimal |
| Low/Very Low tier | ✓ Optimal |
| Reranker/retrieval | ~ Justified |
| Spend <$50 | – Exploratory |

---

## Step 4 — Compute I/O Ratio

From token breakdown or operation parsing:
- `input_pct` = input_cost / (input_cost + output_cost) × 100

---

## Step 5 — Savings Opportunities

For Watch/Overpaying verdicts: suggest alternatives, estimate savings.
Include "Well-calibrated" card for Optimal models.
Include "Commitment Opportunity" if any service is 100% On-Demand.

---

## Step 6 — 7 AI Insights (Tab 4)

### 6a. AI Spend Velocity
```
run_cost_report:
  dimensions: year_week
  filters: [<service_filter>]
  metrics: total_amortized_cost
  start_date: 10 weeks ago
```
Calculate WoW growth, show sparkline, flag if >20% WoW for 3+ weeks.

### 6b. Model Sprawl
Count distinct models. Active (>$100) vs Trail (<$100). Flag >10 total.

### 6c. Prompt Caching %
Parse operations for "cached"/"cd"/"cchd" vs standard input. Calculate cache_pct per model.
Flag <5% as opportunity.

### 6d. Batch API Utilization
Parse operations for "Batch". Calculate batch_pct per model.
Flag input-heavy models with 0% batch as "Evaluate eligibility".

### 6e. Non-Production Waste
```
run_cost_report:
  dimensions: vendor_account_name
  filters: [<ai_service_filter>]
  metrics: total_amortized_cost
```
Classify accounts as Prod/NonProd. Flag NonProd >5% or >$10K.

### 6f. Workload Classification
From I/O ratios:
- <30% input / >70% output → Generation
- 30-60% / 40-70% → Balanced
- 60-80% / 20-40% → Classification/RAG
- >80% / <20% → Heavy Classification
- Streaming only → Agentic/Interactive

### 6g. Model Version Currency
Group by family. Flag older versions still active:
- <$100 → Deprecate
- $100-$5K → Evaluate migration
- >$5K → Plan migration

Supersession: Opus 4.8>4.7>4.6>4.5>4.1; Sonnet 5>4.6>4.5>4.0; GPT 5.5>5.4>5>4.1>4o

---

## Step 7 — Build HTML Report (4-Tab)

### KPI Strip (outside tabs): Total AI Spend (amortized), PTU Commitment, PTU Coverage %, Models Active, Savings Opportunity

### Tab 1: Model Spend & Benchmarks
Model table with: Model, AA Match, Amortized Cost, Quality Index, Price Tier, I/O Ratio, Verdict.
Detail rows with use case + verdict commentary.

### Tab 2: AI Commitments & PTU
Reserved vs On-Demand bar, summary table, reservations list, per-cloud sections, recommendations.

### Tab 3: PTU Consumers
Per-environment tables (Prod/PreProd/Sandbox) with application name, amortized cost, PTU-hours, share %.

### Tab 4: AI Insights
2-column card grid with all 7 insights. Full-width Model Version Currency table at bottom.

### Design rules
- Max-width 960px, centered
- No external assets
- Cost metric note: "Uses Amortized Cost — includes pre-paid reservation amortization"

---

## Step 8 — Inline Summary

- One-paragraph biggest finding
- Corrected total (amortized vs unblended if different)
- Top 3 models table: Model | Amortized | Verdict | Savings
- Commitment status: "X% coverage, Y reservations, $Z overflow"
- Total savings opportunity
