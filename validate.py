#!/usr/bin/env python3
"""
CLI Data Quality Validation Suite Wrapper.
Usage:
    python validate.py --data run1
    python validate.py --data data/exports
"""
import argparse
import json
import os
import sys
import pandas as pd

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.validation.validator import DataQualityValidator


def load_dataset_from_dir(data_dir: str) -> dict:
    tables = [
        "customers", "products", "consents", "sessions", "carts", "cart_lines",
        "campaigns", "message_templates", "send_attempts", "communication_events",
        "orders", "order_lines", "attributions", "ground_truth"
    ]
    dataset = {}
    for table in tables:
        csv_file = os.path.join(data_dir, f"{table}.csv")
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            # Replace NaN with None
            records = df.where(pd.notnull(df), None).to_dict(orient="records")
            dataset[table] = records
        else:
            dataset[table] = []
    return dataset


def main():
    parser = argparse.ArgumentParser(description="Data Quality Validation Suite")
    parser.add_argument("--data", type=str, default="data/exports", help="Directory containing dataset CSV files")

    args = parser.parse_args()
    data_dir = os.path.abspath(args.data)

    if not os.path.isdir(data_dir):
        print(f"Error: Directory '{data_dir}' does not exist.")
        sys.exit(1)

    print(f"============================================================")
    print(f" Data Quality Validation Suite")
    print(f" Inspecting Directory: {data_dir}")
    print(f"============================================================")

    dataset = load_dataset_from_dir(data_dir)
    validator = DataQualityValidator(dataset)
    summary = validator.run_all_validations()

    print(f"\nIndividual Rule Results:")
    print(f"{'-'*60}")
    for idx, rule in enumerate(summary["rule_results"], 1):
        status_tag = f"[{rule['status']}]"
        print(f" {idx:2d}. {status_tag:<8} {rule['rule_name']:<35} (Errors: {rule['error_count']})")
        if rule["status"] != "PASS" and rule.get("sample_errors"):
            for err in rule["sample_errors"][:2]:
                print(f"      -> {err}")

    print(f"{'-'*60}")
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Passed Rules:   {summary['passed_rules']} / {summary['total_rules']}")
    print(f"Violations:     {summary['total_violations']}")
    print(f"============================================================")

    if summary["failed_rules"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
