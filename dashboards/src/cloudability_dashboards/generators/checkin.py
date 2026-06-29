"""FinOps Daily Check-in Generator.

Generates a daily standup report in markdown or JSON format, replacing
the Node.js multi-agent daily checkin project. Consolidates six analysis
functions (cost-analysis, anomaly-risk, optimization, forecast-budget,
operations-strategy, actions-insights) into a single coherent pipeline.

Usage:
    from cloudability_dashboards.generators.checkin import generate

    report = generate()
    print(report)
"""

from __future__ import annotations

import calendar
import json
from datetime import date, timedelta
from pathlib import Path

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


def _fmt_currency(amount: float) -> str:
    """Format a number as currency with $ and commas."""
    if abs(amount) >= 1_000_000:
        return f"${amount:,.0f}"
    elif abs(amount) >= 1_000:
        return f"${amount:,.0f}"
    else:
        return f"${amount:,.2f}"


def _fmt_pct(value: float) -> str:
    """Format a percentage with sign."""
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f}%"


def _extract_rows(report: dict) -> list[dict]:
    """Extract row data from a cost report response."""
    if not report:
        return []
    if "results" in report:
        return report["results"] if isinstance(report["results"], list) else []
    if isinstance(report, list):
        return report
    return []



# ======================================================================
# Data Collection
# ======================================================================


def _collect_data(client: CloudabilityClient) -> dict:
    """Gather all data from the Cloudability API.

    Each call is wrapped in try/except so one failure doesn't crash everything.
    """
    today = date.today()
    month_start = today.replace(day=1)
    days_elapsed = (today - month_start).days + 1

    # Previous month same period
    prev_month_start = (month_start - timedelta(days=1)).replace(day=1)
    prev_month_same_day = prev_month_start + timedelta(days=days_elapsed - 1)

    # Week-over-week boundaries
    seven_days_ago = today - timedelta(days=7)
    fourteen_days_ago = today - timedelta(days=14)

    data: dict = {
        "today": today,
        "month_start": month_start,
        "days_elapsed": days_elapsed,
        "days_in_month": calendar.monthrange(today.year, today.month)[1],
    }

    # MTD spend by vendor
    try:
        data["mtd"] = client.cost_report(
            dimensions="vendor",
            metrics="unblended_cost",
            start_date=month_start.isoformat(),
            end_date=today.isoformat(),
        )
    except Exception:
        data["mtd"] = {}

    # Previous month same period
    try:
        data["prev_month"] = client.cost_report(
            dimensions="vendor",
            metrics="unblended_cost",
            start_date=prev_month_start.isoformat(),
            end_date=prev_month_same_day.isoformat(),
        )
    except Exception:
        data["prev_month"] = {}

    # WoW current (last 7 days)
    try:
        data["wow_current"] = client.cost_report(
            dimensions="vendor",
            metrics="unblended_cost",
            start_date=seven_days_ago.isoformat(),
            end_date=today.isoformat(),
        )
    except Exception:
        data["wow_current"] = {}

    # WoW previous (14-7 days ago)
    try:
        data["wow_previous"] = client.cost_report(
            dimensions="vendor",
            metrics="unblended_cost",
            start_date=fourteen_days_ago.isoformat(),
            end_date=seven_days_ago.isoformat(),
        )
    except Exception:
        data["wow_previous"] = {}

    # Top movers by service - current week
    try:
        data["services_current"] = client.cost_report(
            dimensions="enhanced_service_name,vendor",
            metrics="unblended_cost",
            start_date=seven_days_ago.isoformat(),
            end_date=today.isoformat(),
            limit=20,
        )
    except Exception:
        data["services_current"] = {}

    # Top movers by service - previous week
    try:
        data["services_previous"] = client.cost_report(
            dimensions="enhanced_service_name,vendor",
            metrics="unblended_cost",
            start_date=fourteen_days_ago.isoformat(),
            end_date=seven_days_ago.isoformat(),
            limit=20,
        )
    except Exception:
        data["services_previous"] = {}

    # Anomalies
    try:
        data["anomalies"] = client.anomalies(limit=10)
    except Exception:
        data["anomalies"] = {}

    # Rightsizing
    try:
        data["rightsizing"] = client.rightsizing(limit=10)
    except Exception:
        data["rightsizing"] = {}

    # Budgets
    try:
        data["budgets"] = client.budgets()
    except Exception:
        data["budgets"] = {}

    return data



