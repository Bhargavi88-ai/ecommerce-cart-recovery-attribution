import os
import sqlite3
import pytest

from app.generator.synthetic_data_generator import SyntheticDataGenerator
from app.exports.sql_exporter import TABLE_MAPPINGS, generate_sql_seed


def test_starter_seed_sql_loading_and_integrity():
    """
    Loads starter-scale seed.sql into an in-memory SQLite database and verifies:
    1. Schema creation succeeds with foreign keys enabled.
    2. Zero foreign-key violations (PRAGMA foreign_key_check).
    3. Row counts for every table match the generated dataset exactly.
    4. Deterministic byte-for-byte reproducibility.
    """
    seed = 20261022
    scale = "starter"

    # Generate expected dataset
    gen = SyntheticDataGenerator(scale=scale, seed=seed)
    expected_data = gen.generate_dataset()

    # Locate seed.sql
    seed_sql_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "exports", "seed.sql")
    )
    if os.path.exists(seed_sql_path):
        with open(seed_sql_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
    else:
        sql_script = generate_sql_seed(expected_data, scale=scale, seed=seed)

    # 1. Load into in-memory SQLite database with foreign keys enabled
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(sql_script)

    # 2. Check foreign-key integrity
    violations = conn.execute("PRAGMA foreign_key_check;").fetchall()
    assert len(violations) == 0, f"Foreign key check failed with violations: {violations}"

    # 3. Check row counts for every table in parent-before-child order
    actual_counts = {}
    for tbl_name, dataset_key, _ in TABLE_MAPPINGS:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {tbl_name};").fetchone()[0]
        actual_counts[tbl_name] = cnt
        expected_cnt = len(expected_data.get(dataset_key, []))
        assert cnt == expected_cnt, f"Mismatch in {tbl_name}: expected {expected_cnt}, got {cnt}"

    conn.close()

    # 4. Verify deterministic output (same seed -> same bytes)
    script_1 = generate_sql_seed(expected_data, scale=scale, seed=seed)
    script_2 = generate_sql_seed(expected_data, scale=scale, seed=seed)
    assert script_1 == script_2, "SQL seed generation must be bitwise deterministic"
