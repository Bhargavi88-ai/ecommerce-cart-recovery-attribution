import os
import sys
import shutil
import json
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.generator.synthetic_data_generator import SyntheticDataGenerator
from app.exports.exporter import DatasetExporter
from app.exports.manifest_generator import ManifestGenerator


def run_reproducibility_test(scale: str = "starter", seed: int = 20261022):
    print(f"============================================================")
    print(f" Reproducibility Verification Test")
    print(f" Scale: {scale.upper()} | Seed: {seed}")
    print(f"============================================================")

    dir_run1 = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/exports/run1_test"))
    dir_run2 = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/exports/run2_test"))
    report_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/reports"))

    os.makedirs(dir_run1, exist_ok=True)
    os.makedirs(dir_run2, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)

    # Run 1
    print("[1/3] Generating Run 1...")
    gen1 = SyntheticDataGenerator(seed=seed, scale=scale)
    data1 = gen1.generate_dataset()
    exp1 = DatasetExporter(export_dir=dir_run1)
    exp1.export_all(data1, scale=scale, seed=seed)

    # Run 2
    print("[2/3] Generating Run 2...")
    gen2 = SyntheticDataGenerator(seed=seed, scale=scale)
    data2 = gen2.generate_dataset()
    exp2 = DatasetExporter(export_dir=dir_run2)
    exp2.export_all(data2, scale=scale, seed=seed)

    # Compare
    print("[3/3] Comparing row counts and deterministic checksums...")
    target_files = [
        "customers.csv", "products.csv", "consents.csv", "sessions.csv",
        "carts.csv", "cart_lines.csv", "campaigns.csv", "message_templates.csv",
        "send_attempts.csv", "orders.csv", "attributions.csv",
        "ground_truth.csv", "seed.sql"
    ]

    comparison_results = []
    all_matched = True

    for fname in target_files:
        f1 = os.path.join(dir_run1, fname)
        f2 = os.path.join(dir_run2, fname)

        h1 = ManifestGenerator.calculate_file_hash(f1)
        h2 = ManifestGenerator.calculate_file_hash(f2)

        c1 = ManifestGenerator.count_file_rows(f1)
        c2 = ManifestGenerator.count_file_rows(f2)

        match = (h1 == h2) and (c1 == c2)
        if not match:
            all_matched = False

        comparison_results.append({
            "file": fname,
            "run1_row_count": c1,
            "run2_row_count": c2,
            "row_count_match": c1 == c2,
            "run1_sha256": h1,
            "run2_sha256": h2,
            "checksum_match": h1 == h2,
            "status": "MATCH" if match else "MISMATCH"
        })
        print(f"      - {fname:<24} Rows: {c1:<6} HashMatch: {h1 == h2}")

    # Cleanup temporary test directories
    shutil.rmtree(dir_run1, ignore_errors=True)
    shutil.rmtree(dir_run2, ignore_errors=True)

    report = {
        "scale": scale,
        "seed": seed,
        "all_matched": all_matched,
        "total_files_tested": len(target_files),
        "results": comparison_results
    }

    report_path = os.path.join(report_dir, "reproducibility_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"============================================================")
    print(f" Reproducibility Result: {'PASSED (100% IDENTICAL)' if all_matched else 'FAILED'}")
    print(f" Report written to: {report_path}")
    print(f"============================================================")
    return all_matched


if __name__ == "__main__":
    success = run_reproducibility_test()
    if not success:
        sys.exit(1)