# ======================================================================
# Analysis Functions
# ======================================================================


def _analyze_spend(mtd_data: dict, prev_data: dict, wow_current: dict, wow_previous: dict, days_elapsed: int, days_in_month: int) -> dict:
    """Analyze spend trends: MTD, daily rate, projection, vendor breakdown."""
    mtd_rows = _extract_rows(mtd_data)
    prev_rows = _extract_rows(prev_data)

    # Build vendor cost maps
    mtd_by_vendor: dict[str, float] = {}
    for row in mtd_rows:
        vendor = row.get("vendor", "Unknown")
        cost = _safe_float(row.get("unblended_cost"))
        mtd_by_vendor[vendor] = mtd_by_vendor.get(vendor, 0) + cost

    prev_by_vendor: dict[str, float] = {}
    for row in prev_rows:
        vendor = row.get("vendor", "Unknown")
        cost = _safe_float(row.get("unblended_cost"))
        prev_by_vendor[vendor] = prev_by_vendor.get(vendor, 0) + cost

    mtd_total = sum(mtd_by_vendor.values())
    prev_total = sum(prev_by_vendor.values())
    daily_rate = mtd_total / max(days_elapsed, 1)
    projected = daily_rate * days_in_month

    # Month-over-month change
    mom_change_pct = ((mtd_total - prev_total) / prev_total * 100) if prev_total else 0.0

    # Vendor breakdown with change vs prior
    vendor_breakdown = []
    all_vendors = sorted(set(list(mtd_by_vendor.keys()) + list(prev_by_vendor.keys())))
    for vendor in all_vendors:
        current = mtd_by_vendor.get(vendor, 0)
        previous = prev_by_vendor.get(vendor, 0)
        change_pct = ((current - previous) / previous * 100) if previous else 0.0
        vendor_breakdown.append({
            "vendor": vendor,
            "cost": current,
            "previous": previous,
            "change_pct": change_pct,
        })
    vendor_breakdown.sort(key=lambda x: x["cost"], reverse=True)

    # WoW totals
    wow_curr_total = sum(_safe_float(r.get("unblended_cost")) for r in _extract_rows(wow_current))
    wow_prev_total = sum(_safe_float(r.get("unblended_cost")) for r in _extract_rows(wow_previous))
    wow_change_pct = ((wow_curr_total - wow_prev_total) / wow_prev_total * 100) if wow_prev_total else 0.0

    return {
        "mtd_total": mtd_total,
        "daily_rate": daily_rate,
        "projected": projected,
        "prev_total": prev_total,
        "mom_change_pct": mom_change_pct,
        "wow_change_pct": wow_change_pct,
        "wow_current": wow_curr_total,
        "wow_previous": wow_prev_total,
        "vendor_breakdown": vendor_breakdown,
        "days_elapsed": days_elapsed,
        "days_in_month": days_in_month,
    }


def _analyze_movers(current_services: dict, previous_services: dict) -> list:
    """Identify top service movers week-over-week."""
    curr_rows = _extract_rows(current_services)
    prev_rows = _extract_rows(previous_services)

    # Build service cost maps (keyed by service+vendor)
    curr_map: dict[str, dict] = {}
    for row in curr_rows:
        key = f"{row.get('enhanced_service_name', 'Unknown')}|{row.get('vendor', '')}"
        curr_map[key] = {
            "service": row.get("enhanced_service_name", "Unknown"),
            "vendor": row.get("vendor", "Unknown"),
            "cost": _safe_float(row.get("unblended_cost")),
        }

    prev_map: dict[str, float] = {}
    for row in prev_rows:
        key = f"{row.get('enhanced_service_name', 'Unknown')}|{row.get('vendor', '')}"
        prev_map[key] = _safe_float(row.get("unblended_cost"))

    movers = []
    for key, info in curr_map.items():
        prev_cost = prev_map.get(key, 0)
        curr_cost = info["cost"]
        abs_change = curr_cost - prev_cost
        pct_change = ((curr_cost - prev_cost) / prev_cost * 100) if prev_cost else 0.0
        movers.append({
            "service": info["service"],
            "vendor": info["vendor"],
            "current_cost": curr_cost,
            "previous_cost": prev_cost,
            "abs_change": abs_change,
            "pct_change": pct_change,
        })

    # Sort by absolute change descending
    movers.sort(key=lambda x: abs(x["abs_change"]), reverse=True)
    return movers[:10]


