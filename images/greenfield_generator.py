#!/usr/bin/env python3
"""
GreenField ML-grade synthetic document generator
================================================

Goal:
- Generate ~500-1000 linked business documents for a fictional Ontario farm supply company.
- Keep spend under a budget cap, default $40.
- Create high-density documents with lots of transaction data.
- Generate raw text, CSV manifests, labels, image prompts, OCR-noise variants.
- Optionally call OpenAI image generation for a selected subset of high-value docs.

Install:
  pip install openai pillow python-dotenv

Usage, no API spend:
  python greenfield_generator.py --bundles 120 --dry-run

Usage, generate prompts + selected images:
  export OPENAI_API_KEY=...
  python greenfield_generator.py --bundles 120 --generate-images --budget-usd 40 --estimated-cost-per-image 0.08

Cheaper mode:
  python greenfield_generator.py --bundles 100 --generate-images --budget-usd 25 --image-policy efficient

High-quality mode:
  python greenfield_generator.py --bundles 80 --generate-images --budget-usd 40 --image-policy quality

Notes:
- This script assumes synthetic, fictional data.
- Image cost varies by model, size, quality, and API pricing changes.
- The budget guard uses `estimated_cost_per_image`; set this conservatively.
- The newest available image model can be passed with --image-model.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import os
import random
import re
import shutil
import textwrap
import time
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# ----------------------------
# Company constants
# ----------------------------

COMPANY = {
    "legal_name": "GreenField Supply Co. Ltd.",
    "operating_name": "GreenField Farm & Site Supply",
    "address": "17 Sideroad 8, Guelph, ON N1H 6J2",
    "phone": "(519) 822-4419",
    "email": "orders@greenfieldsupply.example",
    "hst": "84203 1234 RT0001",
    "palette": {
        "forest_green": "#1F4D2B",
        "cream": "#F4F0DD",
        "muted_beige": "#C9B88D",
        "soil_brown": "#4A3520",
    },
}

CUSTOMERS = [
    {"id": "CUST-001", "name": "Maple Ridge Farms Ltd.", "type": "cash crop farm", "city": "Fergus", "terms": "Net 30", "contact": "Jeff Martin"},
    {"id": "CUST-002", "name": "GreenScape Landscaping Inc.", "type": "landscaper", "city": "Mississauga", "terms": "Net 30", "contact": "Kyle Park"},
    {"id": "CUST-003", "name": "Oak Valley Dairy", "type": "dairy farm", "city": "Elora", "terms": "Net 60", "contact": "Sarah L."},
    {"id": "CUST-004", "name": "NorthLine Contracting", "type": "contractor", "city": "Kitchener", "terms": "Net 30", "contact": "Mike Rowan"},
    {"id": "CUST-005", "name": "Riverbend Organics", "type": "organic farm", "city": "St Jacobs", "terms": "Net 15", "contact": "Anita B."},
    {"id": "CUST-006", "name": "HighPoint Property Services", "type": "property services", "city": "Cambridge", "terms": "Due on receipt", "contact": "Jason Reid"},
    {"id": "CUST-007", "name": "Silver Creek Stables", "type": "horse farm", "city": "Milton", "terms": "Net 30", "contact": "Megan S."},
    {"id": "CUST-008", "name": "UrbanRoot Gardens Co.", "type": "urban farm", "city": "Toronto", "terms": "Card", "contact": "Priya N."},
    {"id": "CUST-009", "name": "ClearPath Utilities", "type": "utility contractor", "city": "Hamilton", "terms": "Net 30", "contact": "Brian Berry"},
    {"id": "CUST-010", "name": "Brampton Turf Solutions", "type": "turf installer", "city": "Brampton", "terms": "Net 30", "contact": "Owen Patel"},
]

PRODUCTS = [
    {"sku": "GF-FERT-UREA-BULK", "name": "Urea 46-0-0 Bulk (per ton)", "messy": ["Urea bulk 46", "Urea 46-0-0 per ton", "bulk urea"], "unit": "ton", "price": 710.00, "category": "fertilizer"},
    {"sku": "GF-FERT-UREA-55", "name": "Urea 46 granular - 55lb bags", "messy": ["urea granular 55lb", "46 urea bags", "Urea 55#"], "unit": "bag", "price": 34.50, "category": "fertilizer"},
    {"sku": "GF-FERT-START-122412", "name": "Starter Fert 12-24-12 (skid pricing avail)", "messy": ["12-24-12 starter", "starter fert skid", "Starter 12/24/12"], "unit": "bag", "price": 42.00, "category": "fertilizer"},
    {"sku": "GF-LIME-AG-LOAD", "name": "Lime - ag grade (dump trailer load)", "messy": ["ag lime load", "lime dump trailer", "ag grade lime"], "unit": "load", "price": 540.00, "category": "soil"},
    {"sku": "GF-SOIL-TOP-PREM", "name": "Topsoil screened (premium) per yard", "messy": ["screened topsoil", "top soil premium", "premium dirt"], "unit": "yd", "price": 46.00, "category": "bulk"},
    {"sku": "GF-SOIL-TOP-BASIC", "name": "Top Soil (basic fill) — cheap stuff", "messy": ["basic fill", "cheap top soil", "fill dirt"], "unit": "yd", "price": 28.00, "category": "bulk"},
    {"sku": "GF-SEED-GRASS-CON25", "name": "Grass Seed Mix - Contractor Blend 25kg", "messy": ["contractor grass seed", "seed mix 25kg", "Contractor Blend"], "unit": "bag", "price": 89.00, "category": "seed"},
    {"sku": "GF-SEED-TURF-10", "name": "Grass seed premium turf mix 10lb", "messy": ["premium turf 10lb", "turf mix", "grass seed prem"], "unit": "bag", "price": 31.50, "category": "seed"},
    {"sku": "GF-FEED-CHKN-LAYER20", "name": "Chicken Feed Layer Pellets 20kg", "messy": ["layer pellets", "chicken feed 20kg", "hens feed"], "unit": "bag", "price": 22.25, "category": "feed"},
    {"sku": "GF-FEED-DAIRY4-BULK", "name": "Dairy ration mix #4 (bulk auger fill)", "messy": ["dairy #4", "ration mix 4", "bulk dairy feed"], "unit": "ton", "price": 492.00, "category": "feed"},
    {"sku": "GF-BED-STRAW-DUSTY", "name": "Straw bales (small square, dusty)", "messy": ["small straw", "dusty straw bales", "cheap straw"], "unit": "bale", "price": 6.50, "category": "bedding"},
    {"sku": "GF-BED-STRAW-HORSE", "name": "Straw Bale (clean, horse grade)", "messy": ["horse straw", "clean straw", "straw horse grade"], "unit": "bale", "price": 8.25, "category": "bedding"},
    {"sku": "GF-BED-SHAV-COMP", "name": "Wood shavings compressed bale", "messy": ["compressed shavings", "wood shaving bale", "horse shavings"], "unit": "bale", "price": 10.75, "category": "bedding"},
    {"sku": "GF-CHEM-GLY-4L", "name": "Roundup alt glyphosate 4L jug", "messy": ["glyphosate 4L", "roundup alt", "weed spray 4L"], "unit": "jug", "price": 68.00, "category": "chemical"},
    {"sku": "GF-IRR-DRIP-100", "name": "Drip line 1/2 poly 100ft roll", "messy": ["drip line 100ft", "half inch poly", "irrigation drip roll"], "unit": "roll", "price": 47.50, "category": "irrigation"},
    {"sku": "GF-FENCE-WIRE-200", "name": "Fence wire galvanized 200m spool", "messy": ["galv fence wire", "wire 200m", "fencing spool"], "unit": "spool", "price": 129.00, "category": "fencing"},
    {"sku": "GF-FENCE-TPOST-6", "name": "T-posts 6ft green bundle of 10", "messy": ["6ft green t posts", "T post bundle", "posts 10 pack"], "unit": "bundle", "price": 79.00, "category": "fencing"},
    {"sku": "GF-BULK-GRAVEL-34", "name": "Gravel 3/4 clear stone per ton", "messy": ["3/4 clear", "clear stone", "gravel 3/4"], "unit": "ton", "price": 42.00, "category": "bulk"},
    {"sku": "GF-BULK-CRUSHER", "name": "Crusher run gravel driveway mix", "messy": ["crusher run", "driveway mix", "crush run"], "unit": "ton", "price": 36.00, "category": "bulk"},
    {"sku": "GF-BULK-SAND-MASON", "name": "Sand - masonry (washed) yard", "messy": ["mason sand", "washed sand", "sand yard"], "unit": "yd", "price": 38.00, "category": "bulk"},
    {"sku": "GF-SEASON-SALT-20", "name": "Ice melt salt (road salt) 20kg", "messy": ["road salt 20kg", "ice melt", "salt bags"], "unit": "bag", "price": 12.00, "category": "seasonal"},
    {"sku": "GF-SITE-GLOVES-50", "name": "Work gloves (bulk pack 50)", "messy": ["gloves bulk", "work glove box", "gloves 50 pack"], "unit": "case", "price": 55.00, "category": "site"},
    {"sku": "GF-SITE-TARP-1012", "name": "Blue tarp 10x12 (heavy duty-ish)", "messy": ["blue tarp", "10x12 tarp", "hd-ish tarp"], "unit": "ea", "price": 16.75, "category": "site"},
]

VENDORS = [
    "Fertilizer Depot Inc.",
    "Ontario Seed & Turf Wholesale",
    "Wellington Aggregates Yard Ticket",
    "County Hardware & Farm Supply",
    "Tri-County Feed Mill",
]

PAYMENT_METHODS = ["EFT", "e-transfer", "cheque", "Interac", "Visa", "on account"]
DOC_TYPES = ["invoice", "receipt", "email", "note", "delivery_ticket", "bank_proof", "inventory_sheet"]


# ----------------------------
# Data models
# ----------------------------

@dataclass
class LineItem:
    sku: str
    name: str
    messy_name: str
    qty: float
    unit: str
    unit_price: float
    line_total: float

@dataclass
class Transaction:
    tx_id: str
    invoice_no: str
    customer: dict[str, Any]
    date: str
    due_date: str
    items: list[LineItem]
    subtotal: float
    hst: float
    total: float
    payment_method: str
    paid_date: str
    payment_ref: str
    doc_quality: str
    ambiguity: str


# ----------------------------
# Utility functions
# ----------------------------

def money(x: float) -> str:
    return f"{x:,.2f}"

def safe_id(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def random_date(start: date, end: date) -> date:
    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))

def choose_products_for_customer(customer: dict[str, Any]) -> list[dict[str, Any]]:
    t = customer["type"]
    if "crop" in t:
        pool = [p for p in PRODUCTS if p["category"] in ["fertilizer", "soil", "seed", "chemical"]]
    elif "landscaper" in t or "turf" in t or "property" in t:
        pool = [p for p in PRODUCTS if p["category"] in ["bulk", "seed", "site", "seasonal"]]
    elif "dairy" in t or "horse" in t:
        pool = [p for p in PRODUCTS if p["category"] in ["feed", "bedding", "fencing"]]
    elif "contractor" in t or "utility" in t:
        pool = [p for p in PRODUCTS if p["category"] in ["bulk", "fencing", "site", "irrigation"]]
    else:
        pool = PRODUCTS
    return random.sample(pool, k=random.randint(2, min(5, len(pool))))

def qty_for_unit(unit: str) -> float:
    if unit in ["ton", "yd"]:
        return round(random.choice([1, 1.5, 2, 2.5, 3, 4, 4.5, 5, 8, 10, 12]), 1)
    if unit in ["load"]:
        return random.choice([1, 2, 3])
    if unit in ["bale", "bag"]:
        return random.choice([4, 6, 10, 12, 20, 25, 30, 40, 50])
    if unit in ["bundle", "case", "spool", "roll", "jug"]:
        return random.choice([1, 2, 3, 4, 6, 8])
    return random.choice([1, 2, 3])

def generate_transaction(i: int, start: date, end: date) -> Transaction:
    customer = random.choice(CUSTOMERS)
    d = random_date(start, end)
    terms_days = 60 if "60" in customer["terms"] else 30 if "30" in customer["terms"] else 7
    due = d + timedelta(days=terms_days)
    paid = d + timedelta(days=random.randint(2, min(terms_days + 5, 65)))

    items = []
    for p in choose_products_for_customer(customer):
        qty = qty_for_unit(p["unit"])
        # customer-specific variance
        unit_price = round(p["price"] * random.uniform(0.94, 1.08), 2)
        line_total = round(qty * unit_price, 2)
        items.append(LineItem(
            sku=p["sku"],
            name=p["name"],
            messy_name=random.choice(p["messy"]),
            qty=qty,
            unit=p["unit"],
            unit_price=unit_price,
            line_total=line_total,
        ))

    # Add delivery/service line to ~75%
    if random.random() < 0.75:
        delivery_price = random.choice([65, 85, 95, 120, 150, 185])
        items.append(LineItem("SERV-DELIVERY", "Delivery / truck run", "delivery - truck", 1, "ea", delivery_price, delivery_price))

    subtotal = round(sum(x.line_total for x in items), 2)
    hst = round(subtotal * 0.13, 2)
    total = round(subtotal + hst, 2)
    invoice_no = f"GF-{10480+i:05d}"
    payment_method = random.choice(PAYMENT_METHODS)
    payment_ref = (
        f"{customer['name'].split()[0].upper()}-{invoice_no[-3:]}"
        if payment_method in ["EFT", "e-transfer"]
        else f"CHK-{random.randint(1000,9999)}"
        if payment_method == "cheque"
        else f"AUTH-{random.randint(100000,999999)}"
    )
    return Transaction(
        tx_id=f"TX-{i:04d}",
        invoice_no=invoice_no,
        customer=customer,
        date=d.isoformat(),
        due_date=due.isoformat(),
        items=items,
        subtotal=subtotal,
        hst=hst,
        total=total,
        payment_method=payment_method,
        paid_date=paid.isoformat(),
        payment_ref=payment_ref,
        doc_quality=random.choice(["clean", "normal", "messy", "bad_phone_photo", "cropped_shadow"]),
        ambiguity=random.choice(["none", "same_as_last_time", "price_changed", "partial_delivery", "handwritten_correction"]),
    )


# ----------------------------
# Text artifact generators
# ----------------------------

def invoice_text(tx: Transaction) -> str:
    rows = []
    for li in tx.items:
        rows.append(f"{li.sku:<20} {li.messy_name:<42} {li.qty:<7} {li.unit:<6} {money(li.unit_price):>9} {money(li.line_total):>10}")
    note = ""
    if tx.ambiguity == "handwritten_correction":
        note = "\nPEN NOTE: check price on one line / total circled by hand"
    elif tx.ambiguity == "partial_delivery":
        note = "\nPEN NOTE: one item backordered, send rest Friday"
    else:
        note = f"\nPEN NOTE: Thanks {tx.customer['contact'].split()[0]}! Call if you need anything else"
    return f"""GreenField Farm & Site Supply
{COMPANY['address']}
Tel {COMPANY['phone']}  HST # {COMPANY['hst']}

