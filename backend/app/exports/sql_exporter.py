import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import sqlite
from app.database import Base
import app.models  # Ensure all SQLAlchemy models are registered
from app.generator.synthetic_data_generator import SyntheticDataGenerator


TABLE_MAPPINGS = [
    # (table_name, dataset_key, columns)
    ("products", "products", ["product_id", "sku", "name", "category", "price", "is_active"]),
    ("campaigns", "campaigns", ["campaign_id", "name", "channel", "trigger_delay_minutes", "discount_percent", "is_active", "created_at"]),
    ("message_templates", "message_templates", ["template_id", "campaign_id", "channel", "variant", "subject", "body_template", "is_active"]),
    ("customers", "customers", ["customer_id", "first_name", "last_name", "email", "phone", "preferred_channel", "created_at", "updated_at"]),
    ("consents", "consents", ["consent_id", "customer_id", "channel", "status", "effective_at", "source", "created_at"]),
    ("sessions", "sessions", ["session_id", "customer_id", "device_type", "ip_address", "user_agent", "started_at", "ended_at"]),
    ("carts", "carts", ["cart_id", "customer_id", "session_id", "status", "subtotal", "discount_total", "total_amount", "created_at", "updated_at", "last_activity_at", "abandoned_at", "recovered_at"]),
    ("cart_lines", "cart_lines", ["cart_line_id", "cart_id", "product_id", "quantity", "unit_price", "total_price"]),
    ("orders", "orders", ["order_id", "customer_id", "cart_id", "total_amount", "order_timestamp", "status"]),
    ("order_lines", "order_lines", ["order_line_id", "order_id", "product_id", "quantity", "unit_price", "total_price"]),
    ("send_attempts", "send_attempts", ["send_id", "message_id", "campaign_id", "template_id", "cart_id", "customer_id", "channel", "status", "suppression_reason", "scheduled_at", "sent_at", "created_at"]),
    ("communication_events", "communication_events", ["event_id", "send_id", "event_type", "timestamp", "metadata_json"]),
    ("attributions", "attributions", ["attribution_id", "order_id", "send_id", "campaign_id", "cart_id", "order_timestamp", "qualifying_click_at", "latency_hours", "attributed_revenue", "model", "created_at"]),
    ("anomaly_records", "anomalies", ["anomaly_id", "issue_type", "affected_entity", "affected_record_id", "detected_at", "observed_value", "expected_value", "ground_truth_label", "expected_decision", "actual_decision", "resolution_status"]),
]


def format_sql_value(val: Any) -> str:
    """Formats a Python value for deterministic SQL INSERT statement."""
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "1" if val else "0"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, (datetime, pd.Timestamp)):
        return f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'"
    if isinstance(val, (dict, list)):
        s = json.dumps(val, default=str, separators=(",", ":"))
        return f"'{s.replace(chr(39), chr(39) + chr(39))}'"
    s = str(val).replace("'", "''")
    return f"'{s}'"


