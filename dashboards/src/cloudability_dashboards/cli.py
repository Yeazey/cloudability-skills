"""CLI entry point for cloudability-dashboards.

Usage:
    cldy-dash executive    Generate executive dashboard
    cldy-dash multicloud   Generate multi-cloud architecture dashboard
    cldy-dash containers   Generate container cost dashboard
    cldy-dash checkin      Generate daily check-in report (markdown to stdout)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _load_env():
    """Load .env file if present (simple key=value parsing, no dependency)."""
    env_file = Path.cwd() / '.env'
    if not env_file.exists():
        env_file = Path(__file__).parent.parent.parent.parent / '.env'
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key not in os.environ:  # Don't override existing env vars
                    os.environ[key] = value


def _get_output_dir() -> Path:
    """Get output directory, creating it if needed."""
    output_dir = Path(os.environ.get('OUTPUT_DIR', Path(__file__).parent.parent.parent.parent / 'output'))
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _open_file(path: Path) -> None:
    """Open a file in the default browser/viewer."""
    if sys.platform == 'darwin':
        subprocess.run(['open', str(path)], check=False)
    elif sys.platform == 'linux':
        subprocess.run(['xdg-open', str(path)], check=False)
    else:
        os.startfile(str(path))  # Windows


def cmd_executive(args):
    from cloudability_dashboards.generators.executive import generate
    output_dir = _get_output_dir()
    path = generate(output_dir=output_dir)
    print(f'\n✅ Dashboard generated: {path}')
    if not args.no_open:
        _open_file(path)


def cmd_multicloud(args):
    from cloudability_dashboards.generators.multicloud import generate
    output_dir = _get_output_dir()
    path = generate(output_dir=output_dir)
    print(f'\n✅ Dashboard generated: {path}')
    if not args.no_open:
        _open_file(path)


def cmd_containers(args):
    from cloudability_dashboards.generators.containers import generate
    output_dir = _get_output_dir()
    path = generate(output_dir=output_dir)
    print(f'\n✅ Dashboard generated: {path}')
    if not args.no_open:
        _open_file(path)


def cmd_checkin(args):
    from cloudability_dashboards.generators.checkin import generate
    fmt = 'json' if args.json else 'markdown'
    output_dir = _get_output_dir() if args.save else None
    report = generate(output_format=fmt, output_dir=output_dir)
    print(report)


def main():
    _load_env()

    parser = argparse.ArgumentParser(
        prog='cldy-dash',
        description='Cloudability Dashboard Generator - Unified Python CLI',
    )
    subparsers = parser.add_subparsers(dest='command', help='Dashboard to generate')

    # Executive
    p_exec = subparsers.add_parser('executive', aliases=['exec'], help='Executive cloud cost dashboard')
    p_exec.add_argument('--no-open', action='store_true', help='Do not auto-open in browser')
    p_exec.set_defaults(func=cmd_executive)

    # Multi-cloud
    p_multi = subparsers.add_parser('multicloud', aliases=['multi', 'arch'], help='Multi-cloud architecture dashboard')
    p_multi.add_argument('--no-open', action='store_true', help='Do not auto-open in browser')
    p_multi.set_defaults(func=cmd_multicloud)

    # Containers
    p_cont = subparsers.add_parser('containers', aliases=['k8s', 'kube'], help='Kubernetes container cost dashboard')
    p_cont.add_argument('--no-open', action='store_true', help='Do not auto-open in browser')
    p_cont.set_defaults(func=cmd_containers)

    # Check-in
    p_check = subparsers.add_parser('checkin', aliases=['standup', 'daily'], help='Daily FinOps check-in report')
    p_check.add_argument('--json', action='store_true', help='Output as JSON instead of markdown')
    p_check.add_argument('--save', action='store_true', help='Also save to output directory')
    p_check.set_defaults(func=cmd_checkin)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Validate credentials after parsing (so --help works without them)
    token = os.environ.get('CLOUDABILITY_OPEN_TOKEN')
    env_id = os.environ.get('CLOUDABILITY_ENVIRONMENT_ID')
    if not token or not env_id:
        print('❌ Missing credentials. Set CLOUDABILITY_OPEN_TOKEN and CLOUDABILITY_ENVIRONMENT_ID.')
        print('   Either export them or create a .env file.')
        sys.exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
