import os
import json
import csv
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from app.exports.manifest_generator import ManifestGenerator
from app.validation.validator import DataQualityValidator


class DatasetExporter:
    """
    Serializes in-memory generated datasets to CSV, JSON, SQL seed, and manifest.
    """

    def __init__(self, export_dir: str):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    def export_all(
        self,
        dataset: Dict[str, Any],
        scale: str,
        seed: int
    ) -> Dict[str, Any]:
        # 1. Run Data Quality Validation
        validator = DataQualityValidator(dataset)
        val_summary = validator.run_all_validations()
        val_report_rows = validator.get_validation_report_rows()

        # 2. Export Tabular Entities to CSV
        entity_tables = [
            ("customers", dataset.get("customers", [])),
            ("products", dataset.get("products", [])),
            ("consents", dataset.get("consents", [])),
            ("sessions", dataset.get("sessions", [])),
            ("carts", dataset.get("carts", [])),
            ("cart_lines", dataset.get("cart_lines", [])),
            ("campaigns", dataset.get("campaigns", [])),
            ("message_templates", dataset.get("message_templates", [])),
            ("send_attempts", dataset.get("send_attempts", [])),
            ("communication_events", dataset.get("communication_events", [])),
            ("orders", dataset.get("orders", [])),
            ("order_lines", dataset.get("order_lines", [])),
            ("attributions", dataset.get("attributions", [])),
            ("ground_truth", dataset.get("ground_truth", [])),
        ]

        for name, records in entity_tables:
            self._export_records_csv(name, records)

        # 3. Export Ground Truth JSON
        gt_path = os.path.join(self.export_dir, "ground_truth.json")
        with open(gt_path, "w", encoding="utf-8") as f:
            json.dump(dataset.get("ground_truth", []), f, indent=2, default=str)

        # 4. Export Validation Summary JSON & Validation Report CSV
        val_summary_path = os.path.join(self.export_dir, "validation_summary.json")
        with open(val_summary_path, "w", encoding="utf-8") as f:
            json.dump(val_summary, f, indent=2)

        val_report_path = os.path.join(self.export_dir, "validation_report.csv")
        pd.DataFrame(val_report_rows).to_csv(val_report_path, index=False)

        # 5. Export SQL Seed Script
        self._export_sql_seed(dataset, scale=scale, seed=seed)

        # 6. Generate Provenance Manifest
        manifest = ManifestGenerator.generate_manifest(
            export_dir=self.export_dir,
            scale=scale,
            seed=seed
        )
        manifest_path = os.path.join(self.export_dir, "source_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest

    def _export_records_csv(self, table_name: str, records: List[Dict[str, Any]]):
        if not records:
            return
        filepath = os.path.join(self.export_dir, f"{table_name}.csv")
        df = pd.DataFrame(records)
        # Format datetimes in ISO format for determinism
        for col in df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns:
            df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
        df.to_csv(filepath, index=False)

    def _export_sql_seed(self, dataset: Dict[str, Any], scale: str = "starter", seed: int = 20261022):
        from app.exports.sql_exporter import write_sql_seed_file

        seed_path = os.path.join(self.export_dir, "seed.sql")
        if scale == "starter":
            write_sql_seed_file(dataset, seed_path, scale="starter", seed=seed)
        else:
            # Full scale: export full SQL to seed_full.sql if explicitly requested via environment flag
            if os.getenv("EXPORT_FULL_SQL", "").lower() in ("1", "true", "yes"):
                full_path = os.path.join(self.export_dir, "seed_full.sql")
                write_sql_seed_file(dataset, full_path, scale="full", seed=seed)

            # Keep seed.sql deterministic and committed at starter scale (<5 MB, git-safe)
            from app.generator.synthetic_data_generator import SyntheticDataGenerator
            starter_gen = SyntheticDataGenerator(scale="starter", seed=seed)
            starter_data = starter_gen.generate_dataset()
            write_sql_seed_file(starter_data, seed_path, scale="starter", seed=seed)

