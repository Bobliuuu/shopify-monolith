#!/usr/bin/env python3
"""Simple RAG pipeline over insights with citation-style provenance."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import duckdb

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data.duckdb"


@dataclass
class Chunk:
    chunk_id: str
    source: str
    text: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tokenize(text: str) -> set[str]:
    return {w.strip(".,:;!?()[]{}\"'").lower() for w in text.split() if w.strip()}


def _score(query: str, chunk: Chunk) -> float:
    q = _tokenize(query)
    c = _tokenize(chunk.text)
    if not q or not c:
        return 0.0
    inter = len(q.intersection(c))
    return inter / max(1, len(q))


def build_chunks(con: duckdb.DuckDBPyConnection) -> list[Chunk]:
    chunks: list[Chunk] = []
    rows = con.execute(
        """
        SELECT action_id, message, expected_impact
        FROM analytics.daily_action_queue
        ORDER BY created_at DESC
        LIMIT 500
        """
    ).fetchall()
    for action_id, message, expected_impact in rows:
        chunks.append(
            Chunk(
                chunk_id=str(action_id),
                source="analytics.daily_action_queue",
                text=f"{message} Expected impact: {expected_impact}",
            )
        )
    digests = con.execute(
        """
        SELECT digest_id, summary
        FROM analytics.executive_digest
        ORDER BY created_at DESC
        LIMIT 100
        """
    ).fetchall()
    for digest_id, summary in digests:
        chunks.append(
            Chunk(
                chunk_id=str(digest_id),
                source="analytics.executive_digest",
                text=str(summary),
            )
        )
    return chunks


def answer_question(db_path: Path, question: str, top_k: int = 5) -> dict:
    con = duckdb.connect(str(db_path))
    try:
        candidates = build_chunks(con)
    finally:
        con.close()
    ranked = sorted(
        ((c, _score(question, c)) for c in candidates),
        key=lambda pair: pair[1],
        reverse=True,
    )[:top_k]
    citations = [
        {
            "chunk_id": c.chunk_id,
            "source": c.source,
            "score": round(score, 4),
            "evidence": c.text[:500],
        }
        for c, score in ranked
        if score > 0
    ]
    if not citations:
        response = "I do not have enough grounded evidence in the insights store to answer safely."
    else:
        response = "Based on recent insights, prioritize the highest-impact items referenced in citations."
    return {"generated_at": _utc_now(), "question": question, "response": response, "citations": citations}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local RAG query against analytics insights.")
    parser.add_argument("--db-path", default=str(DEFAULT_DB))
    parser.add_argument("--question", required=True)
    parser.add_argument("--output", default="data/rag/latest_answer.json")
    args = parser.parse_args()
    ans = answer_question(Path(args.db_path), args.question)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ans, indent=2), encoding="utf-8")
    print(f"RAG answer written: {out}")


if __name__ == "__main__":
    main()