INVOICE: {tx.invoice_no}
Date: {tx.date}
Due: {tx.due_date}
Terms: {tx.customer['terms']}

BILL TO:
{tx.customer['name']}
{tx.customer['city']}, Ontario
Attn: {tx.customer['contact']}

SKU                  Description                                Qty     Unit   Unit Price     Amount
-----------------------------------------------------------------------------------------------
{chr(10).join(rows)}

Subtotal: {money(tx.subtotal)}
HST (ON) 13%: {money(tx.hst)}
TOTAL: ${money(tx.total)}
Payment: {tx.payment_method} / ref {tx.payment_ref} expected {tx.paid_date}
{note}
"""

def receipt_text(tx: Transaction) -> str:
    vendor = random.choice(VENDORS)
    # Vendor receipt usually covers a subset/restock related to transaction categories
    main = tx.items[0]
    qty = max(1, round(main.qty * random.uniform(1.2, 3.0), 1))
    price = round(main.unit_price * random.uniform(0.70, 0.92), 2)
    subtotal = round(qty * price + random.choice([0, 15, 25, 36, 45]), 2)
    hst = round(subtotal * 0.13, 2)
    total = round(subtotal + hst, 2)
    return f"""{vendor}
RECEIPT #{random.randint(20000,99999)}    {tx.date}
Sold to: GreenField Farm & Site Supply

