#!/usr/bin/env python3
"""
GreenField Ultra-Cheap 10k Synthetic Document Generator
=======================================================

Purpose
-------
Generate a large, internally consistent synthetic B2B "real economy" dataset for
Ambrook-style document ingestion / reconciliation / document AI.

Core idea:
- Generate MOST documents as text/CSV/HTML for almost no cost.
- Generate a SMALL high-value subset as images using OpenAI image generation.
- Keep one stable company profile, customer base, products, SKUs, color palette,
  and transaction graph across all docs.

Typical run:
  python greenfield_10k_generator.py --target-docs 10000 --dry-run --overwrite

Then optionally generate images:
  export OPENAI_API_KEY=...
  python greenfield_10k_generator.py \
    --target-docs 10000 \
    --generate-images \
    --image-budget-usd 40 \
    --estimated-cost-per-image 0.08 \
    --overwrite

What it creates
---------------
- raw/company/*
- raw/transactions/transactions.jsonl
- raw/artifacts/*.txt / *.csv / *.html
- prompts/images/*.prompt.txt
- ocr/ground_truth/*
- ocr/noisy/*
- labels/docai/*
- labels/layoutlm_placeholders/*
- manifests/*
- splits/*
- schemas/*
- docs/*

No API spend in dry-run mode.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import mimetypes
import os
import random
import re
import shutil
import time
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    import boto3
except Exception:
    boto3 = None


# ======================================================
# Stable company context
# ======================================================

COMPANY = {
    "legal_name": "GreenField Supply Co. Ltd.",
    "operating_name": "GreenField Farm & Site Supply",
    "address": "17 Sideroad 8, Guelph, ON N1H 6J2",
    "phone": "(519) 822-4419",
    "email": "orders@greenfieldsupply.example",
    "ar_email": "ar@greenfieldsupply.example",
    "dispatch_email": "dispatch@greenfieldsupply.example",
    "hst": "84203 1234 RT0001",
    "bank_account": "Business Chequing ****1182",
    "palette": {
        "forest_green": "#1F4D2B",
        "cream": "#F4F0DD",
        "muted_beige": "#C9B88D",
        "soil_brown": "#4A3520",
        "faded_ink": "#323232",
    },
    "style": "rural Ontario farm supply store; practical, slightly outdated, not corporate SaaS",
}

CUSTOMERS = [
    {"id": "CUST-001", "name": "Maple Ridge Farms Ltd.", "type": "cash crop farm", "city": "Fergus", "terms": "Net 30", "contact": "Jeff Martin", "email": "accounts@mapleridgefarms.example"},
    {"id": "CUST-002", "name": "GreenScape Landscaping Inc.", "type": "landscaper", "city": "Mississauga", "terms": "Net 30", "contact": "Kyle Park", "email": "kyle@greenscapelandscaping.example"},
    {"id": "CUST-003", "name": "Oak Valley Dairy", "type": "dairy farm", "city": "Elora", "terms": "Net 60", "contact": "Sarah Lewis", "email": "sarah@oakvalleydairy.example"},
    {"id": "CUST-004", "name": "NorthLine Contracting", "type": "contractor", "city": "Kitchener", "terms": "Net 30", "contact": "Mike Rowan", "email": "mike@northlinecontracting.example"},
    {"id": "CUST-005", "name": "Riverbend Organics", "type": "organic farm", "city": "St Jacobs", "terms": "Net 15", "contact": "Anita Brooks", "email": "orders@riverbendorganics.example"},
    {"id": "CUST-006", "name": "HighPoint Property Services", "type": "property services", "city": "Cambridge", "terms": "Due on receipt", "contact": "Jason Reid", "email": "jason@highpointproperty.example"},
    {"id": "CUST-007", "name": "Silver Creek Stables", "type": "horse farm", "city": "Milton", "terms": "Net 30", "contact": "Megan Scott", "email": "stableoffice@silvercreek.example"},
    {"id": "CUST-008", "name": "UrbanRoot Gardens Co.", "type": "urban farm", "city": "Toronto", "terms": "Card", "contact": "Priya Nair", "email": "priya@urbanroot.example"},
    {"id": "CUST-009", "name": "ClearPath Utilities", "type": "utility contractor", "city": "Hamilton", "terms": "Net 30", "contact": "Brian Berry", "email": "ap@clearpathutilities.example"},
    {"id": "CUST-010", "name": "Brampton Turf Solutions", "type": "turf installer", "city": "Brampton", "terms": "Net 30", "contact": "Owen Patel", "email": "owen@bramptonturf.example"},
    {"id": "CUST-011", "name": "Elm Lane Poultry", "type": "poultry farm", "city": "Listowel", "terms": "Net 30", "contact": "Gord Allen", "email": "office@elmlanepoultry.example"},
    {"id": "CUST-012", "name": "Stonebridge Estates Maintenance", "type": "property maintenance", "city": "Burlington", "terms": "Net 30", "contact": "Laura Chen", "email": "laura@stonebridge-maint.example"},
]

PRODUCTS = [
    ("GF-FERT-UREA-BULK", "Urea 46-0-0 Bulk (per ton)", ["Urea bulk 46", "Urea 46-0-0 per ton", "bulk urea", "46 urea bulk"], "ton", 710.00, "fertilizer"),
    ("GF-FERT-UREA-55", "Urea 46 granular - 55lb bags", ["urea granular 55lb", "46 urea bags", "Urea 55#", "urea bags"], "bag", 34.50, "fertilizer"),
    ("GF-FERT-START-122412", "Starter Fert 12-24-12 (skid pricing avail)", ["12-24-12 starter", "starter fert skid", "Starter 12/24/12"], "bag", 42.00, "fertilizer"),
    ("GF-LIME-AG-LOAD", "Lime - ag grade (dump trailer load)", ["ag lime load", "lime dump trailer", "ag grade lime"], "load", 540.00, "soil"),
    ("GF-LIME-DOLO-18", "Dolomitic Lime bagged 18kg", ["dolo lime", "dolomitic 18kg", "lime bags"], "bag", 9.75, "soil"),
    ("GF-SOIL-TOP-PREM", "Topsoil screened (premium) per yard", ["screened topsoil", "top soil premium", "premium dirt"], "yd", 46.00, "bulk"),
    ("GF-SOIL-TOP-BASIC", "Top Soil (basic fill) — cheap stuff", ["basic fill", "cheap top soil", "fill dirt"], "yd", 28.00, "bulk"),
    ("GF-SEED-GRASS-CON25", "Grass Seed Mix - Contractor Blend 25kg", ["contractor grass seed", "seed mix 25kg", "Contractor Blend"], "bag", 89.00, "seed"),
    ("GF-SEED-TURF-10", "Grass seed premium turf mix 10lb", ["premium turf 10lb", "turf mix", "grass seed prem"], "bag", 31.50, "seed"),
    ("GF-SEED-ALF-50", "Alfalfa seed coated 50lb sack", ["alfalfa coated", "alfalfa 50#", "coated alf seed"], "sack", 219.00, "seed"),
    ("GF-FEED-CHKN-LAYER20", "Chicken Feed Layer Pellets 20kg", ["layer pellets", "chicken feed 20kg", "hens feed"], "bag", 22.25, "feed"),
    ("GF-FEED-DAIRY4-BULK", "Dairy ration mix #4 (bulk auger fill)", ["dairy #4", "ration mix 4", "bulk dairy feed"], "ton", 492.00, "feed"),
    ("GF-BED-STRAW-DUSTY", "Straw bales (small square, dusty)", ["small straw", "dusty straw bales", "cheap straw"], "bale", 6.50, "bedding"),
    ("GF-BED-STRAW-HORSE", "Straw Bale (clean, horse grade)", ["horse straw", "clean straw", "straw horse grade"], "bale", 8.25, "bedding"),
    ("GF-BED-SHAV-COMP", "Wood shavings compressed bale", ["compressed shavings", "wood shaving bale", "horse shavings"], "bale", 10.75, "bedding"),
    ("GF-CHEM-GLY-4L", "Roundup alt glyphosate 4L jug", ["glyphosate 4L", "roundup alt", "weed spray 4L"], "jug", 68.00, "chemical"),
    ("GF-CHEM-WEED-GEN", "Weed killer concentrate (generic)", ["generic weed killer", "weed conc.", "weed concentrate"], "jug", 39.00, "chemical"),
    ("GF-CHEM-INSECT-ORCH", "Insecticide spray orchard grade", ["orchard insecticide", "insect spray", "orchard spray"], "jug", 83.00, "chemical"),
    ("GF-IRR-DRIP-100", "Drip line 1/2 poly 100ft roll", ["drip line 100ft", "half inch poly", "irrigation drip roll"], "roll", 47.50, "irrigation"),
    ("GF-IRR-HOSE-34", "Water hose heavy duty 3/4", ["3/4 hose", "heavy hose", "water hose hd"], "roll", 64.00, "irrigation"),
    ("GF-FENCE-WIRE-200", "Fence wire galvanized 200m spool", ["galv fence wire", "wire 200m", "fencing spool"], "spool", 129.00, "fencing"),
    ("GF-FENCE-TPOST-6", "T-posts 6ft green bundle of 10", ["6ft green t posts", "T post bundle", "posts 10 pack"], "bundle", 79.00, "fencing"),
    ("GF-FENCE-CHARGER-SOLAR", "Electric fence charger solar", ["solar fence charger", "fence charger", "solar zapper"], "ea", 189.00, "fencing"),
    ("GF-BULK-GRAVEL-34", "Gravel 3/4 clear stone per ton", ["3/4 clear", "clear stone", "gravel 3/4"], "ton", 42.00, "bulk"),
    ("GF-BULK-CRUSHER", "Crusher run gravel driveway mix", ["crusher run", "driveway mix", "crush run"], "ton", 36.00, "bulk"),
    ("GF-BULK-SAND-MASON", "Sand - masonry (washed) yard", ["mason sand", "washed sand", "sand yard"], "yd", 38.00, "bulk"),
    ("GF-SEASON-SALT-20", "Ice melt salt (road salt) 20kg", ["road salt 20kg", "ice melt", "salt bags"], "bag", 12.00, "seasonal"),
    ("GF-SEASON-PETMELT", "Ice Melt Premium (pet safe)", ["pet melt", "premium ice melt", "pet safe salt"], "bag", 18.50, "seasonal"),
    ("GF-SITE-GLOVES-50", "Work gloves (bulk pack 50)", ["gloves bulk", "work glove box", "gloves 50 pack"], "case", 55.00, "site"),
    ("GF-SITE-TARP-1012", "Blue tarp 10x12 (heavy duty-ish)", ["blue tarp", "10x12 tarp", "hd-ish tarp"], "ea", 16.75, "site"),
]
PRODUCTS = [
    {"sku": sku, "name": name, "messy": messy, "unit": unit, "price": price, "category": cat}
    for sku, name, messy, unit, price, cat in PRODUCTS
]

VENDORS = [
    "Fertilizer Depot Inc.",
    "Ontario Seed & Turf Wholesale",
    "Wellington Aggregates Yard Ticket",
    "County Hardware & Farm Supply",
    "Tri-County Feed Mill",
    "Guelph AgriChem Wholesale",
    "Waterloo Farm Hardware",
]

PAYMENT_METHODS = ["EFT", "e-transfer", "cheque", "Interac", "Visa", "on account"]
AMBIGUITIES = ["none", "same_as_last_time", "price_changed", "partial_delivery", "handwritten_correction", "split_payment", "substitution", "missing_po"]
QUALITY_LEVELS = ["clean", "normal", "messy", "bad_phone_photo", "cropped_shadow", "faxed_lowres", "stapled_bundle"]

SCALE_PROFILES = {
    "minimal": {"num_customers": 24, "num_skus": 45, "num_orders": 400},
    "balanced": {"num_customers": 90, "num_skus": 120, "num_orders": 1800},
    "maximal": {"num_customers": 240, "num_skus": 260, "num_orders": 5200},
}

CATEGORY_CUSTOMER_HINTS = {
    "fertilizer": {"cash crop farm", "organic farm"},
    "soil": {"cash crop farm", "organic farm", "landscaper", "urban farm"},
    "seed": {"cash crop farm", "organic farm", "urban farm", "landscaper", "turf installer"},
    "chemical": {"cash crop farm", "organic farm"},
    "irrigation": {"cash crop farm", "organic farm", "landscaper", "contractor", "utility contractor", "property services", "turf installer"},
    "bulk": {"landscaper", "property services", "property maintenance", "contractor", "utility contractor", "turf installer", "cash crop farm"},
    "site": {"landscaper", "contractor", "utility contractor", "property services", "property maintenance", "dairy farm", "horse farm", "poultry farm", "turf installer"},
    "seasonal": {"landscaper", "property services", "property maintenance", "turf installer"},
    "feed": {"dairy farm", "poultry farm", "horse farm"},
    "bedding": {"horse farm", "dairy farm", "poultry farm"},
    "fencing": {"horse farm", "dairy farm", "cash crop farm", "contractor", "utility contractor", "poultry farm"},
}


# ======================================================
# Models and helpers
# ======================================================

@dataclass
class LineItem:
    sku: str
    canonical_name: str
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
    paid_date: str
    items: list[LineItem]
    subtotal: float
    hst: float
    total: float
    payment_method: str
    payment_ref: str
    ambiguity: str
    quality: str
    po_number: str

def safe(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()

def money(x: float) -> str:
    return f"{x:,.2f}"

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def random_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))

def customer_product_pool(customer: dict[str, Any]) -> list[dict[str, Any]]:
    cats = allowed_categories_for_customer_type(customer["type"])
    pool = [p for p in PRODUCTS if p["category"] in cats]
    return pool or PRODUCTS


def allowed_categories_for_customer_type(customer_type: str) -> list[str]:
    t = customer_type
    if any(x in t for x in ["crop", "organic"]):
        return ["fertilizer", "soil", "seed", "chemical", "irrigation"]
    elif any(x in t for x in ["landscaper", "turf", "property"]):
        return ["bulk", "seed", "site", "seasonal", "irrigation"]
    elif any(x in t for x in ["dairy", "horse", "poultry"]):
        return ["feed", "bedding", "fencing", "site"]
    elif any(x in t for x in ["contractor", "utility"]):
        return ["bulk", "fencing", "site", "irrigation"]
    return ["bulk", "site", "seed"]

def qty_for(unit: str) -> float:
    if unit in ["ton", "yd"]:
        return round(random.choice([1, 1.5, 2, 2.5, 3, 4, 4.5, 5, 6, 8, 10, 12, 16]), 1)
    if unit == "load":
        return random.choice([1, 2, 3])
    if unit in ["bag", "bale"]:
        return random.choice([4, 6, 8, 10, 12, 20, 25, 30, 40, 50, 80])
    return random.choice([1, 2, 3, 4, 6, 8, 10])

def generate_transaction(i: int, start: date, end: date) -> Transaction:
    customer = random.choice(CUSTOMERS)
    d = random_date(start, end)
    terms_days = 60 if "60" in customer["terms"] else 30 if "30" in customer["terms"] else 7
    due = d + timedelta(days=terms_days)
    paid = d + timedelta(days=random.randint(1, max(2, min(terms_days + 8, 70))))
    invoice_no = f"GF-{10480+i:05d}"

    items = []
    for p in random.sample(customer_product_pool(customer), k=random.randint(2, 5)):
        qty = qty_for(p["unit"])
        unit_price = round(p["price"] * random.uniform(0.92, 1.10), 2)
        items.append(LineItem(
            sku=p["sku"],
            canonical_name=p["name"],
            messy_name=random.choice(p["messy"]),
            qty=qty,
            unit=p["unit"],
            unit_price=unit_price,
            line_total=round(qty * unit_price, 2),
        ))

    if random.random() < 0.82:
        price = random.choice([65, 75, 85, 95, 120, 150, 185, 225])
        items.append(LineItem("SERV-DELIVERY", "Delivery / truck run", random.choice(["delivery - truck", "bulk dump delivery", "local run", "delivery charge"]), 1, "ea", price, price))

    if random.random() < 0.12:
        # Intentional discount / credit line edge case
        discount = -random.choice([15, 25, 40, 55, 75])
        items.append(LineItem("SERV-DISCOUNT", "Account discount / price adjustment", "acct discount", 1, "ea", discount, discount))

    subtotal = round(sum(x.line_total for x in items), 2)
    hst = round(subtotal * 0.13, 2)
    total = round(subtotal + hst, 2)
    payment_method = random.choice(PAYMENT_METHODS)
    ref_prefix = re.sub(r"[^A-Z]", "", customer["name"].upper())[:6] or "GREEN"
    payment_ref = f"{ref_prefix}-{invoice_no[-4:]}" if payment_method in ["EFT", "e-transfer"] else f"CHK-{random.randint(1000,9999)}" if payment_method == "cheque" else f"AUTH-{random.randint(100000,999999)}"

    return Transaction(
        tx_id=f"TX-{i:06d}",
        invoice_no=invoice_no,
        customer=customer,
        date=d.isoformat(),
        due_date=due.isoformat(),
        paid_date=paid.isoformat(),
        items=items,
        subtotal=subtotal,
        hst=hst,
        total=total,
        payment_method=payment_method,
        payment_ref=payment_ref,
        ambiguity=random.choice(AMBIGUITIES),
        quality=random.choice(QUALITY_LEVELS),
        po_number=f"PO-{random.randint(2000,9999)}" if random.random() < 0.55 else "",
    )


# ======================================================
# Artifact text generators
# ======================================================

def invoice_doc(tx: Transaction) -> str:
    rows = "\n".join([
        f"{li.sku:<20} {li.messy_name:<38} {li.qty:<7} {li.unit:<6} {money(li.unit_price):>9} {money(li.line_total):>10}"
        for li in tx.items
    ])
    scribble = {
        "same_as_last_time": "PEN NOTE: same pricing as last time?? verify",
        "price_changed": "PEN NOTE: customer asked why price changed",
        "partial_delivery": "PEN NOTE: partial delivery - send rest Friday",
        "handwritten_correction": "PEN NOTE: crossed out old total, total circled",
        "split_payment": "PEN NOTE: split payment expected",
        "substitution": "PEN NOTE: substituted equivalent product",
        "missing_po": "PEN NOTE: missing PO, call office",
        "none": f"PEN NOTE: Thanks {tx.customer['contact'].split()[0]}! Call if you need anything else",
    }[tx.ambiguity]
    return f"""GreenField Farm & Site Supply
{COMPANY['address']}     {COMPANY['phone']}
HST # {COMPANY['hst']}

