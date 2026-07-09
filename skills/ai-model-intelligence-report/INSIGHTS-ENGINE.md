# AI Model Intelligence Report — Insights Engine

This document defines the 7 AI-specific insights generated in Tab 4 of the report.
All insights are derived from the SAME data already pulled in Steps 2a-2f — no additional
API calls required. They are analytical enrichment of existing data.

---

## Insight 1: AI Spend Velocity

**Purpose:** Detect whether AI spend is accelerating, stable, or declining.

**Data source:**
```
run_cost_report:
  dimensions: year_week
  filters: [<service_filter>]  # run separately for each AI service
  metrics: total_amortized_cost
  sort: year_weekASC
  start_date: 10 weeks ago
```

**Logic:**
- Calculate WoW growth rate: (W_current - W_previous) / W_previous × 100
- Calculate total growth multiplier: W_latest / W_earliest
- Flag if growth > 20% WoW sustained for 3+ weeks
- Show ASCII sparkline: map each week's value to ▁▂▃▄▅▆▇█ range

**Output:** Sparkline per cloud + growth multiplier + trend warning.

---

## Insight 2: Model Sprawl Detection

**Purpose:** Identify model proliferation that creates governance and cost complexity.

**Data source:** Count distinct models from Step 2a/2e results.

**Logic:**
- Count total models with spend > $0
- Classify as "Active" (>$100 spend) vs "Trail" (<$100 spend)
- Flag if total > 10 models (complexity risk)
- List trail models as consolidation candidates
- Identify where multiple versions of the same family are active simultaneously

**Thresholds:**
- Green: ≤8 models
- Amber: 9-15 models
- Red: >15 models

**Output:** Model count, active/trail split, consolidation recommendations.

---

## Insight 3: Prompt Caching Utilization

**Purpose:** Detect underutilization of prompt caching (80-90% savings on cached tokens).

**Data source:** Azure Foundry operation names from Step 2e.

**Logic:**
- For each model, find operations containing "cd"/"cchd"/"cached" → cached input spend
- Find operations containing "inp"/"Inpt"/"Input" (without cache markers) → standard input spend
- Calculate: cache_pct = cached_spend / (cached_spend + standard_input_spend) × 100
- Flag models with cache_pct < 5% as "Low — opportunity"
- Flag models with 0% as "None detected — evaluate eligibility"

**Note:** AWS Bedrock does not expose caching in billing operations (it's baked into the
per-token price). This insight is Azure Foundry-specific unless business dimensions provide
token type data.

**Output:** Table of models with cache %, color-coded, with savings estimate.

---

## Insight 4: Batch API Utilization

**Purpose:** Identify models where batch processing (50% cheaper) is available but underused.

**Data source:** Azure Foundry operation names from Step 2e.

**Logic:**
- For each model, find operations containing "Batch" → batch spend
- Sum all operations for that model → total spend
- Calculate: batch_pct = batch_spend / total_spend × 100
- Flag models with batch_pct = 0% AND spend > $5K as "Evaluate batch eligibility"
- Flag models with batch_pct 1-20% as "Expand batch adoption"

**Batch eligibility heuristics (from I/O ratio):**
- Input-heavy (>60%) → likely classification/RAG → STRONG batch candidate
- Output-heavy (<40% input) → likely interactive/generation → probably needs real-time
- Balanced → mixed, evaluate per-workflow

**Output:** Table of models with batch %, eligibility recommendation, savings estimate.

---

## Insight 5: Non-Production AI Waste

**Purpose:** Quantify AI spend in staging/sandbox that may be unnecessary or oversized.

**Data source:**
```
run_cost_report:
  dimensions: vendor_account_name
  filters: [<ai_service_filter>]
  metrics: total_amortized_cost,unblended_cost
```

**Logic:**
- Classify accounts as Prod/NonProd/Sandbox based on naming:
  - "PreProd", "Stage", "Dev", "Sandbox", "NonProd", "Test" → NonProd
  - All others → Prod
- Sum NonProd AI spend
- Calculate NonProd as % of total
- Flag if NonProd > 5% of total AI spend OR > $10K/month
- Special flag: if NonProd is consuming RESERVED capacity (from PTU consumer data),
  recommend isolating to on-demand

**Output:** NonProd spend total, account breakdown, reservation impact warning.

---

## Insight 6: Workload Classification

**Purpose:** Classify each model's workload type from I/O patterns to validate model selection.

**Data source:** I/O ratios computed in Step 4.

**Classification rules (from I/O ratio):**

| Input % | Output % | Classification | Recommended Tier |
|---------|----------|---------------|-----------------|
| < 30% | > 70% | Generation (content creation, code gen) | Mid-Premium justified |
| 30-60% | 40-70% | Balanced (conversation, general assist) | Mid tier optimal |
| 60-80% | 20-40% | Classification/RAG (document processing) | Mid tier sufficient |
| > 80% | < 20% | Heavy Classification (batch extraction) | Low-Mid tier |
| 20-40% | 60-80% | Reasoning (chain-of-thought, planning) | Premium justified |
| Streaming only (no I/O split) | — | Agentic/Interactive | Depends on task complexity |

**Output:** Table of models with classification label + recommended tier mismatch flag.

---

## Insight 7: Model Version Currency

**Purpose:** Identify active spend on superseded model versions that should be consolidated.

**Data source:** Model list from Step 2a/2e + benchmark mapping from Step 3.

**Logic:**
- Group models by family (Opus, Sonnet, Haiku, GPT-5.x, etc.)
- Within each family, identify the LATEST version with significant spend
- Flag older versions that are still active:
  - If older version spend < $100 → "Deprecate" (likely test/orphan)
  - If older version spend $100-$5K → "Evaluate migration"
  - If older version spend > $5K → "Plan migration" (active pipeline using old version)
- Cross-reference with benchmark quality: if newer version is BETTER quality at SAME price,
  migration is strictly positive

**Supersession map:**
- Claude Opus: 4.8 > 4.7 > 4.6 > 4.5 > 4.1 > 3.x
- Claude Sonnet: 5 > 4.6 > 4.5 > 4.0 > 3.x
- Claude Haiku: 4.5 > 3.5
- GPT: 5.5 > 5.4 > 5 > 4.1 > 4o > 4o-mini
- Gemini: 3.5 > 3.1 > 3 > 2.5 > 2.0 > 1.5

**Output:** Table with old model → current model, spend, and migration recommendation.

---

## Tab 4 Layout

The Insights tab uses a 2-column card grid:
- Row 1: AI Velocity (left) | Model Sprawl (right)
- Row 2: Prompt Caching (left) | Batch Eligibility (right)
- Row 3: NonProd Waste (left) | Workload Classification (right)
- Row 4: Model Version Currency (full width — table needs space)

Each card has:
- Left border color (category-coded)
- Title with emoji icon
- Subtitle explaining the metric
- Data table or key metrics
- Bottom recommendation in muted text with 💡 prefix

---

## Data Requirements Summary

| Insight | Needs Additional API Call? | Source |
|---------|--------------------------|--------|
| AI Velocity | YES — weekly trend query | `run_cost_report` by `year_week`, 10-week lookback |
| Model Sprawl | No | Count from existing model results |
| Prompt Caching | No | Parse operations already fetched |
| Batch Eligibility | No | Parse operations already fetched |
| NonProd Waste | YES — account dimension | `run_cost_report` by `vendor_account_name` |
| Workload Classification | No | Derived from I/O ratios already computed |
| Model Version Currency | No | Derived from model list + benchmark mapping |