Item                              Qty        Price       Amount
---------------------------------------------------------------
{main.messy_name:<34} {qty:<10} {money(price):>8} {money(qty*price):>10}
Handling / enviro / freight       1          {money(subtotal - qty*price):>8} {money(subtotal - qty*price):>10}

Subtotal                          {money(subtotal)}
HST (ON) 13%                      {money(hst)}
TOTAL PAID                        ${money(total)}
Paid: {random.choice(["Visa ending 4102", "Interac", "EFT batch", "Cheque"])}
"""

def email_text(tx: Transaction) -> str:
    c = tx.customer
    first = c["contact"].split()[0]
    vague = {
        "same_as_last_time": "same as last time if price is close",
        "price_changed": "did the price change or can you hold old price?",
        "partial_delivery": "send what you have and backorder the rest",
        "handwritten_correction": "also check the total because last one looked off",
        "none": "put it on our account please",
    }[tx.ambiguity]
    item_phrase = ", ".join([li.messy_name for li in tx.items[:2]])
    return f"""From: {safe_id(c['name'])}@example.com
To: orders@greenfieldsupply.example
Subject: order / {c['name']}

hey,

can you get us {item_phrase} for {tx.date}?
{vague}

thanks,
{first}
{c['name']}
"""

def note_text(tx: Transaction) -> str:
    c = tx.customer
    li = random.choice(tx.items)
    return f"""HANDWRITTEN NOTE TRANSCRIPTION:
