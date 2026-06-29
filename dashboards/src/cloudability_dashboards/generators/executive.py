"""Executive Dashboard Generator.

Collects data from the Cloudability API and generates an executive cost
summary HTML dashboard. Each API call is wrapped in error handling so
that a single failure does not crash the entire generation pipeline.

Usage:
    from cloudability_dashboards.generators.executive import generate

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
    # V3 API nests rows under 'results'
    if "results" in report:
        return report["results"] if isinstance(report["results"], list) else []
    # Sometimes data is at top level as a list
    if isinstance(report, list):
        return report
    return []


# ======================================================================
# Data Collection
# ======================================================================


def _collect_current_month_costs(client: CloudabilityClient) -> dict:
    """Fetch current month costs grouped by vendor account."""
    print("📊 Collecting current month costs...")
    start, end = DateHelper.current_month()
    try:
        return client.cost_report(
            dimensions="vendor_account_name",
            metrics="unblended_cost,total_amortized_cost",
            start_date=start,
            end_date=end,
            sort="unblended_costDESC",
            limit=50,
        )
    except Exception as e:
        print(f"  ⚠️  Failed to collect current month costs: {e}")
        return {}


def _collect_previous_month_costs(client: CloudabilityClient) -> dict:
    """Fetch previous month costs grouped by vendor account."""
    print("📊 Collecting previous month costs...")
    start, end = DateHelper.previous_month()
    try:
        return client.cost_report(
            dimensions="vendor_account_name",
            metrics="unblended_cost,total_amortized_cost",
            start_date=start,
            end_date=end,
            sort="unblended_costDESC",
            limit=50,
        )
    except Exception as e:
        print(f"  ⚠️  Failed to collect previous month costs: {e}")
        return {}


def _collect_monthly_trend(client: CloudabilityClient) -> dict:
    """Fetch monthly cost trend for the year to date."""
    print("📈 Collecting monthly trend (YTD)...")
    start, end = DateHelper.year_to_date()
    try:
        return client.cost_report(
            dimensions="month",
            metrics="unblended_cost,total_amortized_cost",
            start_date=start,
            end_date=end,
        )
    except Exception as e:
        print(f"  ⚠️  Failed to collect monthly trend: {e}")
        return {}


def _collect_service_breakdown(client: CloudabilityClient) -> dict:
    """Fetch current month service breakdown."""
    print("🔧 Collecting service breakdown...")
    start, end = DateHelper.current_month()
    try:
        return client.cost_report(
            dimensions="enhanced_service_name,vendor",
            metrics="unblended_cost",
            start_date=start,
            end_date=end,
            sort="unblended_costDESC",
            limit=30,
        )
    except Exception as e:
        print(f"  ⚠️  Failed to collect service breakdown: {e}")
        return {}


def _collect_rightsizing(client: CloudabilityClient) -> dict:
    """Fetch rightsizing recommendations."""
    print("📐 Collecting rightsizing recommendations...")
    try:
        return client.rightsizing(limit=20)
    except Exception as e:
        print(f"  ⚠️  Failed to collect rightsizing data: {e}")
        return {"results": []}


def _collect_anomalies(client: CloudabilityClient) -> dict:
    """Fetch recent anomalies."""
    print("🚨 Collecting anomalies...")
    try:
        return client.anomalies(limit=10)
    except Exception as e:
        print(f"  ⚠️  Failed to collect anomalies: {e}")
        return {"results": []}


def _collect_budgets(client: CloudabilityClient) -> dict:
    """Fetch budget data."""
    print("💰 Collecting budgets...")
    try:
        return client.budgets()
    except Exception as e:
        print(f"  ⚠️  Failed to collect budgets: {e}")
        return {"results": []}


def _collect_commitment_data(client: CloudabilityClient) -> dict:
    """Fetch commitment/reservation cost data."""
    print("📋 Collecting commitment data...")
    start, end = DateHelper.current_month()
    try:
        return client.cost_report(
            dimensions="lease_type,vendor",
            metrics="total_amortized_cost,public_on_demand_cost,unblended_cost",
            start_date=start,
            end_date=end,
            limit=50,
        )
    except Exception as e:
        print(f"  ⚠️  Failed to collect commitment data: {e}")
        return {}


# ======================================================================
# Data Processing
# ======================================================================


def _process_data(
    current_month: dict,
    previous_month: dict,
    monthly_trend: dict,
    service_breakdown: dict,
    rightsizing: dict,
    anomalies: dict,
    budgets: dict,
    commitments: dict,
) -> dict:
    """Transform raw API responses into a context dict for template rendering.

    Returns:
        Dictionary with all computed metrics ready for the Jinja2 template.
    """
    # --- Current month totals ---
    current_rows = _extract_rows(current_month)
    total_spend = sum(_safe_float(r.get("unblended_cost")) for r in current_rows)

    # --- Previous month totals ---
    previous_rows = _extract_rows(previous_month)
    previous_total = sum(_safe_float(r.get("unblended_cost")) for r in previous_rows)

    # --- Month-over-month change ---
    if previous_total > 0:
        mom_change_pct = ((total_spend - previous_total) / previous_total) * 100
    else:
        mom_change_pct = 0.0

    # --- Top accounts ---
    top_accounts = [
        {
            "name": r.get("vendor_account_name", "Unknown"),
            "cost": _safe_float(r.get("unblended_cost")),
            "amortized": _safe_float(r.get("total_amortized_cost")),
        }
        for r in current_rows
    ]

    # --- Monthly trend ---
    trend_rows = _extract_rows(monthly_trend)
    monthly_trend_data = [
        {
            "month": r.get("month", ""),
            "cost": _safe_float(r.get("unblended_cost")),
        }
        for r in trend_rows
    ]

    # --- Top services ---
    service_rows = _extract_rows(service_breakdown)
    top_services = [
        {
            "name": r.get("enhanced_service_name", "Unknown"),
            "vendor": r.get("vendor", "Unknown"),
            "cost": _safe_float(r.get("unblended_cost")),
        }
        for r in service_rows
    ]

    # --- Rightsizing ---
    rs_results = rightsizing.get("results", []) if isinstance(rightsizing, dict) else []
    rightsizing_savings = 0.0
    for rec in rs_results:
        # Savings can be nested under recommendations
        if isinstance(rec, dict):
            recs = rec.get("recommendations", [])
            if isinstance(recs, list):
                for r in recs:
                    rightsizing_savings += _safe_float(r.get("savings"))
            else:
                rightsizing_savings += _safe_float(rec.get("savings"))
    rightsizing_count = len(rs_results)

    # --- Anomalies ---
    anomaly_results = anomalies.get("results", []) if isinstance(anomalies, dict) else []
    if isinstance(anomalies, dict) and "results" not in anomalies:
        # Some responses use a different key
        anomaly_results = anomalies.get("anomalies", [])
    anomaly_count = len(anomaly_results) if isinstance(anomaly_results, list) else 0

    # --- Budget status ---
    budget_results = budgets.get("results", []) if isinstance(budgets, dict) else []
    if isinstance(budgets, dict) and "results" not in budgets:
        budget_results = budgets.get("budgets", [])
    if not isinstance(budget_results, list):
        budget_results = []

    budget_total = len(budget_results)
    budget_at_risk = 0
    budget_exceeded = 0
    for b in budget_results:
        if isinstance(b, dict):
            status = b.get("status", "").lower()
            if status in ("exceeded", "over"):
                budget_exceeded += 1
            elif status in ("at_risk", "warning", "at risk"):
                budget_at_risk += 1

    budget_status = {
        "total": budget_total,
        "at_risk": budget_at_risk,
        "exceeded": budget_exceeded,
    }

    # --- Commitment savings ---
    commitment_rows = _extract_rows(commitments)
    total_on_demand = sum(
        _safe_float(r.get("public_on_demand_cost")) for r in commitment_rows
    )
    total_amortized = sum(
        _safe_float(r.get("total_amortized_cost")) for r in commitment_rows
    )
    commitment_savings = max(total_on_demand - total_amortized, 0.0)

    return {
        "total_spend": total_spend,
        "previous_total": previous_total,
        "mom_change_pct": round(mom_change_pct, 1),
        "top_accounts": top_accounts,
        "monthly_trend": monthly_trend_data,
        "top_services": top_services,
        "rightsizing_savings": rightsizing_savings,
        "rightsizing_count": rightsizing_count,
        "anomaly_count": anomaly_count,
        "budget_status": budget_status,
        "commitment_savings": commitment_savings,
    }


# ======================================================================
# Main Generator
# ======================================================================


def generate(output_dir: Path | None = None) -> Path:
    """Generate the executive cost summary dashboard.

    Collects data from the Cloudability API, processes it into summary
    metrics, renders an HTML dashboard via Jinja2, and writes it to disk.

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

    print("🚀 Executive Dashboard Generator")
    print("=" * 50)

    # Initialize client
    client = CloudabilityClient.from_env()

    # Collect all data (each call is individually error-handled)
    current_month = _collect_current_month_costs(client)
    previous_month = _collect_previous_month_costs(client)
    monthly_trend = _collect_monthly_trend(client)
    service_breakdown = _collect_service_breakdown(client)
    rightsizing_data = _collect_rightsizing(client)
    anomalies_data = _collect_anomalies(client)
    budgets_data = _collect_budgets(client)
    commitment_data = _collect_commitment_data(client)

    # Process raw data into template context
    print("\n🔄 Processing data...")
    context = _process_data(
        current_month=current_month,
        previous_month=previous_month,
        monthly_trend=monthly_trend,
        service_breakdown=service_breakdown,
        rightsizing=rightsizing_data,
        anomalies=anomalies_data,
        budgets=budgets_data,
        commitments=commitment_data,
    )

    # Add metadata to context
    start, end = DateHelper.current_month()
    context["report_period_start"] = start
    context["report_period_end"] = end
    context["generated_at"] = end  # Today's date

    # Render template
    print("🎨 Rendering dashboard...")
    env = _get_template_env()
    template = env.get_template("executive.html.j2")
    html = template.render(**context)

    # Write output
    output_path = output_dir / "executive_dashboard.html"
    output_path.write_text(html, encoding="utf-8")

    print(f"\n✅ Dashboard written to: {output_path}")
    print(f"   Total spend (MTD): ${context['total_spend']:,.2f}")
    print(f"   MoM change: {context['mom_change_pct']:+.1f}%")
    print(f"   Rightsizing opportunities: {context['rightsizing_count']}")
    print(f"   Active anomalies: {context['anomaly_count']}")

    return output_path