INVOICE: {tx.invoice_no}          Date: {tx.date}
Due: {tx.due_date}                Terms: {tx.customer['terms']}
PO: {tx.po_number or "n/a / txt order"}

BILL TO:
{tx.customer['name']}
{tx.customer['city']}, ON
Attn: {tx.customer['contact']}

SKU                  Description                            Qty     Unit    Unit Price      Amount
-----------------------------------------------------------------------------------------------
{rows}

Subtotal:      {money(tx.subtotal)}
HST 13%:       {money(tx.hst)}
TOTAL DUE:    ${money(tx.total)}

Payment method expected: {tx.payment_method}
Payment ref: {tx.payment_ref}
{scribble}
"""

def vendor_receipt_doc(tx: Transaction) -> str:
    vendor = random.choice(VENDORS)
    main = random.choice([x for x in tx.items if x.sku.startswith("GF-")] or tx.items)
    qty = max(1, round(main.qty * random.uniform(1.5, 4.0), 1))
    price = round(main.unit_price * random.uniform(0.62, 0.88), 2)
    fee = random.choice([0, 12, 18, 25, 36, 45, 60])
    subtotal = round(qty * price + fee, 2)
    hst = round(subtotal * 0.13, 2)
    total = round(subtotal + hst, 2)
    return f"""{vendor}
