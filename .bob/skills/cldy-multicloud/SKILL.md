---
name: cldy-multicloud
description: Generate the Multi-Cloud Architecture Dashboard. Use when the user asks for multi-cloud breakdown, architecture dashboard, chip breakdown, IaaS/PaaS/AI split, or cloud provider comparison.
---

Generate the multi-cloud architecture dashboard:

1. Ensure the environment is set up:
   ```bash
   cd dashboards && uv sync
   ```

2. Generate the dashboard:
   ```bash
   cd dashboards && uv run cldy-dash multicloud
   ```

3. The dashboard will be generated at `dashboards/output/multicloud_dashboard.html` and opened in the browser.

The dashboard shows: cloud provider cost breakdown (AWS, Azure, OCI, GCP, Snowflake, Databricks, MongoDB), service type classification (IaaS, PaaS, Containers, AI/ML), and chip architecture breakdown (Intel, AMD, Graviton, NVIDIA GPU, ARM Ampere).