def _analyze_anomalies(anomalies_data: dict) -> dict:
    """Analyze anomalies: count, severity breakdown, top items."""
    results = []
    if isinstance(anomalies_data, dict):
        results = anomalies_data.get("results", anomalies_data.get("anomalies", []))
    elif isinstance(anomalies_data, list):
        results = anomalies_data

    if not isinstance(results, list):
        results = []

    critical = [a for a in results if _safe_float(a.get("unusualSpend", a.get("unusual_spend", 0))) >= 10000]
    warning = [a for a in results if a not in critical and _safe_float(a.get("unusualSpend", a.get("unusual_spend", 0))) >= 1000]

    top_items = []
    for a in results[:5]:
        top_items.append({
            "dimension": a.get("dimensionValue", a.get("dimension_value", "Unknown")),
            "spend": _safe_float(a.get("unusualSpend", a.get("unusual_spend", 0))),
            "date": a.get("date", a.get("anomalyDate", "N/A")),
        })

    return {
        "total_count": len(results),
        "critical_count": len(critical),
        "warning_count": len(warning),
        "top_items": top_items,
    }


def _analyze_rightsizing(rightsizing_data: dict) -> dict:
    """Analyze rightsizing: total savings, top recs."""
    results = []
    if isinstance(rightsizing_data, dict):
        results = rightsizing_data.get("results", [])
    elif isinstance(rightsizing_data, list):
        results = rightsizing_data

    if not isinstance(results, list):
        results = []

    # Extract savings from each recommendation
    recs = []
    for r in results:
        recommendations = r.get("recommendations", [])
        if isinstance(recommendations, list) and recommendations:
            best = recommendations[0]
            savings = _safe_float(best.get("savings", 0))
        else:
            savings = _safe_float(r.get("potentialSavings", r.get("potential_savings", 0)))

        recs.append({
            "resource": r.get("resourceName", r.get("resource_name", r.get("resourceId", "Unknown"))),
            "service": r.get("vendorService", r.get("vendor_service", "Unknown")),
            "action": recommendations[0].get("action", "Rightsize") if recommendations else r.get("action", "Rightsize"),
            "savings": savings,
        })

    recs.sort(key=lambda x: x["savings"], reverse=True)
    total_savings = sum(r["savings"] for r in recs)

    return {
        "total_savings": total_savings,
        "count": len(recs),
        "top_recs": recs[:5],
    }


def _analyze_budgets(budgets_data: dict) -> dict:
    """Analyze budgets: at-risk and exceeded."""
    results = []
    if isinstance(budgets_data, dict):
        results = budgets_data.get("results", budgets_data.get("budgets", []))
    elif isinstance(budgets_data, list):
        results = budgets_data

    if not isinstance(results, list):
        results = []

    exceeded = []
    at_risk = []
    healthy = []

    for b in results:
        name = b.get("name", "Unnamed")
        # Try to get current month threshold and actual
        months = b.get("months", [])
        threshold = 0.0
        actual = _safe_float(b.get("actual", b.get("currentSpend", 0)))

        # Find current month threshold
        today = date.today()
        current_month_key = today.strftime("%Y-%m")
        for m in months:
            if m.get("month", "") == current_month_key:
                threshold = _safe_float(m.get("threshold", 0))
                break

        if not threshold:
            threshold = _safe_float(b.get("threshold", b.get("budget", 0)))

        utilization = (actual / threshold * 100) if threshold else 0.0

        entry = {"name": name, "threshold": threshold, "actual": actual, "utilization": utilization}

        if utilization >= 100:
            exceeded.append(entry)
        elif utilization >= 80:
            at_risk.append(entry)
        else:
            healthy.append(entry)

    return {
        "total_count": len(results),
        "exceeded": exceeded,
        "at_risk": at_risk,
        "healthy_count": len(healthy),
    }