RECEIPT / YARD TICKET #{random.randint(20000,99999)}       {tx.date}
Sold to: GreenField Supply Co. Ltd.

Item                               Qty      Unit    Price       Amount
----------------------------------------------------------------------
{main.messy_name:<34} {qty:<8} {main.unit:<6} {money(price):>8} {money(qty*price):>10}
handling / fuel / pallet fee        1        ea      {money(fee):>8} {money(fee):>10}

Subtotal: {money(subtotal)}
HST:      {money(hst)}
TOTAL:    ${money(total)}
Paid by: {random.choice(["Visa ending 4102", "EFT batch", "Interac", "cheque", "account charge"])}
"""

def customer_email_doc(tx: Transaction) -> str:
    first = tx.customer["contact"].split()[0]
    items = ", ".join([li.messy_name for li in tx.items[:2]])
    line = {
        "same_as_last_time": "same as last time if the price is close",
        "price_changed": "did the price go up or can you hold old price?",
        "partial_delivery": "send what you have and backorder the rest",
        "handwritten_correction": "also can you double check the total on the invoice",
        "split_payment": "we may pay half now and half after delivery",
        "substitution": "if you don't have it, use the cheaper mix",
        "missing_po": "PO is coming later, just get it moving",
        "none": "put it on our account please",
    }[tx.ambiguity]
    return f"""From: {tx.customer['email']}
To: {COMPANY['email']}
Subject: order for {tx.date}

hey,

can you get us {items} for {tx.date}?
{line}

ship/deliver to {tx.customer['city']} if possible.

thanks,
{first}
{tx.customer['name']}
"""

def email_thread_doc(tx: Transaction) -> str:
    return f"""EMAIL THREAD EXPORT

From: {tx.customer['email']}
To: {COMPANY['email']}
Subject: Re: {tx.invoice_no}

Customer:
Can you resend the invoice? AP says they need the ref again.

GreenField:
Attached invoice {tx.invoice_no}. Total is ${money(tx.total)}. Payment ref {tx.payment_ref}.

Customer:
ok thanks. should go out {tx.paid_date}.
"""

def handwritten_note_doc(tx: Transaction) -> str:
    li = random.choice(tx.items)
    return f"""HANDWRITTEN NOTE TRANSCRIPTION:
{tx.customer['contact'].split()[0]} / {tx.customer['name'].split()[0]}
{li.messy_name} - {li.qty} {li.unit}
{random.choice(["call before dumping", "gate code from last job", "cheque ready?", "rush before rain", "same as last time", "price check"])}
ref {tx.invoice_no} / {tx.payment_ref}
"""

def delivery_ticket_doc(tx: Transaction) -> str:
    rows = "\n".join([f"{li.qty:<8} {li.unit:<6} {li.messy_name}" for li in tx.items[:random.randint(1, min(4, len(tx.items)))]] )
    return f"""GREENFIELD FARM & SITE SUPPLY       DELIVERY TICKET #{random.randint(80000,89999)}
Date: {tx.date}
Customer: {tx.customer['name']}
Location: {tx.customer['city']}, ON
Driver: {random.choice(["Mike", "T.S.", "Wayne", "Rob", "Dylan"])}

QTY      UNIT   DESCRIPTION
-----------------------------------------
{rows}

Notes: {random.choice(["Deliver by Thurs morning", "Call before dumping", "Leave by north gate", "Customer signed on arrival", "Road muddy, use side lane", "partial load only"])}
Received by: ____________________
"""

def bank_proof_doc(tx: Transaction) -> str:
    amount = tx.total
    if tx.ambiguity == "split_payment":
        amount = round(tx.total * random.choice([0.5, 0.6, 0.75]), 2)
    return f"""Mobile banking transaction detail

Account: {COMPANY['bank_account']}
Date posted: {tx.paid_date}
Description: {tx.payment_method} {tx.customer['name']} {tx.payment_ref}
Amount: +${money(amount)}
Memo: invoice {tx.invoice_no}
Status: posted
"""

def cheque_stub_doc(tx: Transaction) -> str:
    return f"""CHEQUE STUB / REMITTANCE
Customer: {tx.customer['name']}
Cheque/ref: {tx.payment_ref}
Date: {tx.paid_date}
Invoice: {tx.invoice_no}
Amount: ${money(tx.total)}
Notes: {random.choice(["paid in full", "less credit from last order", "AP batch", "hold receipt"])}
"""

def sms_thread_doc(tx: Transaction) -> str:
    first = tx.customer["contact"].split()[0]
    li = random.choice(tx.items)
    return f"""TEXT MESSAGE TRANSCRIPT

{first}: can u get {li.messy_name} tmrw?
GreenField: how much do you need
{first}: {li.qty} {li.unit} maybe more if price ok
GreenField: ok putting it on {tx.invoice_no}
{first}: thx
"""

def product_catalog_doc() -> str:
    rows = "\n".join([f"{p['sku']} :: {random.choice(p['messy'])} / {p['name']} / ${money(p['price'])} per {p['unit']}" for p in PRODUCTS])
    return f"""GREENFIELD FARM & SITE SUPPLY - SPRING PRODUCT DUMP
copied from old price sheet, prices change without notice

{rows}

Delivery available. Bulk pricing may vary by customer/account.
"""

def old_website_doc() -> str:
    items = "\n".join([f"<li>{p['name']} - call for current price</li>" for p in PRODUCTS[:22]])
    return f"""<html>
