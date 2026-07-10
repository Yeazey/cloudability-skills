---
name: cldyroi
description: Use when the user asks for "ROI inputs", "ROI calculator", "fill out the ROI", "cldyroi", or needs to populate the Cloudability ROI assumptions document. Automatically computes all percentage-based inputs from live Cloudability data using adaptive multi-layer detection that works across any customer environment.
---

# /cldyroi — Cloudability ROI Calculator (Full Reference)

This is the complete reference version with all step details, appendices, and service mappings.
For the condensed Bob version, see `.bob/skills/cldyroi/SKILL.md`.

## Overview

Automatically populate the Cloudability ROI Assumptions document by computing real
percentages from live billing data. Adapts to any customer environment.

## Prerequisites

- Cloudability MCP server connected with valid token
- Tools: `run_cost_report`, `search_dimension_values`, `list_cost_measures`,
  `list_business_dimensions`, `get_rightsizing_recommendations`, `list_anomalies`,
  `get_kubecost_workload_costs`, `list_tag_mappings`

---

## ROI Inputs — What We Auto-Fill vs Customer Input

| # | Input | Auto-Fill? | Method |
|---|-------|-----------|--------|
| 1 | Total annual cloud spend | ✅ Yes | `vendor` report, 12mo lookback |
| 2 | % IaaS | ✅ Yes | Service classification |
| 3 | % PaaS | ✅ Yes | Service classification |
| 4 | % orphaned assets | ✅ Yes | Rightsizing idle savings |
| 5 | % Kubernetes spend | ✅ Yes | Cluster-attributed infra + services |
| 6 | % on-demand spend | ✅ Yes | lease_type for commitment-eligible only |
| 7 | % anomalous spend | ⚡ Partial | Anomaly API (may return empty) |
| 8 | % public cloud | ✅ Yes | Always 100% in Cloudability |
| 9 | % full-stack optimization | ✅ Yes | Non-prod IaaS + storage + containers (⚠️) |
| 10 | % non-prod environments | ✅ Yes | Multi-layer detection |
| 11 | FTE counts | ❌ No | Customer input required |
| 12 | FTE costs | ❌ No | Customer input required |
| 13 | Improvement level | — | Default: Conservative |

---

## Step 1 — Total Annual Cloud Spend

```
run_cost_report:
  dimensions: vendor
  metrics: unblended_cost
  start_date: 12 months ago
  end_date: today
```

Sum all vendors. Note which clouds are present (determines which commitment types to check).

---

## Step 2 — % On-Demand (Commitment-Eligible Services Only)

### Key principle: Only count services where Cloudability has RI/SP/CUD planning support.

### 2a. Discover commitment-eligible services in this environment

Query `enhanced_service_name` for each cloud present. The complete list of
commitment-eligible services (18 types across 3 clouds) is in Appendix A.

### 2b. Get lease_type breakdown for those services

```
run_cost_report:
  dimensions: enhanced_service_name,lease_type
  filters: [one filter per commitment-eligible service found]
  metrics: unblended_cost
```

### 2c. Calculate

```
On-Demand % = sum(On-Demand for eligible services) / sum(ALL lease types for eligible services) × 100
```

**Important:** Denominator is ONLY commitment-eligible services, NOT total cloud spend.

---

## Step 3 — % Orphaned/Idle Assets

```
get_rightsizing_recommendations:
  vendor: [each vendor present]
  limit: 1  (only need aggregates)
```

Extract from `summary.aggregates`:
- `idleSavings` — truly idle resources (terminate candidates)

```
% orphaned = (sum idleSavings × annualization) / total annual spend × 100
```

Annualization: 10-day window × 36.5, or 30-day × 12.

---

## Step 4 — % Kubernetes/Container Spend

**Comprehensive definition (all layers):**

1. Infrastructure attributed to clusters: `container_cluster_name != "(not set)"`
2. Container service fees: EKS, ECS, Fargate, AKS, ACI, GKE, Cloud Run, Anthos
3. Kubecost fairshare data (if available)

Use the LARGEST number from these layers. See Appendix B for full service list.

---

## Step 5 — % Anomalous Spend

```
list_anomalies:
  start_date: 12 months ago
  end_date: today
```

If results exist: sum impact values.
If empty: report "0% detected" + note industry benchmark 5-15%.

---

## Step 6 — % Public Cloud = 100%

---

## Step 7 — % IaaS vs PaaS

Classify top 50 services. IaaS = infrastructure (compute/network/block storage).
PaaS = managed services. Exclude support/marketplace/SP lines from denominator.