Call {c['name'].split()[0]} re: {li.messy_name}
{random.choice(["running low again", "needs delivery before rain", "price check requested", "driver says gate locked", "ask if cheque ready"])}
Ref {tx.invoice_no} / {tx.payment_ref}
"""

def delivery_ticket_text(tx: Transaction) -> str:
    c = tx.customer
    delivered = tx.items[: random.randint(1, min(3, len(tx.items)))]
    rows = "\n".join([f"{li.qty:<8} {li.unit:<6} {li.messy_name}" for li in delivered])
    return f"""GREENFIELD FARM & SITE SUPPLY       DELIVERY TICKET #{random.randint(80000,89999)}
Date: {tx.date}
Customer: {c['name']}
Location: {c['city']}, ON
Driver: {random.choice(["Mike", "TS", "Wayne", "Rob"])}

QTY      UNIT   DESCRIPTION
-----------------------------------------
{rows}

Notes: {random.choice(["Deliver by Thurs morning", "Call before dumping", "Leave by north gate", "Customer signed on arrival", "Road muddy, use side lane"])}
Received by: ____________________
"""

def bank_proof_text(tx: Transaction) -> str:
    return f"""Mobile banking transaction detail

Date posted: {tx.paid_date}
Description: {tx.payment_method} {tx.customer['name']} {tx.payment_ref}
Amount: +${money(tx.total)}
Account: Business Chequing **** 1182
Memo: matches invoice {tx.invoice_no}
"""

def inventory_sheet_text(transactions: list[Transaction]) -> str:
    # High density inventory snapshot
    usage: dict[str, float] = {}
    names: dict[str, str] = {}
    units: dict[str, str] = {}
    for tx in transactions:
        for li in tx.items:
            if li.sku.startswith("GF-"):
                usage[li.sku] = usage.get(li.sku, 0) + li.qty
                names[li.sku] = li.name
                units[li.sku] = li.unit

    rows = ["sku,name,starting_qty,ordered_out,restocked,ending_qty,unit"]
    for sku, out in sorted(usage.items()):
        starting = random.randint(30, 180)
        restocked = random.choice([0, 0, 10, 20, 30, 50])
        ending = round(starting - out + restocked, 1)
        rows.append(f"{sku},{names[sku]},{starting},{round(out,1)},{restocked},{ending},{units[sku]}")
    return "\n".join(rows) + "\n"


# ----------------------------
# Image prompt generation
# ----------------------------

GLOBAL_STYLE = """GreenField Farm & Site Supply, fictional Ontario farm supply company.