<head><title>GreenField Farm and Site Supply - Guelph Ontario</title></head>
<body bgcolor="#f4f0dd" text="#1f4d2b">
<table width="780" align="center">
<tr><td><h1>GreenField Farm & Site Supply</h1></td></tr>
<tr><td>Home | Products | Delivery | Contact</td></tr>
<tr><td><p>Farm inputs, gravel, seed, feed, fencing. Serving Guelph, Fergus, Elora, Kitchener and area.</p></td></tr>
<tr><td><ul>{items}</ul></td></tr>
<tr><td>Call {COMPANY['phone']} - prices subject to spring rush</td></tr>
</table>
</body>
</html>
"""

def inventory_csv(transactions: list[Transaction], batch_id: str) -> str:
    usage: dict[str, float] = {}
    names: dict[str, str] = {}
    units: dict[str, str] = {}
    for tx in transactions:
        for li in tx.items:
            if li.sku.startswith("GF-"):
                usage[li.sku] = usage.get(li.sku, 0) + li.qty
                names[li.sku] = li.canonical_name
                units[li.sku] = li.unit
    rows = ["batch_id,sku,name,starting_qty,ordered_out,restocked,ending_qty,unit,notes"]
    for sku, out in sorted(usage.items()):
        starting = random.randint(35, 250)
        restocked = random.choice([0, 0, 0, 10, 20, 30, 50, 100])
        ending = round(starting - out + restocked, 1)
        note = random.choice(["", "counted by Mike", "check bin", "handwritten correction", "low stock"])
        rows.append(f"{batch_id},{sku},{names[sku]},{starting},{round(out,1)},{restocked},{ending},{units[sku]},{note}")
    return "\n".join(rows) + "\n"

def bank_csv(transactions: list[Transaction], batch_id: str) -> str:
    rows = ["batch_id,date,description,amount,type,invoice_no,payment_ref,customer"]
    for tx in transactions:
        amount = tx.total if tx.ambiguity != "split_payment" else round(tx.total * random.choice([0.5, 0.6, 0.75]), 2)
        rows.append(f"{batch_id},{tx.paid_date},{tx.payment_method} {tx.customer['name']} {tx.payment_ref},{money(amount)},credit,{tx.invoice_no},{tx.payment_ref},{tx.customer['name']}")
    return "\n".join(rows) + "\n"


def order_confirmation_doc(order: dict[str, Any]) -> str:
    lines = "\n".join(
        f"- {li['sku']} {li['qty']} {li['unit']} @ ${money(li['unit_price'])} ({money(li['line_total'])})"
        for li in order["line_items"]
    )
    return f"""SHOP ORDER CONFIRMATION
Order: {order['order_id']}
Customer: {order['customer_name']}
Date: {order['order_date']}
Status: {order['status']}
Currency: CAD

Items:
{lines}

Subtotal: ${money(order['subtotal'])}
Discount: ${money(order['discount_total'])}
Tax: ${money(order['tax_total'])}
Shipping: ${money(order['shipping_total'])}
Total: ${money(order['grand_total'])}
"""


def packing_slip_doc(order: dict[str, Any], fulfillment: dict[str, Any]) -> str:
    lines = "\n".join(
        f"{li['sku']}  qty={li['qty']}  loc={fulfillment['location_id']}"
        for li in order["line_items"]
    )
    return f"""PACKING SLIP
Fulfillment: {fulfillment['fulfillment_id']}
Order: {order['order_id']}
Customer: {order['customer_name']}
Carrier: {fulfillment['carrier']}
Tracking: {fulfillment['tracking_number']}
Fulfilled at: {fulfillment['fulfilled_at']}

{lines}
"""


def refund_notice_doc(refund: dict[str, Any], order: dict[str, Any]) -> str:
    return f"""REFUND NOTICE
Refund id: {refund['refund_id']}
Order: {order['order_id']}
Customer: {order['customer_name']}
Reason: {refund['reason']}
Date: {refund['created_at']}
Amount: ${money(refund['amount'])}
Status: posted
"""


def payout_report_doc(payout: dict[str, Any]) -> str:
    return f"""SHOPIFY PAYOUT REPORT
Payout id: {payout['payout_id']}
Payout date: {payout['payout_date']}
Gross: ${money(payout['gross'])}
Fees: ${money(payout['fees'])}
Net: ${money(payout['net'])}
Transactions: {payout['transaction_count']}
"""


def supplier_po_doc(po: dict[str, Any]) -> str:
    rows = "\n".join(
        f"{li['sku']} x {li['qty']} {li['unit']} @ ${money(li['unit_price'])}"
        for li in po["line_items"]
    )
    return f"""SUPPLIER PURCHASE ORDER
PO: {po['po_id']}
Vendor: {po['vendor']}
Created: {po['created_at']}
Expected: {po['expected_receipt_date']}
Status: {po['status']}

{rows}
"""


def inventory_adjustment_doc(adj: dict[str, Any]) -> str:
    return f"""INVENTORY ADJUSTMENT LOG