# ======================================================================
# Priority Actions
# ======================================================================


def _build_priority_actions(spend: dict, movers: list, anomalies: dict, rightsizing: dict) -> list:
    """Build top 3-5 priority actions ranked by impact."""
    actions = []

    # From anomalies - critical ones become priority actions
    for item in anomalies.get("top_items", [])[:2]:
        if item["spend"] >= 1000:
            actions.append({
                "severity": "🔴" if item["spend"] >= 10000 else "🟡",
                "title": f"Anomaly: {item['dimension']}",
                "impact": item["spend"],
                "type": "anomaly",
                "detail": f"Unusual spend of {_fmt_currency(item['spend'])} detected on {item['date']}",
            })

    # From movers - big week-over-week increases
    for mover in movers[:3]:
        if mover["abs_change"] > 0 and mover["pct_change"] >= 20:
            actions.append({
                "severity": "🟡" if mover["pct_change"] < 50 else "🔴",
                "title": f"Spike: {mover['service']} ({mover['vendor']})",
                "impact": mover["abs_change"],
                "type": "cost_spike",
                "detail": f"{_fmt_pct(mover['pct_change'])} WoW ({_fmt_currency(mover['abs_change'])} increase)",
            })

    # From rightsizing - stale savings opportunities
    if rightsizing.get("total_savings", 0) >= 1000:
        actions.append({
            "severity": "🟡",
            "title": f"Rightsizing: {_fmt_currency(rightsizing['total_savings'])} available",
            "impact": rightsizing["total_savings"],
            "type": "optimization",
            "detail": f"{rightsizing['count']} recommendations pending",
        })

    # From spend - month projection significantly above prior
    if spend.get("mom_change_pct", 0) >= 15:
        actions.append({
            "severity": "🟡",
            "title": f"Month trending {_fmt_pct(spend['mom_change_pct'])} vs prior",
            "impact": spend.get("projected", 0) - spend.get("prev_total", 0),
            "type": "trend",
            "detail": f"Projected: {_fmt_currency(spend.get('projected', 0))}",
        })

    # Sort by impact and take top 5
    actions.sort(key=lambda x: x["impact"], reverse=True)
    return actions[:5]


# ======================================================================
# Markdown Formatter
# ======================================================================


