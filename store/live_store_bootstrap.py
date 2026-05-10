#!/usr/bin/env python3
"""Store launch bootstrap and readiness checks."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

CHECKS = (
    "shop_domain_set",
    "shopify_token_set",
    "primary_domain_configured",
    "payments_configured",
    "shipping_profile_configured",
    "tax_profile_configured",
    "product_catalog_seeded",
    "navigation_ready",
    "policy_pages_ready",
    "theme_published",
    "analytics_tags_enabled",
    "checkout_smoke_test_passed",
    "rollback_plan_documented",
)


@dataclass
class LaunchCheck:
    name: str
    passed: bool
    detail: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_readiness_checks() -> list[LaunchCheck]:
    """Evaluate baseline store readiness from environment and local artifacts."""
    checks: list[LaunchCheck] = []
    checks.append(
        LaunchCheck(
            name="shop_domain_set",
            passed=bool(os.getenv("SHOPIFY_SHOP_NAME")),
            detail="Requires SHOPIFY_SHOP_NAME env variable.",
        )
    )
    checks.append(
        LaunchCheck(
            name="shopify_token_set",
            passed=bool(os.getenv("SHOPIFY_API_PASSWORD") or os.getenv("SHOPIFY_ACCESS_TOKEN")),
            detail="Requires SHOPIFY_API_PASSWORD or SHOPIFY_ACCESS_TOKEN.",
        )
    )
    for static in CHECKS[2:]:
        checks.append(
            LaunchCheck(
                name=static,
                passed=False,
                detail="Manual confirmation required before go-live.",
            )
        )
    return checks


def write_launch_report(output_path: Path) -> dict[str, object]:
    checks = run_readiness_checks()
    payload = {
        "generated_at": _utc_now(),
        "all_checks_passed": all(c.passed for c in checks),
        "checks": [asdict(c) for c in checks],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Shopify launch readiness report.")
    parser.add_argument(
        "--output",
        default="data/launch/store_launch_readiness.json",
        help="Path to write the launch report JSON.",
    )
    args = parser.parse_args()
    report = write_launch_report(Path(args.output))
    print(f"Launch report written: {args.output}")
    print(f"All checks passed: {report['all_checks_passed']}")


if __name__ == "__main__":
    main()