Style:
- rural Ontario farm supply business, practical and slightly outdated
- forest green, off-white, muted beige, dark soil brown palette
- documents should contain lots of readable transactional data
- realistic imperfections: skew, shadows, wrinkles, stains, folds, uneven alignment
- phone-photo realism, not clean SaaS mockup
- preserve key names, dates, totals, SKUs, and quantities
"""

def image_prompt(doc_type: str, raw_text: str, tx: Transaction | None = None, policy: str = "efficient") -> str:
    quality = tx.doc_quality if tx else random.choice(["normal", "messy", "bad_phone_photo"])
    quality_clause = {
        "clean": "mostly readable, lightly handled paper, mild desk shadow",
        "normal": "realistic office document, slight skew, small smudges",
        "messy": "wrinkled paper, pen marks, dirt smudges, imperfect table alignment",
        "bad_phone_photo": "low-quality phone photo, tilted perspective, mild blur, partial shadow",
        "cropped_shadow": "slightly cropped edge, strong side shadow, not perfectly flat",
    }[quality]

    if doc_type == "invoice":
        task = "Create a realistic photographed invoice on paper from GreenField Farm & Site Supply. Include itemized table, invoice number, customer, totals, HST, payment note, and handwritten circle around total."
    elif doc_type == "receipt":
        task = "Create a crumpled thermal/vendor receipt photographed on a wooden or warehouse counter. Faded ink, wrinkled paper, torn edge, lots of line-item and payment data."
    elif doc_type == "email":
        task = "Create a realistic Gmail or Outlook email screenshot. Include sender, recipient, subject, timestamp, body, reply buttons, and subtle screenshot compression."
    elif doc_type == "note":
        task = "Create a realistic handwritten note in blue pen on scrap paper or yellow sticky note. It must look handwritten, not typed. Messy spacing and pen pressure variation."
    elif doc_type == "delivery_ticket":
        task = "Create a carbon-copy style delivery ticket on clipboard or truck dashboard. Use handwritten entries, signature line, delivery notes, and customer details."
    elif doc_type == "bank_proof":
        task = "Create a realistic mobile banking transaction detail screenshot with amount, date, reference, account, and description. Slight glare/crop like phone screenshot."
    elif doc_type == "inventory_sheet":
        task = "Create a printed inventory spreadsheet on a clipboard, with many rows, SKUs, quantities, handwritten corrections, crossed-out values, and pen marks."
    else:
        task = "Create a realistic business document image."

    if policy == "quality":
        density = "Make the document high-resolution and packed with readable data while retaining realism."
    else:
        density = "Keep it readable and data-dense; do not waste space on decorative elements."

    return f"""{GLOBAL_STYLE}

Task:
{task}

Image quality condition:
{quality_clause}

Data density:
{density}