def _format_markdown(spend: dict, movers: list, anomalies: dict, rightsizing: dict, budgets: dict, priorities: list) -> str:
    """Format the full report as markdown."""
    today = date.today()
    lines: list[str] = []

    # Header
    lines.append(f"# 📋 FinOps Daily Check-in — {today.strftime('%A, %B %d, %Y')}")
    lines.append("")

    # ── Priority Actions ──────────────────────────────────────────────
    lines.append("## ⚡ Priority Actions")
    lines.append("")
    if priorities:
        lines.append("| # | Severity | Action | Impact | Detail |")
        lines.append("|---|----------|--------|--------|--------|")
        for i, p in enumerate(priorities, 1):
            lines.append(f"| {i} | {p['severity']} | {p['title']} | {_fmt_currency(p['impact'])} | {p['detail']} |")
    else:
        lines.append("✅ No critical actions today.")
    lines.append("")

    # ── INFORM ────────────────────────────────────────────────────────
    lines.append("## 👁️ INFORM — Spend Snapshot")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| MTD Total | {_fmt_currency(spend.get('mtd_total', 0))} |")
    lines.append(f"| Daily Rate | {_fmt_currency(spend.get('daily_rate', 0))} |")
    lines.append(f"| Month Projection | {_fmt_currency(spend.get('projected', 0))} |")
    lines.append(f"| vs Prior Month (same period) | {_fmt_pct(spend.get('mom_change_pct', 0))} |")
    lines.append(f"| WoW Change | {_fmt_pct(spend.get('wow_change_pct', 0))} |")
    lines.append(f"| Days Elapsed | {spend.get('days_elapsed', 0)}/{spend.get('days_in_month', 30)} |")
    lines.append("")

    # Vendor breakdown
    lines.append("### Provider Breakdown")
    lines.append("")
    vendor_list = spend.get("vendor_breakdown", [])
    if vendor_list:
        lines.append("| Vendor | MTD Cost | vs Prior | Change |")
        lines.append("|--------|----------|----------|--------|")
        for v in vendor_list:
            lines.append(f"| {v['vendor']} | {_fmt_currency(v['cost'])} | {_fmt_currency(v['previous'])} | {_fmt_pct(v['change_pct'])} |")
    lines.append("")

    # Top movers
    if movers:
        lines.append("### Top Service Movers (WoW)")
        lines.append("")
        lines.append("| Service | Vendor | This Week | Last Week | Change |")
        lines.append("|---------|--------|-----------|-----------|--------|")
        for m in movers[:7]:
            lines.append(
                f"| {m['service']} | {m['vendor']} | "
                f"{_fmt_currency(m['current_cost'])} | {_fmt_currency(m['previous_cost'])} | "
                f"{_fmt_pct(m['pct_change'])} |"
            )
        lines.append("")

    # ── OPTIMIZE ──────────────────────────────────────────────────────
    lines.append("## ⚡ OPTIMIZE — Rightsizing")
    lines.append("")
    lines.append(f"**Total Potential Savings:** {_fmt_currency(rightsizing.get('total_savings', 0))}")
    lines.append(f"  \n**Recommendations:** {rightsizing.get('count', 0)}")
    lines.append("")

    top_recs = rightsizing.get("top_recs", [])
    if top_recs:
        lines.append("| Resource | Service | Action | Savings |")
        lines.append("|----------|---------|--------|---------|")
        for r in top_recs:
            lines.append(f"| {r['resource'][:40]} | {r['service']} | {r['action']} | {_fmt_currency(r['savings'])} |")
    lines.append("")

    # ── OPERATE ───────────────────────────────────────────────────────
    lines.append("## 🏦 OPERATE — Budget & Anomaly Health")
    lines.append("")

    # Budget health
    lines.append("### Budget Health")
    lines.append("")
    exceeded = budgets.get("exceeded", [])
    at_risk = budgets.get("at_risk", [])

    if exceeded:
        lines.append("**🔴 Exceeded:**")
        lines.append("")
        lines.append("| Budget | Spend | Threshold | Utilization |")
        lines.append("|--------|-------|-----------|-------------|")
        for b in exceeded:
            lines.append(f"| {b['name']} | {_fmt_currency(b['actual'])} | {_fmt_currency(b['threshold'])} | {b['utilization']:.0f}% |")
        lines.append("")

    if at_risk:
        lines.append("**🟡 At Risk (>80%):**")
        lines.append("")
        lines.append("| Budget | Spend | Threshold | Utilization |")
        lines.append("|--------|-------|-----------|-------------|")
        for b in at_risk:
            lines.append(f"| {b['name']} | {_fmt_currency(b['actual'])} | {_fmt_currency(b['threshold'])} | {b['utilization']:.0f}% |")
        lines.append("")

    if not exceeded and not at_risk:
        lines.append(f"✅ All {budgets.get('total_count', 0)} budgets healthy.")
        lines.append("")

    # Anomaly triage
    lines.append("### Anomaly Triage")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Detected | {anomalies.get('total_count', 0)} |")
    lines.append(f"| 🔴 Critical (≥$10k) | {anomalies.get('critical_count', 0)} |")
    lines.append(f"| 🟡 Warning (≥$1k) | {anomalies.get('warning_count', 0)} |")
    lines.append("")

    top_anomalies = anomalies.get("top_items", [])
    if top_anomalies:
        lines.append("| Dimension | Unusual Spend | Date |")
        lines.append("|-----------|---------------|------|")
        for a in top_anomalies:
            lines.append(f"| {a['dimension']} | {_fmt_currency(a['spend'])} | {a['date']} |")
        lines.append("")

    # ── INSIGHT ───────────────────────────────────────────────────────
    lines.append("## 💡 Insight")
    lines.append("")
    insight = _generate_insight(spend, movers, anomalies, rightsizing, budgets)
    lines.append(insight)
    lines.append("")

    return "\n".join(lines)


