# AI Model Intelligence Report — Multi-Cloud Commitment Enhancement

This document extends the base SKILL.md with multi-cloud commitment detection,
3-tab HTML structure, and amortized cost logic.

## Step 2e — Multi-Cloud AI Service Discovery (Fallback)

If **no AI Model business dimensions** are found in Step 0b (all three are null), use this
alternative approach to identify AI models from billing data directly:

### Service discovery
Search for AI services across all clouds using `search_dimension_values`:
- `enhanced_service_name` containing "Bedrock", "Foundry", "Vertex"
- `service_name` containing "Bedrock" (AWS names models in service_name)

### Model identification strategy by cloud:
1. **AWS Bedrock** — `service_name` directly contains model names (e.g., "Claude Opus 4.7 (Amazon Bedrock Edition)")
   - Use `dimensions: service_name,operation` with `filters: ["service_name=@Bedrock"]`
   - The `operation` field shows invocation type (InvokeModelStreamingInference, InvokeModelInference)

2. **Azure Foundry** — `operation` field encodes model + token direction
   - Use `dimensions: enhanced_service_name,operation` with `filters: ["enhanced_service_name=@Foundry"]`
   - Parse operation names: "GPT 5 outpt DZone 1M Tokens", "5.4 inp Dz 1M Tokens"
   - "inp"/"Inpt"/"Input" = input tokens; "outpt"/"Outp"/"Output"/"opt"/"Opt" = output tokens
   - "cd"/"cchd"/"cached" = cached input tokens; "Batch" = batch processing

3. **GCP Vertex AI** — `operation` field shows model + operation
   - Use `dimensions: service_name,operation` with `filters: ["service_name==Vertex"]`

---

## Step 2f — Commitment Detection (CRITICAL — affects cost metric)

**Always check for AI commitments before reporting costs.** The correct cost metric for this
report is `total_amortized_cost`, NOT `unblended_cost`. Unblended only shows on-demand overflow
for committed capacity — the amortized metric captures the full economic cost.

### Query for each AI service:
```
run_cost_report:
  dimensions: lease_type
  filters: [<service_filter>]
  metrics: unblended_cost,total_amortized_cost,usage_quantity,public_on_demand_cost
```

### What to look for:
- `lease_type == "Reserved"` → Provisioned Throughput / PTU commitment exists
- `lease_type == "Savings Plan"` → Savings Plan covering AI workloads
- If ONLY `lease_type == "On-Demand"` exists → no commitments, unblended = amortized

### If commitments exist, gather details:
```
run_cost_report:
  dimensions: lease_type,reservation_identifier
  filters: [<service_filter>, "reservation_identifier!=(not set)"]
  metrics: unblended_cost,total_amortized_cost,usage_quantity
```

### Commitment equivalents across clouds:

| Cloud | Commitment Type | How it appears in billing |
|-------|----------------|--------------------------|
| **Azure** | Provisioned Throughput Units (PTU) | `operation == "Provisioned Managed Data Zone Unit"`, `lease_type == "Reserved"` |
| **AWS Bedrock** | Provisioned Throughput (Model Units) | `lease_type == "Reserved"`, `service_name` still shows model name |
| **GCP Vertex AI** | Provisioned Throughput | `lease_type == "Reserved"`, `service_name == "Vertex"` |

### Consumer breakdown (for PTU tab):
```
run_cost_report:
  dimensions: resource_identifier
  filters: [<service_filter>, "operation==Provisioned Managed Data Zone Unit"]
  metrics: unblended_cost,total_amortized_cost,usage_quantity
  sort: total_amortized_costDESC
```

Parse `resource_identifier` to extract: subscription, resource group, account name.
These map to applications/teams consuming PTU capacity.

---

## Step 6 — Build the HTML Report (UPDATED: 3-Tab Structure)

The report uses a **3-tab layout** instead of a single page:

### Tab 1: Model Spend and Benchmarks
Same as original Step 6, but:
- Use `total_amortized_cost` as the primary cost metric
- PTU infrastructure row links to Tab 2 ("See AI Commitments tab")
- Savings opportunity cards include a "Commitment Opportunity" card if any service is 100% On-Demand

### Tab 2: AI Commitments and PTU
- **Explainer box** — what PTUs are, equivalents across clouds
- **Reserved vs On-Demand bar** — visual split with percentages
- **Summary table**: PTU-hours consumed, amortized cost, effective rate per PTU-hour
- **Reservations list** — each reservation_identifier with hours consumed, estimated PTUs
- **Per-cloud sections** — only show clouds that have commitment data:
  - Azure PTU section if `lease_type == "Reserved"` exists for Foundry
  - AWS section if `lease_type == "Reserved"` exists for Bedrock
  - GCP section if `lease_type == "Reserved"` exists for Vertex
  - "No commitments" note for clouds that are 100% On-Demand (with savings recommendation)
- **Recommendations** — cover overflow, evaluate new commitments for on-demand-only services

### Tab 3: PTU Consumers
- **Metric note** — explain that PTU capacity is shared across apps
- **Per-environment tables** (Prod / PreProd / Sandbox):
  - Application name (parsed from resource group)
  - Amortized cost (proportional share of commitment)
  - PTU-hours consumed
  - Share % of total
  - Spend bar visualization
- **Key insights** — identify dominant consumers, flag pre-prod using reserved capacity

### KPI Strip (top of page, outside tabs):
5 cards:
1. Total AI Spend (amortized) — sum of ALL AI services
2. PTU Commitment — amortized cost of provisioned capacity
3. PTU Coverage % — reserved hours / total hours
4. Models Active — count of distinct models with spend > $0
5. Savings Opportunity — sum of model optimization + commitment opportunities

### Cost metric note:
Always include a visible note explaining: "This report uses Amortized Cost — the true economic
spend including pre-paid reservation amortization. Unblended (cash) cost for PTUs shows only
on-demand overflow."

---

## Step 7 — Inline Summary (UPDATED)

After the report, respond in chat with:
- One-paragraph narrative of the biggest finding
- Corrected total using amortized cost (call out if it differs significantly from unblended)
- A 3-row table: Model | Amortized Spend | Verdict | Est. Savings (top 3 by amortized spend)
- Commitment status summary: "X% PTU coverage, Y reservations active, $Z on-demand overflow"
- One sentence on total combined savings opportunity (model optimization + commitment expansion)