Raw source content to visually represent:
---BEGIN RAW CONTENT---
{raw_text[:4200]}
---END RAW CONTENT---
"""


# ----------------------------
# Labels + OCR noise
# ----------------------------

def ocr_noise(text: str) -> str:
    replacements = [
        ("0", "O"), ("1", "l"), ("5", "S"), ("rn", "m"),
        ("Invoice", "lnvoice"), ("TOTAL", "T0TAL"), ("GreenField", "GreenFieId"),
        ("@", " at "), ("$", "S"), (",", random.choice([",", "", "."])),
    ]
    out = text
    for a, b in replacements:
        if random.random() < 0.35:
            out = out.replace(a, b)
    lines = []
    for line in out.splitlines():
        if random.random() < 0.05:
            continue
        if random.random() < 0.07:
            line = " " + line
        if random.random() < 0.05:
            line += "  "
        lines.append(line)
    return "\n".join(lines)

def label_for_doc(doc_id: str, doc_type: str, tx: Transaction | None, raw_path: str, image_path: str | None) -> dict[str, Any]:
    entities = []
    if tx:
        entities.extend([
            {"type": "invoice_number", "text": tx.invoice_no},
            {"type": "customer_name", "text": tx.customer["name"]},
            {"type": "date", "text": tx.date},
            {"type": "total", "text": money(tx.total)},
            {"type": "payment_ref", "text": tx.payment_ref},
        ])
        for li in tx.items:
            entities.append({"type": "sku", "text": li.sku})
            entities.append({"type": "line_item", "text": li.name, "qty": li.qty, "unit_price": li.unit_price, "line_total": li.line_total})
    return {
        "doc_id": doc_id,
        "doc_type": doc_type,
        "raw_text_path": raw_path,
        "image_path": image_path,
        "entities": entities,
        "bbox_status": "not_available_until_real_ocr",
    }


# ----------------------------
# Image generation
# ----------------------------

def should_generate_image(doc_type: str, image_policy: str) -> bool:
    # This controls cost. For 120 bundles:
    # efficient ≈ 250-350 images depending random
    # quality ≈ 400-600 images
    r = random.random()
    if image_policy == "minimal":
        probs = {
            "invoice": 0.55,
            "receipt": 0.45,
            "note": 0.75,
            "delivery_ticket": 0.35,
            "email": 0.10,
            "bank_proof": 0.10,
            "inventory_sheet": 0.50,
        }
    elif image_policy == "quality":
        probs = {
            "invoice": 0.90,
            "receipt": 0.85,
            "note": 1.00,
            "delivery_ticket": 0.70,
            "email": 0.35,
            "bank_proof": 0.25,
            "inventory_sheet": 0.70,
        }
    else:  # efficient default
        probs = {
            "invoice": 0.75,
            "receipt": 0.70,
            "note": 0.90,
            "delivery_ticket": 0.50,
            "email": 0.25,
            "bank_proof": 0.18,
            "inventory_sheet": 0.60,
        }
    return r < probs.get(doc_type, 0.2)

def generate_image_openai(client: Any, model: str, prompt: str, out_path: Path, size: str, quality: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
    )
    b64 = result.data[0].b64_json
    out_path.write_bytes(base64.b64decode(b64))


# ----------------------------
# Main dataset builder
# ----------------------------

def build_dataset(args: argparse.Namespace) -> None:
    random.seed(args.seed)
    out = Path(args.out)
    if out.exists() and args.overwrite:
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    # Folder structure
    dirs = [
        "raw/company",
        "raw/transactions",
        "raw/artifacts",
        "prompts/images",
        "images",
        "ocr/ground_truth",
        "ocr/noisy",
        "labels/docai",
        "labels/field_targets",
        "labels/layoutlm_placeholders",
        "manifests",
        "splits",
        "docs",
    ]
    for d in dirs:
        (out / d).mkdir(parents=True, exist_ok=True)

    # Company master files
    write(out / "raw/company/profile.txt", textwrap.dedent(f"""\
    {COMPANY['legal_name']}
    Operating as: {COMPANY['operating_name']}
    Address: {COMPANY['address']}
    Phone: {COMPANY['phone']}
    Email: {COMPANY['email']}
    HST: {COMPANY['hst']}

    Fictional Ontario farm supply store serving farms, landscapers, and contractors.
    Core use case: Ambrook-style transaction/document ingestion, reconciliation, OCR, and cross-document linking.
    """))

    with (out / "raw/company/customers.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CUSTOMERS[0].keys())
        writer.writeheader()
        writer.writerows(CUSTOMERS)

    with (out / "raw/company/products.csv").open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["sku", "name", "unit", "price", "category", "messy_aliases"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in PRODUCTS:
            writer.writerow({k: p[k] for k in ["sku", "name", "unit", "price", "category"]} | {"messy_aliases": " | ".join(p["messy"])})

    # Transactions
    txs = [generate_transaction(i + 1, date(2026, 4, 1), date(2026, 6, 30)) for i in range(args.bundles)]
    dump_json(out / "raw/transactions/transactions.json", [
        asdict(tx) | {"items": [asdict(li) for li in tx.items]} for tx in txs
    ])

    docs: list[dict[str, Any]] = []

    def add_doc(doc_type: str, tx: Transaction | None, raw_text: str, base_id: str) -> None:
        doc_id = safe_id(base_id)
        raw_rel = f"raw/artifacts/{doc_id}.txt"
        raw_path = out / raw_rel
        write(raw_path, raw_text)

        gt_rel = f"ocr/ground_truth/{doc_id}.txt"
        noisy_rel = f"ocr/noisy/{doc_id}.txt"
        write(out / gt_rel, raw_text)
        write(out / noisy_rel, ocr_noise(raw_text))

        prompt = image_prompt(doc_type, raw_text, tx, args.image_policy)
        prompt_rel = f"prompts/images/{doc_id}.prompt.txt"
        write(out / prompt_rel, prompt)

        image_rel = f"images/{doc_id}.png"
        want_image = should_generate_image(doc_type, args.image_policy)
        docs.append({
            "doc_id": doc_id,
            "doc_type": doc_type,
            "tx_id": tx.tx_id if tx else "",
            "invoice_no": tx.invoice_no if tx else "",
            "customer": tx.customer["name"] if tx else "",
            "raw_text_path": raw_rel,
            "ground_truth_ocr_path": gt_rel,
            "noisy_ocr_path": noisy_rel,
            "image_prompt_path": prompt_rel,
            "image_path": image_rel if want_image else "",
            "want_image": want_image,
        })

        dump_json(out / f"labels/docai/{doc_id}.json", label_for_doc(doc_id, doc_type, tx, raw_rel, image_rel if want_image else None))
        dump_json(out / f"labels/field_targets/{doc_id}.fields.json", {
            "doc_id": doc_id,
            "doc_type": doc_type,
            "tx_id": tx.tx_id if tx else None,
            "fields": label_for_doc(doc_id, doc_type, tx, raw_rel, image_rel if want_image else None)["entities"],
        })
        tokens = re.findall(r"\S+", raw_text)[:512]
        dump_json(out / f"labels/layoutlm_placeholders/{doc_id}.json", {
            "doc_id": doc_id,
            "tokens": tokens,
            "bboxes": [[0, 0, 0, 0] for _ in tokens],
            "ner_tags": ["O" for _ in tokens],
            "note": "Populate bboxes after OCR on generated image.",
        })

    for tx in txs:
        add_doc("invoice", tx, invoice_text(tx), f"{tx.tx_id}_{tx.invoice_no}_invoice")
        add_doc("receipt", tx, receipt_text(tx), f"{tx.tx_id}_{tx.invoice_no}_vendor_receipt")
        add_doc("email", tx, email_text(tx), f"{tx.tx_id}_{tx.invoice_no}_customer_email")
        add_doc("note", tx, note_text(tx), f"{tx.tx_id}_{tx.invoice_no}_handwritten_note")
        if random.random() < 0.65:
            add_doc("delivery_ticket", tx, delivery_ticket_text(tx), f"{tx.tx_id}_{tx.invoice_no}_delivery_ticket")
        if random.random() < 0.45:
            add_doc("bank_proof", tx, bank_proof_text(tx), f"{tx.tx_id}_{tx.invoice_no}_bank_proof")

    # Add periodic inventory sheets, dense catalog dumps, website page
    for batch_idx in range(0, len(txs), 25):
        batch = txs[batch_idx: batch_idx + 25]
        add_doc("inventory_sheet", None, inventory_sheet_text(batch), f"inventory_sheet_batch_{batch_idx//25+1:02d}")

    catalog = "\n".join([f"{p['sku']} :: {random.choice(p['messy'])} / {p['name']} / ${p['price']} per {p['unit']}" for p in PRODUCTS])
    add_doc("catalog", None, f"GREENFIELD PRODUCT CATALOG / SPRING 2026\n\n{catalog}\n\nprices change without notice, call for bulk quotes\n", "product_catalog_spring_2026")

    website = f"""<html><head><title>{COMPANY['operating_name']}</title></head>