Adjustment id: {adj['adjustment_id']}
SKU: {adj['sku']}
Location: {adj['location_id']}
Delta: {adj['delta_qty']}
Reason: {adj['reason']}
Timestamp: {adj['created_at']}
"""


def generate_retail_dataset(
    txs: list[Transaction],
    profile: dict[str, int],
    refund_rate: float,
    return_rate: float,
) -> dict[str, Any]:
    locations = [
        {"location_id": "LOC-GUELPH-WH", "name": "Guelph Warehouse"},
        {"location_id": "LOC-GUELPH-YARD", "name": "Guelph Yard"},
        {"location_id": "LOC-KIT-STAGE", "name": "Kitchener Staging"},
    ]

    customers = []
    for i in range(profile["num_customers"]):
        base = CUSTOMERS[i % len(CUSTOMERS)]
        customers.append({
            **base,
            "id": f"CUST-{i+1:05d}",
            "name": f"{base['name']} #{i // len(CUSTOMERS) + 1}",
            "shopify_customer_id": f"shop_customer_{i+1:06d}",
        })

    products = []
    for i in range(profile["num_skus"]):
        base = PRODUCTS[i % len(PRODUCTS)]
        suffix = i // len(PRODUCTS) + 1
        products.append({
            **base,
            "sku": f"{base['sku']}-V{suffix:02d}",
            "product_id": f"prod_{i+1:06d}",
            "variant_id": f"var_{i+1:06d}",
            "is_active": True,
        })

    orders: list[dict[str, Any]] = []
    fulfillments: list[dict[str, Any]] = []
    refunds: list[dict[str, Any]] = []
    returns: list[dict[str, Any]] = []
    shipping_events: list[dict[str, Any]] = []
    payment_transactions: list[dict[str, Any]] = []
    tax_lines: list[dict[str, Any]] = []
    discounts: list[dict[str, Any]] = []
    inventory_adjustments: list[dict[str, Any]] = []
    supplier_purchase_orders: list[dict[str, Any]] = []
    receiving_events: list[dict[str, Any]] = []

    for i in range(profile["num_orders"]):
        tx = txs[i % len(txs)]
        customer = random.choice(customers)
        order_id = f"ord_{i+1:07d}"
        order_date = tx.date
        line_items = []
        subtotal = 0.0
        for p in random.sample(customer_product_pool(customer), k=random.randint(1, 4)):
            qty = qty_for(p["unit"])
            unit_price = round(p["price"] * random.uniform(0.94, 1.12), 2)
            line_total = round(qty * unit_price, 2)
            line_items.append({
                "sku": p["sku"],
                "qty": qty,
                "unit": p["unit"],
                "unit_price": unit_price,
                "line_total": line_total,
                "category": p["category"],
            })
            subtotal += line_total
        subtotal = round(subtotal, 2)
        discount_total = round(subtotal * random.choice([0, 0, 0.03, 0.05, 0.1]), 2)
        shipping_total = random.choice([0, 25, 35, 49, 75])
        taxable = max(0.0, subtotal - discount_total + shipping_total)
        tax_total = round(taxable * 0.13, 2)
        grand_total = round(taxable + tax_total, 2)
        status = random.choice(["open", "fulfilled", "partially_fulfilled", "closed"])
        order = {
            "order_id": order_id,
            "order_number": 30000 + i,
            "customer_id": customer["shopify_customer_id"],
            "customer_name": customer["name"],
            "order_date": order_date,
            "line_items": line_items,
            "subtotal": subtotal,
            "discount_total": discount_total,
            "shipping_total": shipping_total,
            "tax_total": tax_total,
            "grand_total": grand_total,
            "status": status,
            "source_tx_id": tx.tx_id,
            "source_invoice_no": tx.invoice_no,
            "payment_ref": tx.payment_ref,
        }
        orders.append(order)
        tax_lines.append({"order_id": order_id, "title": "HST", "rate": 0.13, "amount": tax_total})
        if discount_total > 0:
            discounts.append({
                "discount_id": f"disc_{i+1:07d}",
                "order_id": order_id,
                "type": random.choice(["seasonal", "volume", "account_adjustment"]),
                "amount": discount_total,
            })

        fulfilled_at = date.fromisoformat(order_date) + timedelta(days=random.randint(0, 6))
        fulfillment = {
            "fulfillment_id": f"ful_{i+1:07d}",
            "order_id": order_id,
            "location_id": random.choice(locations)["location_id"],
            "carrier": random.choice(["Purolator", "Fleet", "Pickup", "Canada Post"]),
            "tracking_number": f"TRK-{i+1:07d}",
            "fulfilled_at": fulfilled_at.isoformat(),
        }
        fulfillments.append(fulfillment)
        shipping_events.extend([
            {"event_id": f"ship_{i+1:07d}_1", "order_id": order_id, "event": "label_created", "at": order_date},
            {"event_id": f"ship_{i+1:07d}_2", "order_id": order_id, "event": "in_transit", "at": (fulfilled_at + timedelta(days=1)).isoformat()},
            {"event_id": f"ship_{i+1:07d}_3", "order_id": order_id, "event": "delivered", "at": (fulfilled_at + timedelta(days=2)).isoformat()},
        ])
        payment_transactions.append({
            "payment_id": f"pay_{i+1:07d}",
            "order_id": order_id,
            "amount": grand_total,
            "method": tx.payment_method,
            "payment_ref": tx.payment_ref,
            "captured_at": tx.paid_date,
        })

        for li in line_items:
            inventory_adjustments.append({
                "adjustment_id": f"adj_{i+1:07d}_{safe(li['sku'])}",
                "sku": li["sku"],
                "location_id": fulfillment["location_id"],
                "delta_qty": -li["qty"],
                "reason": "order_fulfillment",
                "created_at": fulfillment["fulfilled_at"],
            })

        if random.random() < refund_rate:
            amount = round(grand_total * random.choice([0.2, 0.35, 0.5, 1.0]), 2)
            refund = {
                "refund_id": f"ref_{i+1:07d}",
                "order_id": order_id,
                "amount": amount,
                "reason": random.choice(["damaged", "late_delivery", "wrong_item", "quality_issue"]),
                "created_at": (fulfilled_at + timedelta(days=random.randint(1, 12))).isoformat(),
            }
            refunds.append(refund)
            if random.random() < return_rate:
                returns.append({
                    "return_id": f"ret_{i+1:07d}",
                    "order_id": order_id,
                    "refund_id": refund["refund_id"],
                    "status": random.choice(["received", "inspected", "restocked"]),
                    "created_at": refund["created_at"],
                })

    payouts = []
    batch_size = 30
    for i in range(0, len(payment_transactions), batch_size):
        chunk = payment_transactions[i:i + batch_size]
        gross = round(sum(p["amount"] for p in chunk), 2)
        fees = round(gross * 0.023, 2)
        payouts.append({
            "payout_id": f"pay_out_{i // batch_size + 1:05d}",
            "payout_date": chunk[-1]["captured_at"],
            "gross": gross,
            "fees": fees,
            "net": round(gross - fees, 2),
            "transaction_count": len(chunk),
            "payment_ids": [p["payment_id"] for p in chunk],
        })

    for i, p in enumerate(products):
        location = random.choice(locations)
        qty = random.randint(60, 350)
        po = {
            "po_id": f"po_{i+1:06d}",
            "vendor": random.choice(VENDORS),
            "created_at": date(2025, 12, 15).isoformat(),
            "expected_receipt_date": date(2026, 1, 5).isoformat(),
            "status": "received",
            "line_items": [{"sku": p["sku"], "qty": qty, "unit": p["unit"], "unit_price": round(p["price"] * 0.78, 2)}],
        }
        supplier_purchase_orders.append(po)
        receiving_events.append({
            "receiving_id": f"recv_{i+1:06d}",
            "po_id": po["po_id"],
            "location_id": location["location_id"],
            "received_at": po["expected_receipt_date"],
            "sku": p["sku"],
            "qty_received": qty,
        })
        inventory_adjustments.append({
            "adjustment_id": f"adj_recv_{i+1:06d}",
            "sku": p["sku"],
            "location_id": location["location_id"],
            "delta_qty": qty,
            "reason": "po_receipt",
            "created_at": po["expected_receipt_date"],
        })

    inventory_levels: list[dict[str, Any]] = []
    for p in products:
        for loc in locations:
            delta = sum(
                x["delta_qty"] for x in inventory_adjustments
                if x["sku"] == p["sku"] and x["location_id"] == loc["location_id"]
            )
            inventory_levels.append({
                "sku": p["sku"],
                "location_id": loc["location_id"],
                "available_qty": max(0, int(delta + random.randint(0, 60))),
            })

    return {
        "customers": customers,
        "products": products,
        "inventory_locations": locations,
        "inventory_levels": inventory_levels,
        "orders": orders,
        "fulfillments": fulfillments,
        "refunds": refunds,
        "returns": returns,
        "shipping_events": shipping_events,
        "payment_transactions": payment_transactions,
        "tax_lines": tax_lines,
        "discounts": discounts,
        "shopify_payouts": payouts,
        "supplier_purchase_orders": supplier_purchase_orders,
        "receiving_events": receiving_events,
        "inventory_adjustments": inventory_adjustments,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_retail_exports(out: Path, retail: dict[str, Any]) -> None:
    root = out / "raw/retail"
    for table, rows in retail.items():
        write_jsonl(root / f"{table}.jsonl", rows)


def coverage_summary(retail: dict[str, Any], docs: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    entity_counts = {k: len(v) for k, v in retail.items()}
    thresholds = {
        "orders": args.num_orders,
        "customers": args.num_customers,
        "products": args.num_skus,
        "fulfillments": int(args.num_orders * 0.95),
        "payment_transactions": args.num_orders,
        "shopify_payouts": max(1, args.num_orders // 30),
        "supplier_purchase_orders": args.num_skus,
    }
    checks = {
        key: {"actual": entity_counts.get(key, 0), "required": req, "pass": entity_counts.get(key, 0) >= req}
        for key, req in thresholds.items()
    }
    doc_type_counts: dict[str, int] = {}
    for d in docs:
        doc_type_counts[d["doc_type"]] = doc_type_counts.get(d["doc_type"], 0) + 1
    return {
        "scale_profile": args.scale_profile,
        "entity_counts": entity_counts,
        "doc_type_counts": doc_type_counts,
        "checks": checks,
        "all_checks_pass": all(v["pass"] for v in checks.values()),
    }


def validate_consistency(txs: list[Transaction], retail: dict[str, Any], docs: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    order_map = {o["order_id"]: o for o in retail["orders"]}
    payment_by_order = {p["order_id"]: p for p in retail["payment_transactions"]}
    for order in retail["orders"]:
        computed = round(order["subtotal"] - order["discount_total"] + order["shipping_total"] + order["tax_total"], 2)
        if abs(computed - order["grand_total"]) > 0.01:
            errors.append(f"order_total_mismatch:{order['order_id']}")
    for refund in retail["refunds"]:
        payment = payment_by_order.get(refund["order_id"])
        if not payment:
            errors.append(f"refund_without_payment:{refund['refund_id']}")
            continue
        if refund["amount"] > payment["amount"] + 0.01:
            errors.append(f"refund_exceeds_payment:{refund['refund_id']}")
    valid_order_ids = set(order_map.keys())
    for f in retail["fulfillments"]:
        if f["order_id"] not in valid_order_ids:
            errors.append(f"fulfillment_without_order:{f['fulfillment_id']}")
    tx_ids = {t.tx_id for t in txs}
    for o in retail["orders"]:
        if o["source_tx_id"] not in tx_ids:
            errors.append(f"order_missing_source_tx:{o['order_id']}")
    doc_tx_ids = {d["tx_id"] for d in docs if d["tx_id"]}
    missing = sorted(tx_ids - doc_tx_ids)
    if missing:
        errors.append(f"tx_without_docs_count:{len(missing)}")
    return {"hard_errors": errors, "warning_count": 0, "passed": len(errors) == 0}


def validate_plausibility(retail: dict[str, Any]) -> dict[str, Any]:
    failures: dict[str, int] = {
        "category_customer_mismatch": 0,
        "invalid_price_or_qty": 0,
        "invalid_timeline": 0,
        "refund_without_order": 0,
    }
    order_map = {o["order_id"]: o for o in retail["orders"]}
    customer_type_by_id = {c["shopify_customer_id"]: c["type"] for c in retail["customers"]}
    for order in retail["orders"]:
        ctype = customer_type_by_id.get(order["customer_id"], "")
        allowed_categories = set(allowed_categories_for_customer_type(ctype)) if ctype else set()
        for li in order["line_items"]:
            if li["unit_price"] <= 0 or li["qty"] <= 0:
                failures["invalid_price_or_qty"] += 1
            if allowed_categories and li["category"] not in allowed_categories:
                failures["category_customer_mismatch"] += 1
    for fulfillment in retail["fulfillments"]:
        order = order_map.get(fulfillment["order_id"])
        if not order:
            continue
        if fulfillment["fulfilled_at"] < order["order_date"]:
            failures["invalid_timeline"] += 1
    for refund in retail["refunds"]:
        if refund["order_id"] not in order_map:
            failures["refund_without_order"] += 1
    total_failures = sum(failures.values())
    return {
        "rule_failures": failures,
        "pass": total_failures == 0,
        "strict_mode_failed": total_failures > 0,
    }


def upload_dataset_to_r2(out: Path, args: argparse.Namespace) -> dict[str, Any]:
    if boto3 is None:
        raise SystemExit("Install boto3 to use --upload-r2")
    access_key = os.getenv("R2_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("R2_SECRET_ACCESS_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY")
    if not access_key or not secret_key:
        raise SystemExit("Set R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY (or AWS equivalents)")

    endpoint = args.r2_endpoint or os.getenv("R2_ENDPOINT_URL")
    if not endpoint:
        account = os.getenv("R2_ACCOUNT_ID")
        if account:
            endpoint = f"https://{account}.r2.cloudflarestorage.com"
    if not endpoint:
        raise SystemExit("Provide --r2-endpoint or R2_ENDPOINT_URL (or R2_ACCOUNT_ID)")

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )
    prefix = args.r2_prefix.strip("/")
    files = sorted(p for p in out.rglob("*") if p.is_file())
    results = []
    failures = []
    total_bytes = 0
    for path in files:
        rel = path.relative_to(out).as_posix()
        key = f"{prefix}/{rel}" if prefix else rel
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        ok = False
        err = ""
        for _ in range(max(1, args.r2_retries)):
            try:
                client.upload_file(
                    str(path),
                    args.r2_bucket,
                    key,
                    ExtraArgs={"ContentType": content_type},
                )
                ok = True
                break
            except Exception as exc:
                err = str(exc)
                time.sleep(0.4)
        size = path.stat().st_size
        total_bytes += size
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        row = {
            "local_path": rel,
            "bucket": args.r2_bucket,
            "object_key": key,
            "size": size,
            "sha256": digest,
            "uploaded": ok,
            "error": err,
        }
        results.append(row)
        if not ok:
            failures.append(row)
    write_jsonl(out / "manifests/r2_manifest.jsonl", results)
    summary = {
        "bucket": args.r2_bucket,
        "prefix": prefix,
        "endpoint": endpoint,
        "total_files": len(results),
        "total_bytes": total_bytes,
        "uploaded_files": len(results) - len(failures),
        "failed_files": len(failures),
    }
    dump_json(out / "manifests/r2_upload_summary.json", summary)
    if failures:
        raise SystemExit(f"R2 upload failed for {len(failures)} files")
    return summary


ARTIFACT_GENERATORS = [
    ("invoice", invoice_doc),
    ("vendor_receipt", vendor_receipt_doc),
    ("customer_email", customer_email_doc),
    ("email_thread", email_thread_doc),
    ("handwritten_note", handwritten_note_doc),
    ("delivery_ticket", delivery_ticket_doc),
    ("bank_proof", bank_proof_doc),
    ("cheque_stub", cheque_stub_doc),
    ("sms_thread", sms_thread_doc),
]


# ======================================================
# OCR noise, prompts, labels
# ======================================================

def ocr_noise(text: str) -> str:
    out = text
    replacements = [
        ("0", "O"), ("1", "l"), ("5", "S"), ("rn", "m"),
        ("GreenField", "GreenFieId"), ("Invoice", "lnvoice"),
        ("TOTAL", "T0TAL"), ("Amount", "Arnount"), ("@", " at "),
    ]
    for a, b in replacements:
        if random.random() < 0.32:
            out = out.replace(a, b)
    lines = []
    for line in out.splitlines():
        if random.random() < 0.025:
            continue
        if random.random() < 0.06:
            line = " " + line
        if random.random() < 0.04:
            line = line.replace(",", "")
        lines.append(line)
    return "\n".join(lines)

GLOBAL_IMAGE_STYLE = f"""GreenField Farm & Site Supply, fictional Ontario farm supply company.
Stable brand palette: forest green {COMPANY['palette']['forest_green']}, cream {COMPANY['palette']['cream']}, muted beige {COMPANY['palette']['muted_beige']}, soil brown {COMPANY['palette']['soil_brown']}.
Style: rural Ontario, practical, slightly outdated, real small-business paperwork.
Images should be data-dense and realistic, not clean corporate mockups.
Use imperfections: skew, shadows, wrinkles, stains, folds, uneven alignment, phone-photo perspective.
Preserve key names, dates, invoice numbers, totals, SKUs, quantities, and payment references as much as possible.
"""

def image_prompt(doc_type: str, raw_text: str, quality: str) -> str:
    task_map = {
        "invoice": "Create a realistic photographed paper invoice with itemized table, HST, total, account terms, and handwritten circle around total.",
        "vendor_receipt": "Create a crumpled thermal/vendor receipt or yard ticket photo with faded ink, wrinkled paper, and line-item purchase details.",
        "customer_email": "Create a realistic Gmail/Outlook email screenshot with sender, subject, timestamp, and casual body text.",
        "email_thread": "Create a realistic email thread screenshot showing multiple messages and references to invoice/payment.",
        "handwritten_note": "Create a realistic handwritten note in blue pen on scrap paper; must look genuinely handwritten, not typed.",
        "delivery_ticket": "Create a carbon-copy delivery ticket on clipboard/truck dashboard with handwritten fields and signature line.",
        "bank_proof": "Create a mobile banking transaction detail screenshot showing deposit amount, date, ref, and account.",
        "cheque_stub": "Create a photographed cheque stub/remittance slip with invoice number and amount.",
        "sms_thread": "Create a realistic iPhone text message screenshot with short customer/order conversation.",
        "inventory_csv": "Create a printed inventory spreadsheet on a clipboard with many rows, handwritten corrections, crossed-out quantities.",
        "bank_csv": "Create a bank CSV/spreadsheet screenshot or printed transaction export with many rows.",
        "catalog": "Create a printed product catalog/price sheet, outdated rural farm supply design, lots of SKUs and prices.",
        "website": "Create a browser screenshot of an outdated early-2010s small business website.",
        "order_confirmation": "Create an ecommerce order confirmation page or email screenshot with totals and line items.",
        "packing_slip": "Create a warehouse packing slip printed document with SKU, quantities, and tracking details.",
        "refund_notice": "Create a customer-facing refund confirmation message or PDF notice with reason and amount.",
        "payout_report": "Create a payout summary report table showing gross, fees, and net settlement.",
        "supplier_po": "Create a supplier purchase order form with vendor details and ordered SKUs.",
        "inventory_adjustment_log": "Create an inventory adjustment report with SKU deltas, timestamps, and reasons.",
    }
    quality_map = {
        "clean": "mostly readable, mild desk shadow",
        "normal": "slight skew, natural paper texture",
        "messy": "wrinkles, stains, pen marks, imperfect alignment",
        "bad_phone_photo": "tilted phone photo, mild blur, shadow across document",
        "cropped_shadow": "slightly cropped edge, strong side shadow",
        "faxed_lowres": "low-resolution fax/scan look, slightly washed out",
        "stapled_bundle": "looks like part of a stapled packet with another page edge visible",
    }
    return f"""{GLOBAL_IMAGE_STYLE}

