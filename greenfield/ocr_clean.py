"""OCR (simulated or real), text cleaning, and DocAI → Shopify-shaped extraction."""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from enum import Enum
from pathlib import Path
from typing import Any


class EvalMode(str, Enum):
    """How ``ocr_text`` is obtained for a document."""

    GROUND_TRUTH = "ground_truth"
    NOISY = "noisy"
    RAW_ARTIFACT = "raw_artifact"
    IMAGE_OCR = "image_ocr"


def _read_if_exists(path: Path | None) -> str:
    if not path or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def ocr_text(
    dataset_root: Path,
    manifest_row: dict[str, Any],
    mode: EvalMode,
) -> tuple[str, str]:
    """
    Return (text, ocr_engine_label).

    ``IMAGE_OCR`` uses pytesseract on ``image_path`` when Pillow+tesseract are available;
    otherwise falls back to ground truth with engine ``tesseract_fallback_gt``.
    """
    gt_rel = manifest_row.get("ground_truth_ocr_path") or ""
    noisy_rel = manifest_row.get("noisy_ocr_path") or ""
    raw_rel = manifest_row.get("raw_text_path") or ""
    img_rel = manifest_row.get("image_path") or ""

    gt = _read_if_exists(dataset_root / gt_rel) if gt_rel else ""
    noisy = _read_if_exists(dataset_root / noisy_rel) if noisy_rel else ""
    raw = _read_if_exists(dataset_root / raw_rel) if raw_rel else ""

    if mode == EvalMode.GROUND_TRUTH:
        return gt or raw, "ground_truth"
    if mode == EvalMode.NOISY:
        return noisy or gt or raw, "noisy"
    if mode == EvalMode.RAW_ARTIFACT:
        return raw or gt, "raw_artifact"
    if mode == EvalMode.IMAGE_OCR:
        img_path = dataset_root / img_rel if img_rel else Path()
        if img_path.is_file():
            txt, eng = _tesseract_ocr_image(img_path)
            if txt.strip():
                return txt.strip(), eng
        return gt or raw, "tesseract_fallback_gt"

    raise ValueError(f"Unknown mode {mode}")


def _tesseract_ocr_image(image_path: Path) -> tuple[str, str]:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return "", "unavailable"

    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text, "pytesseract"
    except Exception:
        return "", "pytesseract_error"


def source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


_CLEAN_RE = re.compile(r"[ \t]+")
_MULTI_NL = re.compile(r"\n{3,}")


def clean_text(raw: str) -> str:
    """Normalize whitespace; preserve single newlines."""
    t = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = [_CLEAN_RE.sub(" ", ln).strip() for ln in t.split("\n")]
    body = "\n".join(lines)
    return _MULTI_NL.sub("\n\n", body).strip()


_CURRENCY_RE = re.compile(r"[\$,]|,")


def parse_currency_number(s: str) -> float | None:
    if not s:
        return None
    try:
        cleaned = _CURRENCY_RE.sub("", s.strip())
        return float(cleaned)
    except ValueError:
        return None


def load_docai_entities(dataset_root: Path, doc_id: str) -> list[dict[str, Any]] | None:
    path = dataset_root / "labels" / "docai" / f"{doc_id}.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("entities") or [])


def entities_to_extracted_order(
    doc_id: str,
    batch_id: str,
    entities: list[dict[str, Any]],
    manifest_row: dict[str, Any],
) -> dict[str, Any] | None:
    """Build one Shopify-shaped order row from DocAI entities (invoice-style docs)."""
    tx_id = manifest_row.get("tx_id")
    invoice_no = manifest_row.get("invoice_no")

    line_items: list[dict[str, Any]] = []
    grand: float | None = None
    subtotal: float | None = None
    customer_name: str | None = None
    payment_ref: str | None = None
    order_date: str | None = None

    for e in entities:
        et = e.get("type")
        if et == "line_item":
            line_items.append(
                {
                    "sku": e.get("sku"),
                    "title": e.get("description"),
                    "qty": e.get("qty"),
                    "unit": e.get("unit"),
                    "unit_price": e.get("unit_price"),
                    "line_total": e.get("line_total"),
                    "category": e.get("category"),
                }
            )
        elif et == "total":
            if e.get("number") is not None:
                grand = float(e["number"])
            else:
                n = parse_currency_number(str(e.get("text", "")))
                if n is not None:
                    grand = n
        elif et == "customer_name":
            customer_name = e.get("text")
        elif et == "payment_ref":
            payment_ref = e.get("text")
        elif et == "date":
            order_date = e.get("text")

    if not line_items and grand is None:
        return None

    extraction_id = str(uuid.uuid4())
    return {
        "extraction_id": extraction_id,
        "doc_id": doc_id,
        "batch_id": batch_id,
        "order_id": None,
        "order_number": None,
        "customer_id": None,
        "customer_name": customer_name,
        "source_tx_id": tx_id,
        "source_invoice_no": invoice_no,
        "payment_ref": payment_ref,
        "subtotal": subtotal,
        "discount_total": None,
        "shipping_total": None,
        "tax_total": None,
        "grand_total": grand,
        "status": None,
        "order_date": order_date,
        "line_items": json.dumps(line_items),
        "admin_graphql_api_id": None,
        "_confidence": 1.0 if line_items else 0.5,
    }


def entities_to_extracted_products(
    doc_id: str,
    batch_id: str,
    entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Create minimal product rows from line_item entities (catalog-style)."""
    out: list[dict[str, Any]] = []
    for e in entities:
        if e.get("type") != "line_item":
            continue
        sku = e.get("sku")
        if not sku:
            continue
        variant = {
            "id": None,
            "sku": sku,
            "price": str(e.get("unit_price") or ""),
            "title": e.get("description"),
        }
        out.append(
            {
                "extraction_id": str(uuid.uuid4()),
                "doc_id": doc_id,
                "batch_id": batch_id,
                "id": None,
                "title": e.get("description"),
                "vendor": "GreenField Farm & Site Supply",
                "product_type": e.get("category") or "general",
                "handle": None,
                "status": "ACTIVE",
                "variants": json.dumps([variant]),
                "body_html": None,
                "tags": None,
                "created_at": None,
                "updated_at": None,
                "admin_graphql_api_id": None,
                "_confidence": 0.8,
            }
        )
    return out