---

## Step 8 — % Non-Prod (Multi-Layer Detection)

**Waterfall approach (use first layer with >80% coverage):**
1. Business dimension labeled "Environment" / "Env" / "Lifecycle"
2. Tag mapped to "Environment"
3. Account name pattern matching
4. Cluster name pattern matching

Non-prod patterns: dev, test, stage, qa, uat, sandbox, nonprod, preprod, train, demo, lab
Prod patterns: prod, production, prd, live, main

---

## Step 9 — % Full-Stack Optimization Scope

= Non-prod IaaS + Non-prod attached storage + Container optimization + Storage tiering

⚠️ NOTE: This definition needs refinement. It's an approximation that will improve
as the Cloudability full-stack optimization scope expands.

---

## Step 10 — Output

Present as formatted table matching the ROI document structure.
Include methodology notes and data source citations.

---

## Appendix A — Commitment-Eligible Services (18 Types)

### AWS (8 types):
| Type | enhanced_service_name | Scope |
|------|------|------|
| EC2 RIs | `AWS EC2` | Instance type, region, OS |
| RDS RIs | `AWS RDS` | Region, database engine |
| OpenSearch RIs | `AWS Opensearch Service` | Instance type, region |
| Redshift Reserved | `AWS Redshift` | Node type, region |
| ElastiCache Reserved | `AWS ElastiCache` | Node type, region |
| Compute SP | `AWS EC2` + ECS + Lambda + Fargate | EC2, Fargate, Lambda |
| EC2 SP | `AWS EC2` | Instance family, region |
| SageMaker SP | `AWS SageMaker` | All SageMaker instances |

### Azure (13 types):
| Type | enhanced_service_name | Scope |
|------|------|------|
| VM Reserved | `Azure Compute` | Instance type, region |
| SQL DB Reserved | `Azure Database` | Perf tier, region |
| MySQL Reserved | `Azure Database` | Deployment, instance |
| PostgreSQL Reserved | `Azure Database` | Deployment, instance |
| Blob Storage Reserved | `Azure Storage` | Access tier, redundancy |
| Cosmos DB Reserved | `Azure DocumentDB` | RU/s tier |
| Synapse Reserved | `Azure Microsoft.synapse` | DWUs, region |
| Redis Reserved | `Azure Cache` | Node type, region |
| App Service Reserved | `Azure Web` | Instance, tier |
| Compute SP | `Azure Compute` | Scope type |
| Databricks Prepurchase | `Azure Microsoft.databricks` | DBUs |
| Synapse Prepurchase | `Azure Microsoft.synapse` | SCUs |
| Foundry PTU | `Azure Foundry Models` | PTUs, region |

### GCP (3 types):
| Type | service_name | Scope |
|------|------|------|
| Compute Engine CUDs | `Compute Engine` | vCPU, memory, GPU |
| Flex-CUDs | `Compute Engine` | Hourly OD equivalent |
| Cloud SQL CUDs | `Cloud SQL` | Instance family, region |

---

## Appendix B — Container Services (Comprehensive)

| Cloud | Service | enhanced_service_name |
|-------|---------|------|
| AWS | EKS | `AWS Elastic Container Service for Kubernetes` |
| AWS | ECS | `AWS ECS` |
| AWS | Fargate | (within EC2/ECS operations) |
| AWS | App Runner | `AWS App Runner` |
| AWS | Batch | `AWS Batch` |
| Azure | AKS | `Azure Microsoft.containerservice` |
| Azure | ACI | `Azure Microsoft.containerinstance` |
| Azure | Container Apps | (within containerservice) |
| Azure | OpenShift | `Azure Red Hat OpenShift` |
| GCP | GKE | `Google Kubernetes Engine` |
| GCP | Cloud Run | `Cloud Run` |
| GCP | Anthos | `Anthos` |

**Plus:** ALL infrastructure where `container_cluster_name != "(not set)"`.

---

## Appendix C — Non-Prod Detection Patterns

**Non-prod values:** dev, development, test, testing, stage, staging, qa, uat,
sandbox, non-prod, nonprod, pre-prod, preprod, train, training, demo, lab,
perf, performance, dr, support, integration, sit, ci, build, ephemeral, temp, trial

**Prod values:** prod, production, prd, p, live, main, primary

**Account name patterns:**
- `*-prod`, `*-prd`, `*prod*`, `*production*` → PROD
- `*-dev`, `*-test`, `*-stage`, `*nonprod*`, `*preprod*`, `*sandbox*` → NON-PROD