def generate_sql_seed(
    dataset: Dict[str, Any],
    scale: str = "starter",
    seed: int = 20261022
) -> str:
    """
    Generates a complete SQLite SQL script with:
    1. Schema DDL (CREATE TABLE) in parent-before-child order.
    2. INSERT statements for every table in the dataset.
    3. PRAGMA foreign_keys = ON and transaction wrappers.
    Output is bitwise deterministic.
    """
    lines: List[str] = []
    lines.append("-- ============================================================")
    lines.append("-- Deterministic SQL Seed Script for Abandoned Cart Recovery & Attribution System")
    lines.append(f"-- Scale: {scale.upper()} | Seed: {seed}")
    lines.append("-- ============================================================\n")
    lines.append("PRAGMA foreign_keys = ON;\n")

    # 1. DROP statements in reverse topological order (children before parents)
    lines.append("-- 1. Schema Teardown (Children Before Parents)")
    for tbl_name, _, _ in reversed(TABLE_MAPPINGS):
        lines.append(f"DROP TABLE IF EXISTS {tbl_name};")
    lines.append("")

    # 2. CREATE TABLE statements in topological order (parents before children)
    lines.append("-- 2. Schema DDL (Parents Before Children)")
    for tbl_name, _, _ in TABLE_MAPPINGS:
        table_obj = Base.metadata.tables[tbl_name]
        ddl = str(CreateTable(table_obj).compile(dialect=sqlite.dialect())).strip() + ";"
        lines.append(ddl)
    lines.append("")

    # 3. INSERT statements in topological order
    lines.append("-- 3. Data Ingestion (Parent-Before-Child Order)")
    lines.append("BEGIN TRANSACTION;")

    for tbl_name, dataset_key, cols in TABLE_MAPPINGS:
        records = dataset.get(dataset_key, [])
        lines.append(f"\n-- Table: {tbl_name} ({len(records)} rows)")
        col_list_str = ", ".join(cols)
        for rec in records:
            val_list_str = ", ".join(format_sql_value(rec.get(c)) for c in cols)
            lines.append(f"INSERT INTO {tbl_name} ({col_list_str}) VALUES ({val_list_str});")

    lines.append("\nCOMMIT;\n")

    return "\n".join(lines)


def write_sql_seed_file(
    dataset: Dict[str, Any],
    filepath: str,
    scale: str = "starter",
    seed: int = 20261022
) -> str:
    """Generates and writes deterministic SQL seed to the specified filepath."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    sql_text = generate_sql_seed(dataset, scale=scale, seed=seed)
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write(sql_text)
    return filepath


def verify_sql_seed_loading(filepath: str) -> Dict[str, int]:
    """
    Loads a SQL seed file into an in-memory SQLite database, verifies foreign-key integrity,
    and returns row counts per table.
    """
    import sqlite3
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    with open(filepath, "r", encoding="utf-8") as f:
        sql_content = f.read()
    conn.executescript(sql_content)

    violations = conn.execute("PRAGMA foreign_key_check;").fetchall()
    if violations:
        raise ValueError(f"Foreign key violations detected: {violations}")

    counts = {}
    for tbl_name, _, _ in TABLE_MAPPINGS:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {tbl_name};").fetchone()[0]
        counts[tbl_name] = cnt

    conn.close()
    return counts


def main():
    parser = argparse.ArgumentParser(description="Deterministic SQL Seed Exporter")
    parser.add_argument("--scale", type=str, default="starter", choices=["starter", "full"], help="Dataset scale")
    parser.add_argument("--seed", type=int, default=20261022, help="Deterministic random seed")
    parser.add_argument("--out", type=str, default="data/exports/seed.sql", help="Output SQL filepath")
    parser.add_argument("--verify", action="store_true", help="Verify loading into in-memory SQLite database")
    args = parser.parse_args()

    out_path = os.path.abspath(args.out)

    if not args.verify or not os.path.exists(out_path):
        print(f"Generating {args.scale.upper()} dataset with seed {args.seed}...")
        gen = SyntheticDataGenerator(scale=args.scale, seed=args.seed)
        dataset = gen.generate_dataset()

        print(f"Exporting SQL seed to {out_path}...")
        write_sql_seed_file(dataset, out_path, scale=args.scale, seed=args.seed)
        file_size_mb = os.path.getsize(out_path) / (1024 * 1024)
        print(f"Successfully wrote SQL seed ({file_size_mb:.2f} MB) to {out_path}!")

    if args.verify or True:
        print("\nVerifying SQL seed loading and foreign-key integrity...")
        counts = verify_sql_seed_loading(out_path)
        print("============================================================")
        print(" In-Memory SQLite Seed Load Verification")
        print(" Foreign Key Check: 0 VIOLATIONS (PASS)")
        print("============================================================")
        for tbl, cnt in counts.items():
            print(f" {tbl:<25}: {cnt:,}")
        print("============================================================")


if __name__ == "__main__":
    main()

