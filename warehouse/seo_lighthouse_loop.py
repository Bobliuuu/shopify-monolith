#!/usr/bin/env python3
"""Automated SEO research and Lighthouse loop runner."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class LighthouseResult:
    url: str
    score_performance: float | None
    score_accessibility: float | None
    score_seo: float | None
    score_best_practices: float | None
    report_path: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_lighthouse(url: str, output_dir: Path) -> LighthouseResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = url.replace("https://", "").replace("http://", "").replace("/", "_")
    report = output_dir / f"{stem}.report.json"
    cmd = [
        "lighthouse",
        url,
        "--quiet",
        "--chrome-flags=--headless",
        "--output=json",
        f"--output-path={report}",
    ]
    if shutil.which("lighthouse") is None:
        report.write_text(
            json.dumps(
                {
                    "categories": {
                        "performance": {"score": None},
                        "accessibility": {"score": None},
                        "seo": {"score": None},
                        "best-practices": {"score": None},
                    },
                    "warning": "lighthouse CLI not found; report is a placeholder.",
                }
            ),
            encoding="utf-8",
        )
    else:
        subprocess.run(cmd, check=True)
    payload = json.loads(report.read_text(encoding="utf-8"))
    cats = payload.get("categories", {})
    return LighthouseResult(
        url=url,
        score_performance=(cats.get("performance", {}) or {}).get("score"),
        score_accessibility=(cats.get("accessibility", {}) or {}).get("score"),
        score_seo=(cats.get("seo", {}) or {}).get("score"),
        score_best_practices=(cats.get("best-practices", {}) or {}).get("score"),
        report_path=str(report),
    )


def _prioritize_fixes(results: list[LighthouseResult]) -> list[dict]:
    fixes: list[dict] = []
    for r in results:
        if r.score_performance is not None and r.score_performance < 0.7:
            fixes.append(
                {
                    "url": r.url,
                    "priority": "high",
                    "issue": "performance",
                    "recommendation": "Reduce JS payload and optimize largest contentful paint assets.",
                }
            )
        if r.score_seo is not None and r.score_seo < 0.85:
            fixes.append(
                {
                    "url": r.url,
                    "priority": "high",
                    "issue": "seo",
                    "recommendation": "Improve metadata completeness and structured data coverage.",
                }
            )
    return fixes


def run(urls: list[str], output_dir: Path) -> dict:
    results: list[LighthouseResult] = []
    for url in urls:
        results.append(_run_lighthouse(url, output_dir))
    fixes = _prioritize_fixes(results)
    return {
        "generated_at": _utc_now(),
        "results": [r.__dict__ for r in results],
        "prioritized_fixes": fixes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Lighthouse audits and generate prioritized SEO fixes.")
    parser.add_argument("--urls-file", default="data/seo/urls.txt")
    parser.add_argument("--output", default="data/seo/lighthouse_loop.json")
    parser.add_argument("--reports-dir", default="data/seo/reports")
    args = parser.parse_args()
    urls_path = Path(args.urls_file)
    urls = [ln.strip() for ln in urls_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    report = run(urls, Path(args.reports_dir))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"SEO loop report written: {out}")


if __name__ == "__main__":
    main()