def _generate_insight(spend: dict, movers: list, anomalies: dict, rightsizing: dict, budgets: dict) -> str:
    """Generate the #1 narrative takeaway."""
    parts = []

    # Lead with spend trend
    mom = spend.get("mom_change_pct", 0)
    if abs(mom) >= 10:
        direction = "up" if mom > 0 else "down"
        parts.append(
            f"Month-to-date spend is trending **{_fmt_pct(mom)}** vs the same period last month "
            f"(projected {_fmt_currency(spend.get('projected', 0))})."
        )
    else:
        parts.append(
            f"Spend is tracking close to last month ({_fmt_pct(mom)}), "
            f"with a projected finish of {_fmt_currency(spend.get('projected', 0))}."
        )

    # Add optimization opportunity if significant
    savings = rightsizing.get("total_savings", 0)
    if savings >= 5000:
        parts.append(
            f"There's {_fmt_currency(savings)} in rightsizing savings on the table "
            f"across {rightsizing.get('count', 0)} recommendations — consider prioritizing the top items."
        )

    # Add anomaly alert if present
    if anomalies.get("critical_count", 0) > 0:
        parts.append(
            f"⚠️ {anomalies['critical_count']} critical anomalies detected that need immediate attention."
        )

    return " ".join(parts) if parts else "No significant changes detected. Steady state."



# ======================================================================
# JSON Formatter
# ======================================================================


def _format_json(spend: dict, movers: list, anomalies: dict, rightsizing: dict, budgets: dict, priorities: list) -> str:
    """Format the full report as JSON."""
    report = {
        "date": date.today().isoformat(),
        "priority_actions": priorities,
        "spend": spend,
        "movers": movers,
        "anomalies": anomalies,
        "rightsizing": rightsizing,
        "budgets": budgets,
    }
    return json.dumps(report, indent=2, default=str)


# ======================================================================
# Main Entry Point
# ======================================================================


def generate(output_format: str = "markdown", output_dir: Path | None = None) -> str:
    """Generate daily check-in report.

    Args:
        output_format: 'markdown' (default) or 'json'
        output_dir: If provided, also write to file

    Returns:
        The report as a string (markdown or JSON)
    """
    client = CloudabilityClient.from_env()

    try:
        # 1. Collect all data
        data = _collect_data(client)

        # 2. Analyze each domain
        spend = _analyze_spend(
            mtd_data=data["mtd"],
            prev_data=data["prev_month"],
            wow_current=data["wow_current"],
            wow_previous=data["wow_previous"],
            days_elapsed=data["days_elapsed"],
            days_in_month=data["days_in_month"],
        )

        movers = _analyze_movers(
            current_services=data["services_current"],
            previous_services=data["services_previous"],
        )

        anomalies = _analyze_anomalies(data["anomalies"])
        rightsizing_analysis = _analyze_rightsizing(data["rightsizing"])
        budgets_analysis = _analyze_budgets(data["budgets"])

        # 3. Build priority actions from combined analysis
        priorities = _build_priority_actions(spend, movers, anomalies, rightsizing_analysis)

        # 4. Format output
        if output_format == "json":
            report = _format_json(spend, movers, anomalies, rightsizing_analysis, budgets_analysis, priorities)
        else:
            report = _format_markdown(spend, movers, anomalies, rightsizing_analysis, budgets_analysis, priorities)

        # 5. Optionally write to file
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            ext = "json" if output_format == "json" else "md"
            filename = f"checkin-{date.today().isoformat()}.{ext}"
            filepath = output_dir / filename
            filepath.write_text(report, encoding="utf-8")

        return report

    finally:
        client.close()
