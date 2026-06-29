"""Multi-Cloud Architecture Dashboard Generator.

Generates a multi-cloud architecture breakdown dashboard showing:
- Cloud vendor cost split (AWS, Azure, OCI, GCP, Snowflake, Databricks, MongoDB)
- Service type classification (IaaS, PaaS, Containers, AI/ML, Other)
- Chip architecture breakdown (Intel, AMD, Graviton/ARM, NVIDIA GPU, ARM Ampere)

Usage:
    from cloudability_dashboards.generators.multicloud import generate

    path = generate()
    print(f"Dashboard written to {path}")
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from cloudability_dashboards.client import CloudabilityClient, DateHelper


# ======================================================================
# Service Classifications
# ======================================================================

SERVICE_CLASSIFICATIONS: dict[str, str] = {
    # AWS - IaaS
    "amazon elastic compute cloud": "iaas",
    "amazon virtual private cloud": "iaas",
    "amazon elastic block store": "iaas",
    "elastic load balancing": "iaas",
    "aws elastic load balancing": "iaas",
    "amazon route 53": "iaas",
    "aws direct connect": "iaas",
    "amazon lightsail": "iaas",
    "aws global accelerator": "iaas",
    "aws transit gateway": "iaas",
    "aws vpn": "iaas",
    "amazon workspaces": "iaas",
    "aws outposts": "iaas",
    "aws storage gateway": "iaas",
    "amazon elastic file system": "iaas",
    "amazon fsx": "iaas",
    "amazon simple storage service": "iaas",
    "amazon s3 glacier": "iaas",
    "aws backup": "iaas",
    "amazon cloudfront": "iaas",
    "aws shield": "iaas",
    "aws waf": "iaas",
    "aws data transfer": "iaas",
    "aws network firewall": "iaas",
    "savings plans for aws compute usage": "iaas",
    # AWS - PaaS
    "amazon relational database service": "paas",
    "amazon dynamodb": "paas",
    "amazon aurora": "paas",
    "aws lambda": "paas",
    "amazon simple queue service": "paas",
    "amazon simple notification service": "paas",
    "amazon kinesis": "paas",
    "amazon kinesis data firehose": "paas",
    "amazon redshift": "paas",
    "amazon elasticache": "paas",
    "amazon opensearch service": "paas",
    "amazon memorydb": "paas",
    "amazon neptune": "paas",
    "amazon documentdb": "paas",
    "amazon managed streaming for apache kafka": "paas",
    "amazon mq": "paas",
    "aws step functions": "paas",
    "amazon api gateway": "paas",
    "aws elastic beanstalk": "paas",
    "amazon eventbridge": "paas",
    "aws glue": "paas",
    "amazon athena": "paas",
    "amazon quicksight": "paas",
    "amazon emr": "paas",
    "amazon elastic mapreduce": "paas",
    "aws secrets manager": "paas",
    "amazoncloudwatch": "paas",
    "aws cloudtrail": "paas",
    "aws config": "paas",
    "aws systems manager": "paas",
    "aws codecommit": "paas",
    "aws codebuild": "paas",
    "aws codepipeline": "paas",
    "aws key management service": "paas",
    "amazon guardduty": "paas",
    "aws support (enterprise)": "paas",
    "savings plans for aws database usage": "paas",
    "amazon ses": "paas",
    "kiro": "paas",
    # AWS - Containers
    "amazon elastic container service": "containers",
    "amazon elastic kubernetes service": "containers",
    "amazon elastic container service for kubernetes": "containers",
    "amazon ec2 container registry (ecr)": "containers",
    "aws fargate": "containers",
    # AWS - AI
    "amazon sagemaker": "ai",
    "amazon bedrock": "ai",
    "amazon rekognition": "ai",
    "amazon comprehend": "ai",
    "amazon transcribe": "ai",
    "amazon translate": "ai",
    "amazon lex": "ai",
    "amazon textract": "ai",
    "amazon personalize": "ai",
    "amazon kendra": "ai",
    "amazon q": "ai",
    # Azure - IaaS
    "microsoft.compute": "iaas",
    "microsoft.capacity": "iaas",
    "microsoft.storage": "iaas",
    "microsoft.network": "iaas",
    "microsoft.recoveryservices": "iaas",
    "virtual network": "iaas",
    "microsoft.cdn": "iaas",
    # Azure - PaaS
    "microsoft.sql": "paas",
    "microsoft.dbforpostgresql": "paas",
    "microsoft.dbformysql": "paas",
    "microsoft.synapse": "paas",
    "microsoft.databricks": "paas",
    "microsoft.operationalinsights": "paas",
    "microsoft.web": "paas",
    "microsoft.insights": "paas",
    "microsoft.eventhub": "paas",
    "microsoft.servicebus": "paas",
    "microsoft.search": "paas",
    "microsoft.cache": "paas",
    "microsoft.documentdb": "paas",
    "microsoft.fabric": "paas",
    "microsoft.powerbidedicated": "paas",
    "microsoft.visualstudio": "paas",
    "microsoft.communication": "paas",
    "api management": "paas",
    "github": "paas",
    # Azure - Containers
    "microsoft.app": "containers",
    "microsoft.containerregistry": "containers",
    "microsoft.containerservice": "containers",
    # Azure - AI
    "microsoft.cognitiveservices": "ai",
    "microsoft.machinelearningservices": "ai",
    "anthropic::azure plan": "ai",
    # Azure marketplace / 3rd party
    "celonis se::celonis platform": "paas",
    "reltio::enterprise 360": "paas",
    "data dynamics inc.::azure plan": "paas",
    "netapp::azure plan": "iaas",
    "elastic::azure plan": "paas",
    # GCP - IaaS
    "gcp compute engine": "iaas",
    "gcp cloud storage": "iaas",
    "gcp networking": "iaas",
    "gcp netapp volumes": "iaas",
    "gcp backup and dr service": "iaas",
    # GCP - PaaS
    "gcp cloud sql": "paas",
    "gcp bigquery": "paas",
    "gcp bigquery reservation api": "paas",
    "gcp app engine": "paas",
    "gcp cloud logging": "paas",
    "gcp support": "paas",
    "gcp mongodb atlas 2 (private offer)": "paas",
    # GCP - Containers
    "gcp cloud run": "containers",
    # GCP - AI
    "gcp vertex ai": "ai",
    # OCI - IaaS
    "compute": "iaas",
    "block storage": "iaas",
    "objectstore": "iaas",
    "filestorageservice": "iaas",
    # NOTE: "virtual network" already mapped above (shared key with Azure)
    "cloud success protection service": "paas",
    # OCI - PaaS
    "database": "paas",
    "opensearch": "paas",
    "mysql": "paas",
    "oralb": "paas",
    "secure desktops": "iaas",
    # Snowflake
    "warehouse_metering": "paas",
    "storage": "paas",
    # MongoDB
    "atlas_support": "paas",
    "atlas_nds_azure_pit_restore_storage": "paas",
    "atlas_aws_instance_m50": "paas",
    "atlas_aws_instance_m40": "paas",
    "atlas_aws_instance_m30": "paas",
    "atlas_aws_instance_m60": "paas",
    "atlas_aws_instance_m80": "paas",
    "atlas_aws_instance_m140": "paas",
    "atlas_aws_storage_standard": "paas",
    "atlas_aws_backup_snapshot_storage": "paas",
    "atlas_azure_standard_storage": "paas",
    "atlas_azure_backup_snapshot_storage": "paas",
    "atlas_azure_instance_m80": "paas",
    "atlas_nds_aws_pit_restore_storage": "paas",
    # Databricks
    "databricks": "ai",
}


# ======================================================================
# Chip Architecture Patterns
# ======================================================================

# Each entry: architecture name -> list of (compiled_regex, vendor_filter)
# vendor_filter is None for all vendors, or a specific vendor string.
CHIP_PATTERNS: dict[str, list[tuple[re.Pattern, str | None]]] = {
    "Graviton (ARM)": [
        (re.compile(r"^(m[6-8]g|m[6-8]gd|c[6-8]g|c[6-8]gd|c[6-8]gn|r[6-8]g|r[6-8]gd|t4g|x2gd|im4gn|is4gen|i[48]g|hpc7g|g5g)\."), "Amazon"),
    ],
    "AMD": [
        (re.compile(r"^(m[5-7]a|m[5-7]ad|c[5-7]a|c[5-7]ad|r[5-7]a|r[5-7]ad|t3a|hpc[67]a|g4ad)\."), "Amazon"),
        (re.compile(r"Standard_(D|E)\d+a[sd]*_(v[3-6]|v5)"), "Azure"),
        (re.compile(r"Standard_L\d+as"), "Azure"),
        (re.compile(r"Standard_NC\d+as_T4"), "Azure"),
        (re.compile(r"Standard_NV\d+a"), "Azure"),
        (re.compile(r"Standard_ND\d+a"), "Azure"),
        (re.compile(r"Standard_D\d+ads"), "Azure"),
        (re.compile(r"Standard_E\d+a"), "Azure"),
        (re.compile(r"^(n2d|c2d|t2d|c3d|c4d|n4d|h4d)"), "GCP"),
        (re.compile(r"Standard\.E[2-5]"), "OCI"),
        (re.compile(r"Standard\.E\d+\.Flex"), "OCI"),
    ],
    "Intel": [
        (re.compile(r"^(m[5-8](d|n|dn|zn)?|m[6-8]i|m7i-flex|m8i)\."), "Amazon"),
        (re.compile(r"^(c[5-8](d|n)?|c[6-8]i|c7i-flex|c8i)\."), "Amazon"),
        (re.compile(r"^(r[5-8](d|n|dn|b)?|r[6-8]i|r7iz|r8i)\."), "Amazon"),
        (re.compile(r"^(t3|i3|i3en|i4i|d[23]|d3en|h1|z1d|x1|x1e|x2i|u-)\.?"), "Amazon"),
        (re.compile(r"^(p3|dl1|f1|hpc6id|mac1|ra3)\."), "Amazon"),
        (re.compile(r"^(m5|c5|r5|r4)\.\d*x?large"), "Amazon"),
        (re.compile(r"Standard_(D|E|F|M|L|H|B)\d+[_\-]?\d*[cilmst]*s?_v[2-6]$"), "Azure"),
        (re.compile(r"Standard_D\d+s_v[3-5]$"), "Azure"),
        (re.compile(r"Standard_D\d+_v[2-5]$"), "Azure"),
        (re.compile(r"Standard_DS\d+_v\d+$"), "Azure"),
        (re.compile(r"Standard_E\d+d?s?_v[3-6]$"), "Azure"),
        (re.compile(r"Standard_F\d+s?_v2$"), "Azure"),
        (re.compile(r"Standard_B\d+"), "Azure"),
        (re.compile(r"Standard_D\d+lds"), "Azure"),
        (re.compile(r"Standard_D\d+s_v[3-6]$"), "Azure"),
        (re.compile(r"Standard_D\d+d_v5"), "Azure"),
        (re.compile(r"Standard_A\d+m?_v2"), "Azure"),
        (re.compile(r"^(n[12]|c[234]|n4|m[1234]|e2|x4|z3|h3)[\-\.]"), "GCP"),
        (re.compile(r"standard\.(e2|n1|n2|c2|c3)\-"), "GCP"),
        (re.compile(r"highmem\.(n1|n2|e2)"), "GCP"),
        (re.compile(r"custom\.(e2|n1|n2)"), "GCP"),
        (re.compile(r"node\.(n1|c2)"), "GCP"),
        (re.compile(r"sharedcore\.e2"), "GCP"),
        (re.compile(r"Standard[23]"), "OCI"),
        (re.compile(r"Standard\.Intel"), "OCI"),
        (re.compile(r"Optimized3"), "OCI"),
        (re.compile(r"Optimized\.X9"), "OCI"),
        (re.compile(r"Standard\.X9"), "OCI"),
        (re.compile(r"DenseIO2"), "OCI"),
        (re.compile(r"HPC2"), "OCI"),
    ],
    "NVIDIA GPU": [
        (re.compile(r"^(p[4-5]|p4d|p4de|p5e?n?|g[4-6]|g4dn|g5|g6e?|inf[12]|trn[12]|dl[12])\."), "Amazon"),
        (re.compile(r"Standard_NC\d+"), "Azure"),
        (re.compile(r"Standard_ND\d+"), "Azure"),
        (re.compile(r"Standard_NV\d+"), "Azure"),
        (re.compile(r"^(a[234]|g[24])[\-\.]"), "GCP"),
        (re.compile(r"GPU\.A10"), "OCI"),
        (re.compile(r"GPU\d*"), "OCI"),
    ],
    "ARM (Ampere/Other)": [
        (re.compile(r"Standard_(D|E)\d+p"), "Azure"),
        (re.compile(r"^t2a"), "GCP"),
        (re.compile(r"^(c4a|n4a)"), "GCP"),
        (re.compile(r"Standard\.A[1-4]"), "OCI"),
    ],
}


# ======================================================================
# Classification Functions
# ======================================================================


def classify_service(service_name: str, vendor: str) -> str:
    """Classify a cloud service into a category.

    Args:
        service_name: The enhanced service name from the cost report.
        vendor: The cloud vendor name.

    Returns:
        One of: 'iaas', 'paas', 'containers', 'ai', 'other'.
    """
    key = service_name.lower().strip()

    # Direct lookup
    if key in SERVICE_CLASSIFICATIONS:
        return SERVICE_CLASSIFICATIONS[key]

    # Fuzzy matching for Azure case variations
    lower_key = re.sub(r"^microsoft\.", "microsoft.", key, flags=re.IGNORECASE)
    if lower_key in SERVICE_CLASSIFICATIONS:
        return SERVICE_CLASSIFICATIONS[lower_key]

    # MongoDB Atlas catch-all
    if key.startswith("atlas_"):
        return "paas"

    # Snowflake catch-all
    if vendor == "Snowflake":
        return "paas"

    # Databricks catch-all
    if vendor == "Databricks":
        return "ai"

    return "other"


def classify_chip(instance_type: str, vendor: str) -> str | None:
    """Classify an instance type into a chip architecture.

    Args:
        instance_type: The instance type string (e.g. 'm5.xlarge', 'Standard_D4s_v3').
        vendor: The cloud vendor name.

    Returns:
        Architecture name (e.g. 'Intel', 'AMD', 'Graviton (ARM)') or None
        if the instance type is empty/unset.
    """
    if not instance_type or instance_type == "(not set)":
        return None

    for arch, patterns in CHIP_PATTERNS.items():
        for regex, vendor_filter in patterns:
            if vendor_filter and vendor_filter != vendor:
                continue
            if regex.search(instance_type):
                return arch

    return "Other/Unknown"


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


# ======================================================================
# Data Collection
# ======================================================================


def _collect_vendor_breakdown(client: CloudabilityClient) -> dict:
    """Fetch current month costs grouped by vendor."""
    print("☁️  Collecting vendor breakdown...")
    start, end = DateHelper.current_month()
    try:
        return client.cost_report(
            dimensions="vendor",
            metrics="unblended_cost",
            start_date=start,
            end_date=end,
            sort="unblended_costDESC",
        )
    except Exception as e:
        print(f"  ⚠️  Failed to collect vendor breakdown: {e}")
        return {}


def _collect_service_breakdown(client: CloudabilityClient) -> dict:
    """Fetch current month costs grouped by service and vendor."""
    print("🔧 Collecting service breakdown...")
    start, end = DateHelper.current_month()
    try:
        return client.cost_report(
            dimensions="enhanced_service_name,vendor",
            metrics="unblended_cost",
            start_date=start,
            end_date=end,
            sort="unblended_costDESC",
            limit=500,
        )
    except Exception as e:
        print(f"  ⚠️  Failed to collect service breakdown: {e}")
        return {}


def _collect_instance_types(client: CloudabilityClient) -> dict:
    """Fetch current month costs grouped by instance type and vendor."""
    print("🖥️  Collecting instance type data...")
    start, end = DateHelper.current_month()
    try:
        return client.cost_report(
            dimensions="instance_type,vendor",
            metrics="unblended_cost",
            start_date=start,
            end_date=end,
            sort="unblended_costDESC",
            limit=500,
        )
    except Exception as e:
        print(f"  ⚠️  Failed to collect instance type data: {e}")
        return {}


# ======================================================================
# Data Processing
# ======================================================================


def _process_vendor_breakdown(report: dict) -> list[dict]:
    """Process vendor report into [{vendor, cost, pct}]."""
    rows = _extract_rows(report)
    total = sum(_safe_float(r.get("unblended_cost")) for r in rows)

    result = []
    for row in rows:
        vendor = row.get("vendor", "Unknown")
        cost = _safe_float(row.get("unblended_cost"))
        pct = (cost / total * 100) if total > 0 else 0.0
        result.append({
            "vendor": vendor,
            "cost": cost,
            "pct": round(pct, 1),
        })

    return result


def _process_service_types(report: dict) -> dict[str, float]:
    """Process service report into {iaas: $X, paas: $Y, ...}."""
    rows = _extract_rows(report)
    totals: dict[str, float] = {
        "iaas": 0.0,
        "paas": 0.0,
        "containers": 0.0,
        "ai": 0.0,
        "other": 0.0,
    }

    for row in rows:
        service_name = row.get("enhanced_service_name", "")
        vendor = row.get("vendor", "")
        cost = _safe_float(row.get("unblended_cost"))
        category = classify_service(service_name, vendor)
        totals[category] += cost

    return totals


def _process_chip_breakdown(report: dict) -> dict[str, float]:
    """Process instance type report into chip architecture breakdown."""
    rows = _extract_rows(report)
    totals: dict[str, float] = {
        "Intel": 0.0,
        "AMD": 0.0,
        "Graviton (ARM)": 0.0,
        "NVIDIA GPU": 0.0,
        "ARM (Ampere/Other)": 0.0,
    }

    for row in rows:
        instance_type = row.get("instance_type", "")
        vendor = row.get("vendor", "")
        cost = _safe_float(row.get("unblended_cost"))

        arch = classify_chip(instance_type, vendor)
        if arch is None:
            # Skip rows with no instance type
            continue
        if arch in totals:
            totals[arch] += cost
        else:
            # 'Other/Unknown' goes nowhere — we only report named architectures
            pass

    return totals


# ======================================================================
# Main Generator
# ======================================================================


def generate(output_dir: Path | None = None) -> Path:
    """Generate the multi-cloud architecture dashboard.

    Collects vendor, service, and instance type data from the Cloudability
    API, classifies services and chip architectures, renders an HTML
    dashboard via Jinja2, and writes it to disk.

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

    print("🚀 Multi-Cloud Architecture Dashboard Generator")
    print("=" * 50)

    # Initialize client
    client = CloudabilityClient.from_env()

    # Collect all data
    vendor_report = _collect_vendor_breakdown(client)
    service_report = _collect_service_breakdown(client)
    instance_report = _collect_instance_types(client)

    # Process data
    print("\n🔄 Processing data...")
    vendor_breakdown = _process_vendor_breakdown(vendor_report)
    service_types = _process_service_types(service_report)
    chip_breakdown = _process_chip_breakdown(instance_report)

    # Build top_services list from service report
    top_services = []
    for row in _extract_rows(service_report)[:30]:
        name = row.get("enhanced_service_name", "Unknown")
        vendor = row.get("vendor", "")
        cost = _safe_float(row.get("unblended_cost"))
        category = classify_service(name, vendor)
        if cost > 0:
            top_services.append({"name": name, "vendor": vendor, "cost": cost, "category": category})

    # Calculate totals for display
    total_spend = sum(v["cost"] for v in vendor_breakdown)
    service_total = sum(service_types.values())
    chip_total = sum(chip_breakdown.values())

    # Build template context
    start, end = DateHelper.current_month()
    context = {
        "vendor_breakdown": vendor_breakdown,
        "service_types": service_types,
        "service_total": service_total,
        "service_type_total": service_total,
        "chip_breakdown": chip_breakdown,
        "chip_total": chip_total,
        "total_spend": total_spend,
        "top_services": top_services,
        "report_period_start": start,
        "report_period_end": end,
        "generated_at": end,
    }

    # Render template
    print("🎨 Rendering dashboard...")
    env = _get_template_env()
    template = env.get_template("multicloud.html.j2")
    html = template.render(**context)

    # Write output
    output_path = output_dir / "multicloud_dashboard.html"
    output_path.write_text(html, encoding="utf-8")

    print(f"\n✅ Dashboard written to: {output_path}")
    print(f"   Total spend (MTD): ${total_spend:,.2f}")
    print(f"   Vendors: {len(vendor_breakdown)}")
    print(f"   Service type split: IaaS=${service_types['iaas']:,.0f} | PaaS=${service_types['paas']:,.0f} | Containers=${service_types['containers']:,.0f} | AI=${service_types['ai']:,.0f}")
    print(f"   Chip breakdown: Intel=${chip_breakdown['Intel']:,.0f} | AMD=${chip_breakdown['AMD']:,.0f} | Graviton=${chip_breakdown['Graviton (ARM)']:,.0f} | GPU=${chip_breakdown['NVIDIA GPU']:,.0f}")

    return output_path