Task:
{task_map.get(doc_type, "Create a realistic business document image.")}

Image condition:
{quality_map.get(quality, "realistic handled document")}

Raw source content to represent:
---BEGIN RAW CONTENT---
{raw_text[:4500]}
---END RAW CONTENT---
"""

def docai_label(doc_id: str, doc_type: str, tx: Transaction | None, raw_path: str, image_path: str | None) -> dict[str, Any]:
    entities = []
    if tx:
        entities += [
            {"type": "transaction_id", "text": tx.tx_id},
            {"type": "invoice_number", "text": tx.invoice_no},
            {"type": "customer_name", "text": tx.customer["name"]},
            {"type": "date", "text": tx.date},
            {"type": "due_date", "text": tx.due_date},
            {"type": "paid_date", "text": tx.paid_date},
            {"type": "total", "text": money(tx.total), "number": tx.total},
            {"type": "payment_ref", "text": tx.payment_ref},
            {"type": "payment_method", "text": tx.payment_method},
        ]
        for li in tx.items:
            entities.append({
                "type": "line_item",
                "sku": li.sku,
                "description": li.canonical_name,
                "messy_description": li.messy_name,
                "qty": li.qty,
                "unit": li.unit,
                "unit_price": li.unit_price,
                "line_total": li.line_total,
            })
    return {
        "doc_id": doc_id,
        "doc_type": doc_type,
        "raw_text_path": raw_path,
        "image_path": image_path,
        "entities": entities,
        "bbox_status": "populate_after_real_ocr",
    }


# ======================================================
# Image budget selection
# ======================================================

IMAGE_PRIORITY = {
    "handwritten_note": 0,
    "invoice": 1,
    "vendor_receipt": 2,
    "delivery_ticket": 3,
    "bank_proof": 4,
    "sms_thread": 5,
    "customer_email": 6,
    "email_thread": 7,
    "inventory_csv": 8,
    "cheque_stub": 9,
    "bank_csv": 10,
    "catalog": 11,
    "website": 12,
    "order_confirmation": 6,
    "packing_slip": 4,
    "refund_notice": 7,
    "payout_report": 8,
    "supplier_po": 5,
    "inventory_adjustment_log": 9,
}

def wants_image(doc_type: str, image_fraction: float) -> bool:
    base = {
        "handwritten_note": 1.00,
        "invoice": 0.55,
        "vendor_receipt": 0.50,
        "delivery_ticket": 0.35,
        "bank_proof": 0.22,
        "sms_thread": 0.18,
        "customer_email": 0.14,
        "email_thread": 0.12,
        "cheque_stub": 0.12,
        "inventory_csv": 0.75,
        "bank_csv": 0.45,
        "catalog": 1.00,
        "website": 1.00,
        "order_confirmation": 0.20,
        "packing_slip": 0.25,
        "refund_notice": 0.2,
        "payout_report": 0.3,
        "supplier_po": 0.35,
        "inventory_adjustment_log": 0.2,
    }.get(doc_type, 0.05)
    return random.random() < min(1.0, base * image_fraction)


# ======================================================
# Main build
# ======================================================

def build(args: argparse.Namespace) -> None:
    random.seed(args.seed)
    out = Path(args.out)
    if out.exists() and args.overwrite:
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    for d in [
        "raw/company", "raw/transactions", "raw/artifacts", "raw/retail",
        "prompts/images", "images", "ocr/ground_truth", "ocr/noisy",
        "labels/docai", "labels/field_targets", "labels/layoutlm_placeholders",
        "manifests", "splits", "schemas", "docs"
    ]:
        (out / d).mkdir(parents=True, exist_ok=True)

    profile = SCALE_PROFILES[args.scale_profile].copy()
    if args.num_customers:
        profile["num_customers"] = args.num_customers
    if args.num_skus:
        profile["num_skus"] = args.num_skus
    if args.num_orders:
        profile["num_orders"] = args.num_orders

    # Rough docs per transaction: 9 docs + batch docs. target 10k => ~1050 tx.
    bundles = args.bundles or max(1, profile["num_orders"])

    # Company/profile files
    write(out / "raw/company/profile.txt", f"""{COMPANY['legal_name']}
