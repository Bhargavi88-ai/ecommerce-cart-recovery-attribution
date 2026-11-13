import os
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any


class ManifestGenerator:
    """
    Computes SHA-256 checksums, row counts, and provenance metadata
    for all exported dataset files.
    """

    @staticmethod
    def calculate_file_hash(filepath: str) -> str:
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def count_file_rows(filepath: str) -> int:
        if not os.path.exists(filepath):
            return 0
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            # subtract 1 for header if csv
            lines = sum(1 for _ in f)
            return max(0, lines - 1 if filepath.endswith(".csv") else lines)

    @classmethod
    def generate_manifest(
        cls,
        export_dir: str,
        scale: str,
        seed: int,
        dataset_name: str = "E-Commerce Abandoned Cart Recovery Dataset"
    ) -> Dict[str, Any]:
        manifest_files = {}
        target_files = [
            "customers.csv", "products.csv", "consents.csv", "sessions.csv",
            "carts.csv", "cart_lines.csv", "campaigns.csv", "message_templates.csv",
            "send_attempts.csv", "communication_events.csv", "orders.csv", "order_lines.csv",
            "attributions.csv", "ground_truth.csv", "ground_truth.json",
            "validation_summary.json", "validation_report.csv", "seed.sql"
        ]

        for fname in target_files:
            fpath = os.path.join(export_dir, fname)
            if os.path.exists(fpath):
                manifest_files[fname] = {
                    "sha256": cls.calculate_file_hash(fpath),
                    "row_count": cls.count_file_rows(fpath),
                    "size_bytes": os.path.getsize(fpath)
                }

        manifest = {
            "dataset_name": dataset_name,
            "synthetic_notice": "ALL DATA CONTAINED HEREIN IS 100% SYNTHETIC AND DOES NOT REPRESENT REAL INDIVIDUALS.",
            "generator_version": "2.0.0",
            "scale": scale,
            "seed": seed,
            "generated_at_utc": "2026-10-22T00:00:00Z",
            "provenance": {
                "author": "Antigravity Solution Architecture",
                "rules": "E-Commerce Inactivity Abandonment + Multi-Channel Consent & Frequency Capping + Last-Click Attribution",
                "attribution_window_days": 7,
                "inactivity_threshold_minutes": 60
            },
            "files": manifest_files
        }
        return manifest

