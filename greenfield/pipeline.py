"""Batch ingestion: manifest subset → OCR → clean → DuckDB."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Iterable

import duckdb

from greenfield.ocr_clean import (
    EvalMode,
    clean_text,
    entities_to_extracted_order,
    entities_to_extracted_products,
    load_docai_entities,
    ocr_text,
    source_hash,
)
from greenfield.retail_loader import load_retail_jsonl
from greenfield.schema import apply_greenfield_schema, ensure_shopify_reconcile_stub_tables


def _load_split_doc_ids(dataset_root: Path, split: str | None) -> set[str] | None:
    if not split:
        return None
    p = dataset_root / "splits" / f"{split}_doc_ids.txt"
    if not p.is_file():
        return set()
    return {ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()}


def iter_manifest(dataset_root: Path) -> list[dict[str, Any]]:
    """Load manifests/manifest.jsonl (one JSON object per line)."""
    path = dataset_root / "manifests" / "manifest.jsonl"
    if not path.is_file():
        raise FileNotFoundError(f"Missing manifest: {path}")
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _delete_batch_rows(con: duckdb.DuckDBPyConnection, batch_id: str) -> None:
    for table, col in (
        ("extracted_line_items", "batch_id"),
        ("extracted_orders", "batch_id"),
        ("extracted_products", "batch_id"),
        ("extracted_entities", "batch_id"),
        ("ocr_runs", "batch_id"),
    ):
        con.execute(f"DELETE FROM greenfield.{table} WHERE {col} = ?", [batch_id])


def run_ingestion_batch(
    dataset_root: Path | str,
    db_path: Path | str,
    *,
    batch_id: str | None = None,
    eval_mode: str | EvalMode = EvalMode.GROUND_TRUTH,
    split: str | None = None,
    doc_ids: Iterable[str] | None = None,
    load_retail: bool = True,
    replace_retail: bool = True,
    max_docs: int | None = None,
) -> dict[str, Any]:
    """
    Ingest a batch: optional retail JSONL load, then documents from manifest.

    ``split`` filters to ids listed in ``splits/{split}_doc_ids.txt``.
    ``doc_ids`` restricts to an explicit set (intersected with split when both set).
    """
    root = Path(dataset_root).resolve()
    db = Path(db_path).resolve()
    if isinstance(eval_mode, EvalMode):
        mode = eval_mode
    else:
        ev = str(eval_mode).lower().replace("-", "_")
        try:
            mode = EvalMode(ev)
        except ValueError:
            mode = EvalMode.GROUND_TRUTH

    bid = batch_id or f"batch_{uuid.uuid4().hex[:12]}"
    split_ids = _load_split_doc_ids(root, split)
    allow_ids = set(doc_ids) if doc_ids else None

    con = duckdb.connect(str(db))
    try:
        apply_greenfield_schema(con)
        ensure_shopify_reconcile_stub_tables(con)

        retail_counts: dict[str, int] = {}
        if load_retail:
            retail_dir = root / "raw" / "retail"
            if retail_dir.is_dir():
                retail_counts = load_retail_jsonl(
                    con, retail_dir, replace=replace_retail
                )

        started = con.execute("SELECT CURRENT_TIMESTAMP").fetchone()[0]
        con.execute(
            """
            INSERT OR REPLACE INTO greenfield.ingestion_batches
            (batch_id, dataset_root, split_filter, eval_mode, started_at, completed_at, doc_count, status)
            VALUES (?, ?, ?, ?, ?, NULL, NULL, ?)
            """,
            [bid, str(root), split or "", mode.value, started, "running"],
        )

        _delete_batch_rows(con, bid)

        manifest_rows = iter_manifest(root)
        processed = 0
        for row in manifest_rows:
            did = row.get("doc_id")
            if not did:
                continue
            if split_ids is not None and did not in split_ids:
                continue
            if allow_ids is not None and did not in allow_ids:
                continue

            con.execute(
                """
                INSERT OR REPLACE INTO greenfield.documents
                (doc_id, doc_type, tx_id, invoice_no, customer, doc_date, total,
                 dataset_root, raw_text_path, ground_truth_ocr_path, noisy_ocr_path,
                 image_prompt_path, image_path, want_image, split_name, image_sha256, loaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                [
                    did,
                    row.get("doc_type"),
                    row.get("tx_id"),
                    row.get("invoice_no"),
                    row.get("customer"),
                    row.get("date"),
                    row.get("total"),
                    str(root),
                    row.get("raw_text_path"),
                    row.get("ground_truth_ocr_path"),
                    row.get("noisy_ocr_path"),
                    row.get("image_prompt_path"),
                    row.get("image_path"),
                    row.get("want_image"),
                    split,
                    None,
                ],
            )

            raw_txt, engine = ocr_text(root, row, mode)
            cl = clean_text(raw_txt)
            h = source_hash(raw_txt)
            ocr_id = str(uuid.uuid4())
            con.execute(
                """
                INSERT INTO greenfield.ocr_runs
                (ocr_run_id, doc_id, batch_id, ocr_engine, eval_mode, source_hash, raw_text, cleaned_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                [ocr_id, did, bid, engine, mode.value, h, raw_txt, cl],
            )

            entities = load_docai_entities(root, did) or []
            ex_ent_id = str(uuid.uuid4())
            con.execute(
                """
                INSERT INTO greenfield.extracted_entities
                (extraction_id, doc_id, batch_id, entities, _ingested_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                [ex_ent_id, did, bid, json.dumps(entities)],
            )

            order_row = entities_to_extracted_order(did, bid, entities, row)
            if order_row:
                con.execute(
                    """
                    INSERT INTO greenfield.extracted_orders
                    (extraction_id, doc_id, batch_id, order_id, order_number, customer_id, customer_name,
                     source_tx_id, source_invoice_no, payment_ref, subtotal, discount_total, shipping_total,
                     tax_total, grand_total, status, order_date, line_items, admin_graphql_api_id, _confidence, _ingested_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    [
                        order_row["extraction_id"],
                        order_row["doc_id"],
                        order_row["batch_id"],
                        order_row["order_id"],
                        order_row["order_number"],
                        order_row["customer_id"],
                        order_row["customer_name"],
                        order_row["source_tx_id"],
                        order_row["source_invoice_no"],
                        order_row["payment_ref"],
                        order_row["subtotal"],
                        order_row["discount_total"],
                        order_row["shipping_total"],
                        order_row["tax_total"],
                        order_row["grand_total"],
                        order_row["status"],
                        order_row["order_date"],
                        order_row["line_items"],
                        order_row["admin_graphql_api_id"],
                        order_row["_confidence"],
                    ],
                )
                try:
                    li_raw = json.loads(order_row["line_items"])
                    for li in li_raw:
                        lid = str(uuid.uuid4())
                        con.execute(
                            """
                            INSERT INTO greenfield.extracted_line_items
                            (line_item_id, extraction_id, doc_id, batch_id, sku, title, qty, unit, unit_price, line_total, category, _ingested_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                            """,
                            [
                                lid,
                                order_row["extraction_id"],
                                did,
                                bid,
                                li.get("sku"),
                                li.get("title"),
                                li.get("qty"),
                                li.get("unit"),
                                li.get("unit_price"),
                                li.get("line_total"),
                                li.get("category"),
                            ],
                        )
                except (json.JSONDecodeError, TypeError):
                    pass

            for pr in entities_to_extracted_products(did, bid, entities):
                con.execute(
                    """
                    INSERT INTO greenfield.extracted_products
                    (extraction_id, doc_id, batch_id, id, title, vendor, product_type, handle, status,
                     variants, body_html, tags, created_at, updated_at, admin_graphql_api_id, _confidence, _ingested_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    [
                        pr["extraction_id"],
                        pr["doc_id"],
                        pr["batch_id"],
                        pr["id"],
                        pr["title"],
                        pr["vendor"],
                        pr["product_type"],
                        pr["handle"],
                        pr["status"],
                        pr["variants"],
                        pr["body_html"],
                        pr["tags"],
                        pr["created_at"],
                        pr["updated_at"],
                        pr["admin_graphql_api_id"],
                        pr["_confidence"],
                    ],
                )

            processed += 1
            if max_docs is not None and processed >= max_docs:
                break

        done = con.execute("SELECT CURRENT_TIMESTAMP").fetchone()[0]
        con.execute(
            """
            UPDATE greenfield.ingestion_batches
            SET completed_at = ?, doc_count = ?, status = ?
            WHERE batch_id = ?
            """,
            [done, processed, "completed", bid],
        )

        return {
            "batch_id": bid,
            "dataset_root": str(root),
            "db_path": str(db),
            "eval_mode": mode.value,
            "split": split,
            "documents_processed": processed,
            "retail_tables": retail_counts,
        }
    finally:
        con.close()
