---
name: cldy-containers
description: Generate the Kubernetes Container Cost Dashboard. Use when the user asks for container dashboard, k8s costs, kubernetes spend, cluster costs, container optimization, idle resources, or namespace breakdown.
---

Generate the Kubernetes container cost dashboard:

1. Ensure the environment is set up:
   ```bash
   cd dashboards && uv sync
   ```

2. Generate the dashboard:
   ```bash
   cd dashboards && uv run cldy-dash containers
   ```

3. The dashboard will be generated at `dashboards/output/container_dashboard.html` and opened in the browser.

The dashboard shows: total container spend, idle cost analysis, Kubecost efficiency metrics, top clusters by cost, vendor/region breakdown, and optimization opportunities.
