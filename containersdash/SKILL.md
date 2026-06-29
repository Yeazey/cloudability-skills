---
name: containersdash
description: Generate and open the Kubernetes Container Cost Dashboard. Use when the user asks for container dashboard, k8s costs, kubernetes spend, cluster costs, container optimization, idle resources, or namespace breakdown.
---

# Kubernetes Container Cost Dashboard

When triggered, generate the container cost dashboard and open it in Chrome:

```bash
cd /Users/kingyeazey/cloudability-dashboards && uv run cldy-dash containers
```

Project location: `/Users/kingyeazey/cloudability-dashboards/`

The dashboard pulls live container cost data from Cloudability using `cldy-mcp-local` and generates an interactive HTML dashboard at `output/container_dashboard.html`.

## Primary Data Source: `cldy-mcp-local`

Use these tools for container cost data:

### 1. Kubecost Workload Costs (preferred for allocation data)
- **Tool**: `get_kubecost_workload_costs`
- **Aggregate options**: `cluster`, `namespace`, `cluster,namespace`, `pod`, `node`, `controller`, `label`
- **Window options**: `7d`, `30d`, `90d`, `month`, `lastmonth`, `lastweek`, or RFC3339 range
- **Returns**: Fairshare-allocated costs with idle splitting, efficiency metrics, CPU/RAM/GPU/PV/network cost breakdown
- **Important**: Call `kubecost_list_windows` first if user hasn't specified a time window

### 2. Cost Reports (for billing-reconciled data)
- **Tool**: `run_cost_report`
- **Dimensions**: `container_cluster_name`, `container_namespace`, `vendor`, `region`, `year_week`
- **Metrics**: `unblended_cost`, `total_amortized_cost`
- **Use for**: Billing totals, idle analysis via "IDLE RESOURCES" namespace, vendor/region breakdown

## Dashboard Tabs

1. **Overview**: KPI cards (total spend, idle cost, idle %, cluster count), vendor donut, region bar chart, weekly trend line chart
2. **Top Clusters**: horizontal bar chart of top 20 clusters, detailed table with name/cost/amortized/region/vendor
3. **Optimization**: idle vs utilized stacked bar per cluster, top idle namespaces table, total potential savings callout, efficiency metrics
4. **KPIs**: key metric cards, cost distribution chart, week-over-week change indicators

## Design

- Dark blue/purple gradient theme
- Chart.js via CDN
- Responsive grid layout with smooth tab transitions
- Color coding: idle=coral/red, utilized=teal/green, AWS=orange, OCI=red, Azure=blue, GCP=green
- All currency formatted with $ and commas

## Key Metrics from Kubecost

- `totalCost` — Sum of all cost components per allocation
- `cpuCost` / `cpuCostIdle` — CPU request cost and idle
- `ramCost` / `ramCostIdle` — RAM request cost and idle
- `gpuCost` — GPU cost
- `networkCost` — Egress/ingress network cost
- `pvCost` — Persistent volume storage cost
- `sharedCost` — Shared namespace overhead allocation
- `totalIdleCost` — Sum of idle cost components
- `totalEfficiency` — Utilization ratio 0–1

## Key Metrics to Calculate

- Total Container Spend (sum of totalCost across all allocations)
- Total Idle Cost (sum of totalIdleCost or IDLE RESOURCES namespace)
- Idle Rate % (idle / total allocated)
- Cluster Count
- Cost per Cluster average
- Top Region and Top Vendor
- Week-over-week change %
- Efficiency score (average totalEfficiency)

## Notes

- `get_kubecost_workload_costs` is the preferred tool — it provides fairshare allocation with idle splitting
- Fall back to `run_cost_report` with container dimensions for billing-reconciled totals
- Cluster naming convention reveals vendor: `*-akp-*` = AWS EKS, `*-oke-*` = OCI OKE
- Region decoded from cluster prefix: uw2=us-west-2, ew1=eu-west-1, ec1=eu-central-1, ase2=ap-southeast-2, ane1=ap-northeast-1, as1=ap-south-1, cc1=ca-central-1, ash1=us-ashburn-1, frk1=eu-frankfurt-1, lon1=uk-london-1, sao1=sa-saopaulo-1
