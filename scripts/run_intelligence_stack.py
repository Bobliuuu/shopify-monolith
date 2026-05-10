#!/usr/bin/env python3
"""Orchestrate launch checks, sync, insights, SEO loop, and RAG query."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str]) -> None:
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run store intelligence stack end-to-end.")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--db-path", default="data.duckdb")
    parser.add_argument("--rag-question", default="What should we do next to improve revenue?")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    _run([args.python, str(root / "store/live_store_bootstrap.py")])
    _run([args.python, str(root / "greenfield/duckdb_shopify_sync.py"), "--db-path", args.db_path])
    _run([args.python, str(root / "warehouse/insights_engine.py"), "--db-path", args.db_path])
    _run([args.python, str(root / "warehouse/seo_lighthouse_loop.py")])
    _run(
        [
            args.python,
            str(root / "warehouse/rag_assistant.py"),
            "--db-path",
            args.db_path,
            "--question",
            args.rag_question,
        ]
    )
    print("Intelligence stack run complete.")


if __name__ == "__main__":
    main()