<body bgcolor="#f4f0dd" text="#1f4d2b">
<h1>{COMPANY['operating_name']}</h1>
<p>Farm inputs, feed, bedding, gravel, seed, fencing. Guelph / Fergus / Elora / Kitchener area.</p>
<ul>
{''.join([f'<li>{p["name"]} - ${p["price"]}/{p["unit"]}</li>' for p in PRODUCTS[:16]])}
</ul>
<p>Call {COMPANY['phone']} for delivery.</p>
</body></html>
"""
    add_doc("website", None, website, "old_website_homepage")

    # Manifest
    manifest_path = out / "manifests/manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(docs[0].keys()))
        writer.writeheader()
        writer.writerows(docs)

    with (out / "manifests/manifest.jsonl").open("w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    # Transaction graph
    graph = {}
    for tx in txs:
        graph[tx.tx_id] = {
            "invoice_no": tx.invoice_no,
            "customer": tx.customer["name"],
            "total": tx.total,
            "payment_ref": tx.payment_ref,
            "docs": [d["doc_id"] for d in docs if d["tx_id"] == tx.tx_id],
        }
    dump_json(out / "manifests/transaction_graph.json", graph)

    # Splits by transaction, not doc, to avoid leakage
    tx_ids = [tx.tx_id for tx in txs]
    random.shuffle(tx_ids)
    n = len(tx_ids)
    split_map = {
        "train": set(tx_ids[: int(n * 0.7)]),
        "val": set(tx_ids[int(n * 0.7): int(n * 0.85)]),
        "test": set(tx_ids[int(n * 0.85):]),
    }
    for split, ids in split_map.items():
        write(out / f"splits/{split}_tx_ids.txt", "\n".join(sorted(ids)))
        write(out / f"splits/{split}_doc_ids.txt", "\n".join(sorted(d["doc_id"] for d in docs if d["tx_id"] in ids or d["tx_id"] == "")))

    # README
    readme = f"""# GreenField Synthetic ML Dataset

Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}
Bundles: {args.bundles}
Total docs: {len(docs)}
Docs selected for image generation: {sum(1 for d in docs if d['want_image'])}
Image policy: {args.image_policy}
Budget cap: ${args.budget_usd}
Estimated cost per image: ${args.estimated_cost_per_image}

