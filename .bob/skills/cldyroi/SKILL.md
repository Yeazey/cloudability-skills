---
name: cldyroi
description: Use when the user asks for "ROI inputs", "ROI calculator", "fill out the ROI", "cldyroi", or needs to populate the Cloudability ROI assumptions document. Automatically computes all percentage-based inputs from live Cloudability data using adaptive multi-layer detection that works across any customer environment.
---

# /cldyroi — Cloudability ROI Calculator

Automatically populate the Cloudability ROI Assumptions document by computing real
percentages from live billing data. Adapts to any customer environment.

## Prerequisites

- Cloudability MCP server connected with valid token
- Tools: `run_cost_report`, `search_dimension_values`, `list_cost_measures`,
  `list_business_dimensions`, `get_rightsizing_recommendations`

## Steps

1. **Total Annual Spend** — `run_cost_report` by vendor, 12-month lookback
2. **% On-Demand** — `lease_type` filtered to commitment-eligible services ONLY (see Appendix A for all 18+ types across AWS/Azure/GCP)
3. **% Orphaned** — `get_rightsizing_recommendations` idle savings, annualized ÷ total spend
4. **% K8s** — `container_cluster_name != (not set)` + container service fees + Kubecost
5. **% Anomalous** — `list_anomalies` impact sum ÷ total (default 5-15% if empty)
6. **% Public Cloud** — 100% (all Cloudability data is public cloud)
7. **% IaaS/PaaS** — classify top services by type
8. **% Non-Prod** — multi-layer: business dim → tag → account name → cluster name
9. **% Full-Stack Opt** — non-prod IaaS + storage + containers (⚠️ needs refinement)
10. **Output** — formatted table matching ROI document

## Key Design Principles

- **Adaptive:** Works across any customer environment regardless of tagging maturity
- **Multi-layer detection:** Falls through business dims → tags → account names → cluster names
- **Dynamic service discovery:** Doesn't hardcode services — discovers what exists
- **Commitment-scoped:** On-demand % only counts services eligible for RI/SP/CUD
- **Container-inclusive:** K8s = cluster-attributed infra + service fees + Kubecost

## Full documentation: see skills/cldyroi/SKILL.md for complete step-by-step with all appendices.
