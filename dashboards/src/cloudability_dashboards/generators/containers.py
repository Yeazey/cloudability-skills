"""Kubernetes Container Cost Dashboard Generator.

Collects data from the Cloudability cost reporting API and the Kubecost
allocation endpoint, then generates a container-focused HTML dashboard
showing cluster costs, idle spend, vendor/region breakdowns, and
efficiency metrics.

Each API call is individually error-handled so that a single failure
(e.g. Kubecost unavailable) does not crash the generation pipeline.
When Kubecost data is unavailable, the dashboard falls back to
billing-only data.

Usage:
    from cloudability_dashboards.generators.containers import generate

    path = generate()
    print(f"Dashboard written to {path}")
"""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from cloudability_dashboards.client import CloudabilityClient, DateHelper


# ======================================================================
# Helpers
# ======================================================================


def _safe_float(val, default: float = 0.0) -> float:
    """Safely convert a value to float, returning default on failure."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _get_template_env() -> Environment:
    """Create a Jinja2 Environment pointing at the project templates directory."""
    template_dir = Path(__file__).parent.parent / "templates"
    return Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)


def _extract_rows(report: dict) -> list[dict]:
    """Extract row data from a cost report response.

    The API returns results nested under various keys depending on
    the endpoint version. This normalizes access.
    """
    if not report:
        return []
    if "results" in report:
        return report["results"] if isinstance(report["results"], list) else []
    if isinstance(report, list):
        return report
    return []


def _detect_vendor(cluster_name: str) -> str:
    """Infer cloud vendor from cluster naming conventions.

    Args:
        cluster_name: The Kubernetes cluster name.

    Returns:
        Vendor string (Amazon, OCI, or Unknown).
    """
    if "-akp-" in cluster_name or "-infra-" in cluster_name:
        return "Amazon"
    if "-oke-" in cluster_name:
        return "OCI"
    return "Unknown"


# ======================================================================
# Kubecost Response Parsing
# ======================================================================


def _parse_kubecost_cluster_response(response: dict) -> list[dict]:
    """Parse the Kubecost allocation API response for cluster-level data.

    The Kubecost API returns:
    {
        "code": 200,
        "data": [
            {
                "cluster-name/__idle__": {...allocation...},
                "cluster-name/__unallocated__": {...},
                "cluster-name/allocation-name": {...},
                ...
            }
        ]
    }

    We aggregate per-cluster metrics from all allocation objects that share
    the same cluster name.

    Args:
        response: Raw JSON response from the Kubecost allocation endpoint.

    Returns:
        List of cluster summary dicts with cost and efficiency metrics.
    """
    if not response or not isinstance(response, dict):
        return []

    data = response.get("data")
    if not data or not isinstance(data, list) or len(data) == 0:
        return []

    # data[0] is a dict mapping allocation keys to allocation objects
    allocations = data[0]
    if not isinstance(allocations, dict):
        return []

    # Aggregate by cluster
    clusters: dict[str, dict] = {}

    for _key, alloc in allocations.items():
        if not isinstance(alloc, dict):
            continue

        name = alloc.get("name", "")
        # For cluster-aggregated queries, name is the cluster name directly
        # For namespace-aggregated, it might be "cluster/namespace"
        cluster_name = name.split("/")[0] if "/" in name else name

        if cluster_name not in clusters:
            clusters[cluster_name] = {
                "name": cluster_name,
                "cpuCost": 0.0,
                "cpuCostIdle": 0.0,
                "ramCost": 0.0,
                "ramCostIdle": 0.0,
                "gpuCost": 0.0,
                "gpuCostIdle": 0.0,
                "networkCost": 0.0,
                "pvCost": 0.0,
                "totalCost": 0.0,
            }

        c = clusters[cluster_name]
        c["cpuCost"] += _safe_float(alloc.get("cpuCost"))
        c["cpuCostIdle"] += _safe_float(alloc.get("cpuCostIdle"))
        c["ramCost"] += _safe_float(alloc.get("ramCost"))
        c["ramCostIdle"] += _safe_float(alloc.get("ramCostIdle"))
        c["gpuCost"] += _safe_float(alloc.get("gpuCost"))
        c["gpuCostIdle"] += _safe_float(alloc.get("gpuCostIdle"))
        c["networkCost"] += _safe_float(alloc.get("networkCost"))
        c["pvCost"] += _safe_float(alloc.get("pvCost"))
        c["totalCost"] += _safe_float(alloc.get("totalCost"))

    # Compute derived metrics
    result = []
    for cluster_data in clusters.values():
        total = cluster_data["totalCost"]
        cpu_cost = cluster_data["cpuCost"]
        cpu_idle = cluster_data["cpuCostIdle"]
        ram_cost = cluster_data["ramCost"]
        ram_idle = cluster_data["ramCostIdle"]

        # Idle percentage: idle cost as fraction of total cost in that resource category
        cpu_idle_pct = (cpu_idle / cpu_cost * 100) if cpu_cost > 0 else 0.0
        ram_idle_pct = (ram_idle / ram_cost * 100) if ram_cost > 0 else 0.0

        total_idle_cost = cpu_idle + ram_idle + _safe_float(cluster_data.get("gpuCostIdle"))
        total_idle_pct = (total_idle_cost / total * 100) if total > 0 else 0.0

        # Efficiency = 1 - idle fraction
        efficiency = ((total - total_idle_cost) / total * 100) if total > 0 else 0.0

        result.append({
            "name": cluster_data["name"],
            "totalCost": round(total, 2),
            "totalIdlePct": round(total_idle_pct, 1),
            "cpuCost": round(cpu_cost, 2),
            "cpuIdlePct": round(cpu_idle_pct, 1),
            "ramCost": round(ram_cost, 2),
            "ramIdlePct": round(ram_idle_pct, 1),
            "gpuCost": round(cluster_data["gpuCost"], 2),
            "networkCost": round(cluster_data["networkCost"], 2),
            "pvCost": round(cluster_data["pvCost"], 2),
            "efficiency": round(efficiency, 1),
        })

    # Sort by total cost descending
    result.sort(key=lambda c: c["totalCost"], reverse=True)
    return result


def _parse_kubecost_namespace_response(response: dict) -> list[dict]:
    """Parse the Kubecost allocation API response for namespace-level data.

    Args:
        response: Raw JSON response from the Kubecost allocation endpoint
                  aggregated by cluster,namespace.

    Returns:
        List of namespace detail dicts with cost breakdown.
    """
    if not response or not isinstance(response, dict):
        return []

    data = response.get("data")
    if not data or not isinstance(data, list) or len(data) == 0:
        return []

    allocations = data[0]
    if not isinstance(allocations, dict):
        return []

    result = []
    for _key, alloc in allocations.items():
        if not isinstance(alloc, dict):
            continue

        name = alloc.get("name", "")
        properties = alloc.get("properties", {}) or {}
        cluster = properties.get("cluster", "")
        namespace = properties.get("namespace", name)

        total_cost = _safe_float(alloc.get("totalCost"))
        cpu_idle = _safe_float(alloc.get("cpuCostIdle"))
        ram_idle = _safe_float(alloc.get("ramCostIdle"))
        gpu_idle = _safe_float(alloc.get("gpuCostIdle"))
        total_idle = cpu_idle + ram_idle + gpu_idle
        efficiency = ((total_cost - total_idle) / total_cost * 100) if total_cost > 0 else 0.0

        result.append({
            "cluster": cluster,
            "namespace": namespace,
            "totalCost": round(total_cost, 2),
            "cpuCost": round(_safe_float(alloc.get("cpuCost")), 2),
            "ramCost": round(_safe_float(alloc.get("ramCost")), 2),
            "gpuCost": round(_safe_float(alloc.get("gpuCost")), 2),
            "networkCost": round(_safe_float(alloc.get("networkCost")), 2),
            "pvCost": round(_safe_float(alloc.get("pvCost")), 2),
            "efficiency": round(efficiency, 1),
        })

    result.sort(key=lambda n: n["totalCost"], reverse=True)
    return result


# ======================================================================
# Data Collection
# ======================================================================


def _collect_kubecost_clusters(client: CloudabilityClient) -> dict:
    """Fetch Kubecost allocation data aggregated by cluster."""
    print("🐳 Collecting Kubecost cluster allocation data...")
    try:
        return client.kubecost_allocation(
            aggregate="cluster",
            window="30d",
            accumulate=True,
        )
    except Exception as e:
        print(f"  ⚠️  Failed to collect Kubecost cluster data: {e}")
        return {}


def _collect_kubecost_namespaces(client: CloudabilityClient) -> dict:
    """Fetch Kubecost allocation data aggregated by cluster and namespace."""
    print("🐳 Collecting Kubecost namespace allocation data...")
    try:
        return client.kubecost_allocation(
            aggregate="cluster,namespace",
            window="30d",
            accumulate=True,
        )
    except Exception as e:
        print(f"  ⚠️  Failed to collect Kubecost namespace data: {e}")
        return {}


def _collect_billing_cluster_data(client: CloudabilityClient) -> dict:
    """Fetch billing cost data grouped by container cluster, vendor, region."""
    print("💰 Collecting billing cluster data...")
    start, _ = DateHelper.last_n_days(30)
    _, end = DateHelper.current_month()
    try:
        return client.cost_report(
            dimensions="container_cluster_name,vendor,region",
            metrics="unblended_cost,total_amortized_cost",
            start_date=start,
            end_date=end,
            sort="unblended_costDESC",
            limit=200,
        )
    except Exception as e:
        print(f"  ⚠️  Failed to collect billing cluster data: {e}")
        return {}


# ======================================================================
# Data Processing
# ======================================================================


def _process_data(
    kubecost_clusters_raw: dict,
    kubecost_namespaces_raw: dict,
    billing_data: dict,
) -> dict:
    """Transform raw API responses into a context dict for template rendering.

    Args:
        kubecost_clusters_raw: Raw Kubecost cluster allocation response.
        kubecost_namespaces_raw: Raw Kubecost namespace allocation response.
        billing_data: Raw cost report response with cluster/vendor/region dimensions.

    Returns:
        Dictionary with all computed metrics ready for the Jinja2 template.
    """
    # --- Parse billing data ---
    billing_rows = _extract_rows(billing_data)

    # Filter out '(not set)' cluster names to get actual container clusters
    container_rows = [
        r for r in billing_rows
        if r.get("container_cluster_name", "(not set)") != "(not set)"
        and r.get("container_cluster_name", "") != ""
    ]

    # Total container spend from billing
    total_container_spend = sum(
        _safe_float(r.get("unblended_cost")) for r in container_rows
    )

    # Distinct cluster count from billing
    distinct_clusters = set(
        r.get("container_cluster_name", "") for r in container_rows
    )
    cluster_count = len(distinct_clusters)

    # Top clusters by cost (top 20)
    # Group by cluster name first to aggregate across regions
    cluster_costs: dict[str, dict] = {}
    for row in container_rows:
        name = row.get("container_cluster_name", "")
        if name not in cluster_costs:
            cluster_costs[name] = {
                "name": name,
                "vendor": row.get("vendor", _detect_vendor(name)),
                "region": row.get("region", "unknown"),
                "unblended_cost": 0.0,
                "amortized_cost": 0.0,
            }
        cluster_costs[name]["unblended_cost"] += _safe_float(row.get("unblended_cost"))
        cluster_costs[name]["amortized_cost"] += _safe_float(row.get("total_amortized_cost"))

    top_clusters = sorted(
        cluster_costs.values(),
        key=lambda c: c["unblended_cost"],
        reverse=True,
    )[:20]

    # Vendor split from container clusters only
    vendor_split: dict[str, float] = {}
    for row in container_rows:
        vendor = row.get("vendor", _detect_vendor(row.get("container_cluster_name", "")))
        vendor_split[vendor] = vendor_split.get(vendor, 0.0) + _safe_float(
            row.get("unblended_cost")
        )
    # Sort vendor split by cost descending
    vendor_split = dict(sorted(vendor_split.items(), key=lambda x: x[1], reverse=True))

    # Region split (top 10 regions from container clusters)
    region_costs: dict[str, float] = {}
    for row in container_rows:
        region = row.get("region", "unknown")
        region_costs[region] = region_costs.get(region, 0.0) + _safe_float(
            row.get("unblended_cost")
        )
    region_split = dict(
        sorted(region_costs.items(), key=lambda x: x[1], reverse=True)[:10]
    )

    # --- Parse Kubecost data (if available) ---
    kubecost_available = False
    kubecost_clusters: list[dict] = []
    kubecost_namespaces: list[dict] = []
    total_kubecost = 0.0
    total_idle_pct = 0.0

    if kubecost_clusters_raw:
        kubecost_clusters = _parse_kubecost_cluster_response(kubecost_clusters_raw)
        if kubecost_clusters:
            kubecost_available = True
            total_kubecost = sum(c["totalCost"] for c in kubecost_clusters)

            # Weighted average idle % (weighted by cost)
            if total_kubecost > 0:
                weighted_idle = sum(
                    c["totalIdlePct"] * c["totalCost"] for c in kubecost_clusters
                )
                total_idle_pct = round(weighted_idle / total_kubecost, 1)

    if kubecost_namespaces_raw:
        kubecost_namespaces = _parse_kubecost_namespace_response(kubecost_namespaces_raw)

    # Top namespaces by cost (top 30)
    top_namespaces = kubecost_namespaces[:30]

    return {
        # Billing-derived metrics
        "total_container_spend": round(total_container_spend, 2),
        "cluster_count": cluster_count,
        "top_clusters": top_clusters,
        "vendor_split": vendor_split,
        "region_split": region_split,
        # Kubecost-derived metrics
        "kubecost_available": kubecost_available,
        "kubecost_clusters": kubecost_clusters,
        "total_kubecost": round(total_kubecost, 2),
        "total_idle_pct": total_idle_pct,
        "total_efficiency": round(100.0 - total_idle_pct, 1),
        "top_namespaces": top_namespaces,
        # Convenience: single top cluster for KPI card
        "top_cluster": {
            "name": top_clusters[0]["name"] if top_clusters else "N/A",
            "cost": top_clusters[0]["unblended_cost"] if top_clusters else 0.0,
        },
        # Efficiency as 0-1 float (for template comparisons)
        "avg_efficiency": (100.0 - total_idle_pct) / 100.0 if kubecost_available else 0.0,
    }


# ======================================================================
# Main Generator
# ======================================================================


def generate(output_dir: Path | None = None) -> Path:
    """Generate the Kubernetes container cost dashboard.

    Collects data from the Cloudability cost reporting API and Kubecost
    allocation endpoint, processes it into summary metrics, renders an
    HTML dashboard via Jinja2, and writes it to disk.

    Args:
        output_dir: Directory to write the dashboard HTML file.
                    Defaults to <project_root>/output.

    Returns:
        Path to the generated HTML file.
    """
    # Resolve output directory
    if output_dir is None:
        project_root = Path(__file__).parent.parent.parent.parent
        output_dir = project_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("🚀 Container Cost Dashboard Generator")
    print("=" * 50)

    # Initialize client
    client = CloudabilityClient.from_env()

    # Collect all data (each call is individually error-handled)
    kubecost_clusters_raw = _collect_kubecost_clusters(client)
    kubecost_namespaces_raw = _collect_kubecost_namespaces(client)
    billing_data = _collect_billing_cluster_data(client)

    # Process raw data into template context
    print("\n🔄 Processing data...")
    context = _process_data(
        kubecost_clusters_raw=kubecost_clusters_raw,
        kubecost_namespaces_raw=kubecost_namespaces_raw,
        billing_data=billing_data,
    )

    # Add metadata to context
    start, _ = DateHelper.last_n_days(30)
    _, end = DateHelper.current_month()
    context["report_period_start"] = start
    context["report_period_end"] = end
    context["generated_at"] = end

    # Render template
    print("🎨 Rendering dashboard...")
    env = _get_template_env()
    template = env.get_template("containers.html.j2")
    html = template.render(**context)

    # Write output
    output_path = output_dir / "container_dashboard.html"
    output_path.write_text(html, encoding="utf-8")

    print(f"\n✅ Dashboard written to: {output_path}")
    print(f"   Total container spend (billing): ${context['total_container_spend']:,.2f}")
    print(f"   Clusters tracked: {context['cluster_count']}")
    if context["kubecost_available"]:
        print(f"   Kubecost total: ${context['total_kubecost']:,.2f}")
        print(f"   Overall efficiency: {context['total_efficiency']}%")
        print(f"   Overall idle: {context['total_idle_pct']}%")
    else:
        print("   ⚠️  Kubecost data unavailable — showing billing data only")

    return output_path