## What this contains
- Linked transaction bundles: invoice, receipt, email, note, delivery ticket, bank proof.
- Raw text ground truth.
- Noisy OCR simulation.
- Image prompts for every artifact.
- DocAI labels and LayoutLM placeholders.
- Cross-document transaction graph.

## Important
Images are generated only if you use --generate-images.
Budget control is approximate; check current API pricing and usage dashboard.
"""
    write(out / "README.md", readme)

    # Generate images if requested
    selected = [d for d in docs if d["want_image"]]
    max_by_budget = int(args.budget_usd // args.estimated_cost_per_image)
    if len(selected) > max_by_budget:
        # Prioritize high-value docs.
        priority = {"note": 0, "invoice": 1, "receipt": 2, "delivery_ticket": 3, "inventory_sheet": 4, "email": 5, "bank_proof": 6}
        selected.sort(key=lambda d: (priority.get(d["doc_type"], 9), d["doc_id"]))
        selected = selected[:max_by_budget]

    write(out / "manifests/image_generation_plan.csv", rows_to_csv(selected))
    print(f"Generated {len(docs)} text docs.")
    print(f"Selected {len(selected)} images under estimated budget ${args.budget_usd} at ${args.estimated_cost_per_image}/image.")
    print(f"Output: {out.resolve()}")

    if args.dry_run or not args.generate_images:
        print("Dry/text-only mode: no images generated.")
        return

    if OpenAI is None:
        raise SystemExit("Missing openai package. Run: pip install openai")
    client = OpenAI()

    spent_est = 0.0
    for idx, d in enumerate(selected, 1):
        prompt = (out / d["image_prompt_path"]).read_text(encoding="utf-8")
        image_path = out / d["image_path"]
        if image_path.exists():
            print(f"[{idx}/{len(selected)}] skip existing {image_path.name}")
            continue
        if spent_est + args.estimated_cost_per_image > args.budget_usd:
            print("Budget cap reached.")
            break
        print(f"[{idx}/{len(selected)}] generating {d['doc_type']} {d['doc_id']}")
        generate_image_openai(
            client=client,
            model=args.image_model,
            prompt=prompt,
            out_path=image_path,
            size=args.image_size,
            quality=args.image_quality,
        )
        spent_est += args.estimated_cost_per_image
        time.sleep(args.sleep)

    print(f"Estimated image spend: ${spent_est:.2f}")

def rows_to_csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    import io
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="greenfield_dataset")
    p.add_argument("--bundles", type=int, default=120, help="120 bundles gives roughly 600-800 docs.")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="Generate text/prompts/labels only.")
    p.add_argument("--generate-images", action="store_true")
    p.add_argument("--image-policy", choices=["minimal", "efficient", "quality"], default="efficient")
    p.add_argument("--budget-usd", type=float, default=40.0)
    p.add_argument("--estimated-cost-per-image", type=float, default=0.08, help="Conservative budget estimate; update based on current model/size.")
    p.add_argument("--image-model", default=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2"))
    p.add_argument("--image-size", default="1024x1536")
    p.add_argument("--image-quality", default="high")
    p.add_argument("--sleep", type=float, default=0.2)
    return p.parse_args()


if __name__ == "__main__":
    build_dataset(parse_args())