Operating as: {COMPANY['operating_name']}
Address: {COMPANY['address']}
Phone: {COMPANY['phone']}
Email: {COMPANY['email']}
HST: {COMPANY['hst']}

Fictional Ontario farm supply store serving farms, landscapers, contractors, stables, dairies, and property-service businesses.
Brand palette:
- forest green {COMPANY['palette']['forest_green']}
- cream {COMPANY['palette']['cream']}
- muted beige {COMPANY['palette']['muted_beige']}
- soil brown {COMPANY['palette']['soil_brown']}

Purpose: synthetic multimodal document dataset for Ambrook-style ingestion, OCR, entity extraction, transaction reconciliation, and cross-document linking.
""")
    with (out / "raw/company/customers.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(CUSTOMERS[0].keys()))
        w.writeheader(); w.writerows(CUSTOMERS)
    with (out / "raw/company/products.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["sku", "name", "unit", "price", "category", "messy_aliases"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for p in PRODUCTS:
            w.writerow({k: p[k] for k in ["sku", "name", "unit", "price", "category"]} | {"messy_aliases": " | ".join(p["messy"])})

    txs = [generate_transaction(i + 1, date(2026, 1, 1), date(2026, 12, 15)) for i in range(bundles)]
    with (out / "raw/transactions/transactions.jsonl").open("w", encoding="utf-8") as f:
        for tx in txs:
            f.write(json.dumps(asdict(tx), ensure_ascii=False) + "\n")

    retail = generate_retail_dataset(
        txs=txs,
        profile=profile,
        refund_rate=args.refund_rate,
        return_rate=args.return_rate,
    )
    write_retail_exports(out, retail)

    docs: list[dict[str, Any]] = []

    def add_doc(doc_type: str, raw_text: str, tx: Transaction | None, stem: str, ext: str = "txt", force_image: bool = False) -> None:
        doc_id = safe(stem)
        raw_rel = f"raw/artifacts/{doc_id}.{ext}"
        write(out / raw_rel, raw_text)

        gt_rel = f"ocr/ground_truth/{doc_id}.txt"
        noisy_rel = f"ocr/noisy/{doc_id}.txt"
        write(out / gt_rel, raw_text)
        write(out / noisy_rel, ocr_noise(raw_text))

        quality = tx.quality if tx else random.choice(QUALITY_LEVELS)
        prompt_rel = f"prompts/images/{doc_id}.prompt.txt"
        write(out / prompt_rel, image_prompt(doc_type, raw_text, quality))

        image_selected = force_image or wants_image(doc_type, args.image_fraction)
        image_rel = f"images/{doc_id}.png" if image_selected else ""

        row = {
            "doc_id": doc_id,
            "doc_type": doc_type,
            "tx_id": tx.tx_id if tx else "",
            "invoice_no": tx.invoice_no if tx else "",
            "customer": tx.customer["name"] if tx else "",
            "date": tx.date if tx else "",
            "total": tx.total if tx else "",
            "raw_text_path": raw_rel,
            "ground_truth_ocr_path": gt_rel,
            "noisy_ocr_path": noisy_rel,
            "image_prompt_path": prompt_rel,
            "image_path": image_rel,
            "want_image": image_selected,
        }
        docs.append(row)

        label = docai_label(doc_id, doc_type, tx, raw_rel, image_rel or None)
        dump_json(out / f"labels/docai/{doc_id}.json", label)
        dump_json(out / f"labels/field_targets/{doc_id}.fields.json", {
            "doc_id": doc_id,
            "doc_type": doc_type,
            "tx_id": tx.tx_id if tx else None,
            "fields": label["entities"],
        })
        toks = re.findall(r"\S+", raw_text)[:512]
        dump_json(out / f"labels/layoutlm_placeholders/{doc_id}.json", {
            "doc_id": doc_id,
            "doc_type": doc_type,
            "tokens": toks,
            "bboxes": [[0,0,0,0] for _ in toks],
            "ner_tags": ["O" for _ in toks],
            "note": "Run real OCR after image generation to populate boxes.",
        })

    # Per-transaction docs
    for tx in txs:
        for doc_type, gen in ARTIFACT_GENERATORS:
            add_doc(doc_type, gen(tx), tx, f"{tx.tx_id}_{tx.invoice_no}_{doc_type}")

    # Batch docs: bank CSV and inventory CSV every N tx
    batch_size = args.batch_size
    for i in range(0, len(txs), batch_size):
        batch = txs[i:i+batch_size]
        batch_id = f"BATCH-{i//batch_size+1:04d}"
        add_doc("bank_csv", bank_csv(batch, batch_id), None, f"{batch_id}_bank_csv", "csv")
        add_doc("inventory_csv", inventory_csv(batch, batch_id), None, f"{batch_id}_inventory_csv", "csv")

    # Global docs
    add_doc("catalog", product_catalog_doc(), None, "greenfield_product_catalog_spring_2026", "txt", force_image=True)
    add_doc("website", old_website_doc(), None, "greenfield_old_website_homepage", "html", force_image=True)

    # Retail / Shopify style docs
    for order in retail["orders"][: min(len(retail["orders"]), args.max_retail_docs)]:
        add_doc("order_confirmation", order_confirmation_doc(order), None, f"{order['order_id']}_order_confirmation")
    f_by_order = {f["order_id"]: f for f in retail["fulfillments"]}
    for order in retail["orders"][: min(len(retail["orders"]), args.max_retail_docs)]:
        fulfillment = f_by_order.get(order["order_id"])
        if fulfillment:
            add_doc("packing_slip", packing_slip_doc(order, fulfillment), None, f"{order['order_id']}_{fulfillment['fulfillment_id']}_packing_slip")
    o_by_order = {o["order_id"]: o for o in retail["orders"]}
    for refund in retail["refunds"][: min(len(retail["refunds"]), args.max_retail_docs)]:
        order = o_by_order.get(refund["order_id"])
        if order:
            add_doc("refund_notice", refund_notice_doc(refund, order), None, f"{refund['refund_id']}_refund_notice")
    for payout in retail["shopify_payouts"][: min(len(retail["shopify_payouts"]), args.max_retail_docs)]:
        add_doc("payout_report", payout_report_doc(payout), None, f"{payout['payout_id']}_payout_report")
    for po in retail["supplier_purchase_orders"][: min(len(retail["supplier_purchase_orders"]), args.max_retail_docs)]:
        add_doc("supplier_po", supplier_po_doc(po), None, f"{po['po_id']}_supplier_po")
    for adj in retail["inventory_adjustments"][: min(len(retail["inventory_adjustments"]), args.max_retail_docs)]:
        add_doc("inventory_adjustment_log", inventory_adjustment_doc(adj), None, f"{adj['adjustment_id']}_inventory_adjustment")

    # Trim to target docs if needed? Prefer not to delete because graph consistency matters.
    # If target is approximate, leave as generated.
    # Build manifests
    with (out / "manifests/manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(docs[0].keys()))
        w.writeheader(); w.writerows(docs)
    with (out / "manifests/manifest.jsonl").open("w", encoding="utf-8") as f:
        for row in docs:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    graph = {}
    for tx in txs:
        graph[tx.tx_id] = {
            "invoice_no": tx.invoice_no,
            "customer": tx.customer["name"],
            "date": tx.date,
            "total": tx.total,
            "payment_ref": tx.payment_ref,
            "docs": [d["doc_id"] for d in docs if d["tx_id"] == tx.tx_id],
        }
    dump_json(out / "manifests/transaction_graph.json", graph)
    dump_json(out / "manifests/retail_entity_counts.json", {k: len(v) for k, v in retail.items()})

    # Image selection under budget
    selected = [d for d in docs if d["want_image"]]
    selected.sort(key=lambda d: (IMAGE_PRIORITY.get(d["doc_type"], 99), d["doc_id"]))
    max_images = int(args.image_budget_usd // args.estimated_cost_per_image)
    selected_budgeted = selected[:max_images]
    selected_ids = {d["doc_id"] for d in selected_budgeted}
    for d in docs:
        if d["doc_id"] not in selected_ids:
            d["image_path"] = ""
            d["want_image"] = False

    with (out / "manifests/image_generation_plan.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(docs[0].keys()))
        w.writeheader(); w.writerows(selected_budgeted)

    # Re-write manifest after budget trim
    with (out / "manifests/manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(docs[0].keys()))
        w.writeheader(); w.writerows(docs)

    # Splits by transaction
    tx_ids = [tx.tx_id for tx in txs]
    random.shuffle(tx_ids)
    n = len(tx_ids)
    splits = {
        "train": set(tx_ids[:int(n*0.70)]),
        "val": set(tx_ids[int(n*0.70):int(n*0.85)]),
        "test": set(tx_ids[int(n*0.85):]),
    }
    for split, ids in splits.items():
        write(out / f"splits/{split}_tx_ids.txt", "\n".join(sorted(ids)))
        write(out / f"splits/{split}_doc_ids.txt", "\n".join(sorted(d["doc_id"] for d in docs if d["tx_id"] in ids or d["tx_id"] == "")))

    coverage = coverage_summary(retail, docs, args)
    dump_json(out / "manifests/coverage_summary.json", coverage)
    consistency = validate_consistency(txs, retail, docs)
    dump_json(out / "manifests/consistency_report.json", consistency)
    plausibility = validate_plausibility(retail)
    dump_json(out / "manifests/plausibility_report.json", plausibility)

    if not coverage["all_checks_pass"]:
        raise SystemExit("Coverage checks failed. See manifests/coverage_summary.json")
    if not consistency["passed"]:
        raise SystemExit("Consistency validation failed. See manifests/consistency_report.json")
    if args.strict_plausibility and plausibility["strict_mode_failed"]:
        raise SystemExit("Plausibility validation failed. See manifests/plausibility_report.json")

    # Schemas/docs
    dump_json(out / "schemas/docai_schema.json", {
        "doc_id": "string",
        "doc_type": "string",
        "raw_text_path": "string",
        "image_path": "optional string",
        "entities": [{"type": "string", "text": "string", "bbox": "optional after OCR"}],
    })
    dump_json(out / "schemas/transaction_graph_schema.json", {
        "tx_id": "string",
        "invoice_no": "string",
        "customer": "string",
        "total": "number",
        "payment_ref": "string",
        "docs": ["doc_id"],
    })

    write(out / "docs/style_guide.txt", GLOBAL_IMAGE_STYLE)
    write(out / "docs/prompt.txt", f"""Recreate this dataset:
