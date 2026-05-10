"""Seed synthetic rows into stub integration tables (deterministic mini dataset)."""

from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta, timezone

import duckdb

from warehouse.stub_schemas import apply_stub_integration_schemas


def seed_stub_tables(con: duckdb.DuckDBPyConnection, *, seed: int = 42) -> dict[str, int]:
    """Fill GA4 / Google Ads / Customer.io stubs. Returns table -> row counts."""
    apply_stub_integration_schemas(con)
    rnd = random.Random(seed)
    counts: dict[str, int] = {}

    con.execute("DELETE FROM ga4.events WHERE ingestion_mode = 'synthetic'")
    con.execute("DELETE FROM ga4.pseudo_users WHERE ingestion_mode = 'synthetic'")
    base = date.today() - timedelta(days=14)
    users = [f"ga4_user_{i:04d}" for i in range(20)]
    for _ in range(80):
        u = rnd.choice(users)
        con.execute(
            """
            INSERT INTO ga4.events
            (event_date, event_name, user_pseudo_id, transaction_id, value, currency, items, page_location, ingestion_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'synthetic')
            """,
            [
                base + timedelta(days=rnd.randint(0, 13)),
                rnd.choice(["page_view", "purchase", "add_to_cart", "begin_checkout"]),
                u,
                f"TX-{rnd.randint(1, 99999)}" if rnd.random() > 0.7 else None,
                round(rnd.uniform(10, 500), 2) if rnd.random() > 0.5 else None,
                "CAD",
                json.dumps([{"sku": f"GF-SKU-{rnd.randint(1, 99)}", "qty": 1}]),
                "https://example.com/p",
            ],
        )
    counts["ga4.events"] = con.execute(
        "SELECT COUNT(*) FROM ga4.events WHERE ingestion_mode = 'synthetic'"
    ).fetchone()[0]

    for u in users[:10]:
        con.execute(
            """
            INSERT INTO ga4.pseudo_users (user_pseudo_id, first_seen_date, ingestion_mode)
            VALUES (?, ?, 'synthetic')
            """,
            [u, base],
        )

    con.execute("DELETE FROM google_ads.campaign_stats WHERE ingestion_mode = 'synthetic'")
    for d in range(14):
        day = base + timedelta(days=d)
        con.execute(
            """
            INSERT INTO google_ads.campaign_stats
            (campaign_id, campaign_name, date, impressions, clicks, cost_micros, conversions, ingestion_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'synthetic')
            """,
            [
                "cmp_feed",
                "Spring bulk feed",
                day,
                rnd.randint(1000, 50000),
                rnd.randint(10, 800),
                rnd.randint(1_000_000, 50_000_000),
                round(rnd.uniform(0, 40), 2),
            ],
        )
    counts["google_ads.campaign_stats"] = con.execute(
        "SELECT COUNT(*) FROM google_ads.campaign_stats WHERE ingestion_mode = 'synthetic'"
    ).fetchone()[0]

    con.execute("DELETE FROM customerio.deliveries WHERE ingestion_mode = 'synthetic'")
    con.execute("DELETE FROM customerio.profiles WHERE ingestion_mode = 'synthetic'")
    emails = [f"buyer{i}@farm.example" for i in range(15)]
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for i in range(30):
        em = rnd.choice(emails)
        con.execute(
            """
            INSERT INTO customerio.profiles (cio_id, email, created_at, ingestion_mode)
            VALUES (?, ?, ?, 'synthetic')
            """,
            [f"cio_p_{i:05d}", em, now - timedelta(days=rnd.randint(1, 120))],
        )
        sent = now - timedelta(hours=rnd.randint(1, 72))
        opened = sent + timedelta(minutes=rnd.randint(5, 200)) if rnd.random() > 0.4 else None
        clicked = (opened + timedelta(minutes=rnd.randint(1, 60))) if opened and rnd.random() > 0.5 else None
        con.execute(
            """
            INSERT INTO customerio.deliveries
            (delivery_id, campaign_id, recipient_email, event_name, subject, sent_at, opened_at, clicked_at, ingestion_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'synthetic')
            """,
            [
                f"dlv_{i:06d}",
                "camp_newsletter",
                em,
                "sent",
                "Weekly supply specials",
                sent,
                opened,
                clicked,
            ],
        )
    counts["customerio.deliveries"] = con.execute(
        "SELECT COUNT(*) FROM customerio.deliveries WHERE ingestion_mode = 'synthetic'"
    ).fetchone()[0]

    con.execute("DELETE FROM legacy.orders_csv_stub WHERE ingestion_mode = 'synthetic'")
    for i in range(12):
        placed = date.today() - timedelta(days=rnd.randint(1, 90))
        con.execute(
            """
            INSERT INTO legacy.orders_csv_stub
            (external_order_id, customer_email, order_total, currency, placed_at, raw_row, ingestion_mode)
            VALUES (?, ?, ?, 'CAD', ?, ?, 'synthetic')
            """,
            [
                f"LEG-{i+1:05d}",
                rnd.choice(emails),
                round(rnd.uniform(50, 4000), 2),
                placed.isoformat(),
                json.dumps({"channel": "woocommerce_export"}),
            ],
        )
    counts["legacy.orders_csv_stub"] = con.execute(
        "SELECT COUNT(*) FROM legacy.orders_csv_stub WHERE ingestion_mode = 'synthetic'"
    ).fetchone()[0]

    return counts