- Fictional company: {COMPANY['operating_name']} in Guelph, Ontario.
- Stable palette: forest green, cream, muted beige, soil brown.
- Customers: farms, landscapers, contractors, dairies, stables, property services.
- Products: fertilizer, lime, topsoil, seed, feed, bedding, chemicals, irrigation, fencing, gravel, sand, salt, site supplies.
- Generate linked transaction bundles with invoice, vendor receipt, customer email, email thread, handwritten note, delivery ticket, bank proof, cheque stub, SMS thread.
- Generate batch bank CSVs and inventory CSVs.
- Generate maximal retail entities: orders, fulfillments, refunds, returns, payouts, supplier POs, receiving events, and inventory adjustments.
- Maintain internal consistency: same customers, SKUs, invoice numbers, totals, payment refs, and transaction graph.
- Generate mostly text; generate images only for high-value subset under budget.
""")
    write(out / "README.md", f"""# GreenField Ultra-Cheap Dataset

Target docs requested: {args.target_docs}
Bundles generated: {bundles}
Actual docs generated: {len(docs)}
Images selected under budget: {len(selected_budgeted)}
Estimated image budget: ${args.image_budget_usd}
Estimated cost/image: ${args.estimated_cost_per_image}
Estimated image spend if run: ${len(selected_budgeted) * args.estimated_cost_per_image:.2f}

## Use
Text-only:
```bash
python greenfield_10k_generator.py --target-docs 10000 --dry-run --overwrite
```

Generate images:
```bash
export OPENAI_API_KEY=...
python greenfield_10k_generator.py --target-docs 10000 --generate-images --image-budget-usd 40 --estimated-cost-per-image 0.08 --overwrite
```

## Dataset strategy
Most examples are text-only for cheap scale. Images are prioritized for:
1. handwritten notes
2. invoices
3. vendor receipts
4. delivery tickets
5. bank/payment proofs
6. SMS/email screenshots
7. inventory/catalog/website edge cases
""")

    print(f"Output: {out.resolve()}")
    print(f"Bundles: {bundles}")
    print(f"Actual docs: {len(docs)}")
    print(f"Retail orders: {len(retail['orders'])}")
    print(f"Images selected under budget: {len(selected_budgeted)}")
    print(f"Estimated image spend: ${len(selected_budgeted) * args.estimated_cost_per_image:.2f}")

    if args.dry_run or not args.generate_images:
        print("No image API calls made.")
        if args.upload_r2:
            if not args.r2_bucket:
                raise SystemExit("--r2-bucket is required when --upload-r2 is set")
            summary = upload_dataset_to_r2(out, args)
            print(f"Uploaded to R2 bucket={summary['bucket']} files={summary['uploaded_files']}")
        return

    if OpenAI is None:
        raise SystemExit("Install OpenAI SDK: pip install openai")
    client = OpenAI()
    generated = 0
    for i, d in enumerate(selected_budgeted, 1):
        prompt = (out / d["image_prompt_path"]).read_text(encoding="utf-8")
        image_path = out / d["image_path"]
        if image_path.exists():
            continue
        print(f"[{i}/{len(selected_budgeted)}] generating {d['doc_type']} {d['doc_id']}")
        result = client.images.generate(
            model=args.image_model,
            prompt=prompt,
            size=args.image_size,
            quality=args.image_quality,
            n=1,
        )
        b64 = result.data[0].b64_json
        image_path.parent.mkdir(parents=True, exist_ok=True)
        image_path.write_bytes(base64.b64decode(b64))
        generated += 1
        time.sleep(args.sleep)
    print(f"Generated images: {generated}")

    if args.upload_r2:
        if not args.r2_bucket:
            raise SystemExit("--r2-bucket is required when --upload-r2 is set")
        summary = upload_dataset_to_r2(out, args)
        print(f"Uploaded to R2 bucket={summary['bucket']} files={summary['uploaded_files']}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="greenfield_10k_dataset")
    p.add_argument("--target-docs", type=int, default=10000)
    p.add_argument("--bundles", type=int, default=0, help="Override bundle count. Default derived from target-docs.")
    p.add_argument("--scale-profile", choices=sorted(SCALE_PROFILES.keys()), default="maximal")
    p.add_argument("--num-orders", type=int, default=0, help="Override orders generated for retail entities.")
    p.add_argument("--num-customers", type=int, default=0, help="Override customers generated for retail entities.")
    p.add_argument("--num-skus", type=int, default=0, help="Override SKU catalog size for retail entities.")
    p.add_argument("--refund-rate", type=float, default=0.08)
    p.add_argument("--return-rate", type=float, default=0.55)
    p.add_argument("--max-retail-docs", type=int, default=800)
    p.add_argument("--strict-plausibility", action="store_true")
    p.add_argument("--batch-size", type=int, default=50)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--generate-images", action="store_true")
    p.add_argument("--image-fraction", type=float, default=1.0, help="Multiplier before budget trimming. Usually keep 1.0.")
    p.add_argument("--image-budget-usd", type=float, default=40.0)
    p.add_argument("--estimated-cost-per-image", type=float, default=0.08, help="Conservative estimate. Adjust after checking current pricing/usage.")
    p.add_argument("--image-model", default=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2"))
    p.add_argument("--image-size", default="1024x1536")
    p.add_argument("--image-quality", default="high")
    p.add_argument("--sleep", type=float, default=0.15)
    p.add_argument("--upload-r2", action="store_true")
    p.add_argument("--r2-bucket", default=os.getenv("R2_BUCKET", ""))
    p.add_argument("--r2-prefix", default=os.getenv("R2_PREFIX", "greenfield-dataset"))
    p.add_argument("--r2-endpoint", default=os.getenv("R2_ENDPOINT_URL", ""))
    p.add_argument("--r2-retries", type=int, default=3)
    return p.parse_args()


if __name__ == "__main__":
    build(parse_args())