def seed_synthetic_stripe(con: duckdb.DuckDBPyConnection, *, seed: int = 42) -> int:
    """Replace Stripe tables with compatible synthetic rows when live API is not used."""
    rnd = random.Random(seed)
    con.execute("CREATE SCHEMA IF NOT EXISTS stripe")
    con.execute("DROP TABLE IF EXISTS stripe.stripe_customers")
    con.execute("DROP TABLE IF EXISTS stripe.stripe_charges")
    con.execute("DROP TABLE IF EXISTS stripe.stripe_invoices")
    con.execute(
        """
        CREATE TABLE stripe.stripe_customers (
            id VARCHAR,
            email VARCHAR,
            created BIGINT,
            ingestion_mode VARCHAR DEFAULT 'synthetic'
        )
        """
    )
    con.execute(
        """
        CREATE TABLE stripe.stripe_charges (
            id VARCHAR,
            customer VARCHAR,
            amount BIGINT,
            currency VARCHAR,
            created BIGINT,
            status VARCHAR,
            ingestion_mode VARCHAR DEFAULT 'synthetic'
        )
        """
    )
    con.execute(
        """
        CREATE TABLE stripe.stripe_invoices (
            id VARCHAR,
            customer VARCHAR,
            amount_due BIGINT,
            currency VARCHAR,
            status VARCHAR,
            created BIGINT,
            ingestion_mode VARCHAR DEFAULT 'synthetic'
        )
        """
    )
    rows = 0
    for i in range(25):
        cid = f"cus_syn_{i:04d}"
        con.execute(
            "INSERT INTO stripe.stripe_customers VALUES (?, ?, ?, 'synthetic')",
            [cid, f"customer{i}@pay.example", int(1_600_000_000 + rnd.randint(0, 50_000_000))],
        )
        rows += 1
        con.execute(
            "INSERT INTO stripe.stripe_charges VALUES (?, ?, ?, ?, ?, ?, 'synthetic')",
            [
                f"ch_syn_{i:05d}",
                cid,
                rnd.randint(1000, 500_000),
                "cad",
                int(1_700_000_000 + rnd.randint(0, 10_000_000)),
                "succeeded",
            ],
        )
        rows += 1
        con.execute(
            "INSERT INTO stripe.stripe_invoices VALUES (?, ?, ?, ?, ?, ?, 'synthetic')",
            [
                f"in_syn_{i:05d}",
                cid,
                rnd.randint(1000, 500_000),
                "cad",
                "paid",
                int(1_700_000_000 + rnd.randint(0, 10_000_000)),
            ],
        )
        rows += 1
    return rows
