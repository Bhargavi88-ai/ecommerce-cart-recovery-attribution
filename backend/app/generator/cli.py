import argparse
import sys
import os
import json

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.config import settings
from app.generator.synthetic_data_generator import SyntheticDataGenerator
from app.exports.exporter import DatasetExporter
from app.database import SessionLocal, Base, engine
from app.generator.db_loader import populate_database_from_dataset


def main():
    parser = argparse.ArgumentParser(description="Synthetic Data Generator for Abandoned Cart Recovery System")
    parser.add_argument("--scale", type=str, default="starter", choices=["starter", "full"], help="Dataset scale: starter or full")
    parser.add_argument("--seed", type=int, default=20261022, help="Fixed random seed (default: 20261022)")
    parser.add_argument("--output-dir", type=str, default=settings.EXPORTS_DIR, help="Export directory path")
    parser.add_argument("--no-db", action="store_true", help="Skip populating the database")
    parser.add_argument("--reset-db", action="store_true", default=True, help="Reset database schema before loading")

    args = parser.parse_args()

    print(f"============================================================")
    print(f" E-Commerce Cart Recovery Synthetic Data Generator")
    print(f" Scale: {args.scale.upper()} | Seed: {args.seed}")
    print(f" Output Directory: {os.path.abspath(args.output_dir)}")
    print(f"============================================================")

    # 1. Run Generator
    print("[1/4] Generating dependency-ordered synthetic records...")
    generator = SyntheticDataGenerator(seed=args.seed, scale=args.scale)
    dataset = generator.generate_dataset()

    print(f"      - Customers: {len(dataset['customers']):,}")
    print(f"      - Products: {len(dataset['products']):,}")
    print(f"      - Carts: {len(dataset['carts']):,}")
    abandoned_count = len([c for c in dataset['carts'] if c['status'] in ('ABANDONED', 'ELIGIBLE', 'SUPPRESSED', 'CAMPAIGN_SCHEDULED')])
    print(f"      - Abandoned Carts: {abandoned_count:,}")
    print(f"      - Send Attempts: {len(dataset['send_attempts']):,}")
    print(f"      - Communication Events: {len(dataset['communication_events']):,}")
    print(f"      - Orders: {len(dataset['orders']):,}")
    print(f"      - Attributions: {len(dataset['attributions']):,}")
    print(f"      - Labelled Anomalies: {len(dataset['anomalies'])}")

    # 2. Export dataset files, reports, and manifests
    print("[2/4] Running automated validation and exporting data files...")
    exporter = DatasetExporter(export_dir=args.output_dir)
    manifest = exporter.export_all(dataset, scale=args.scale, seed=args.seed)
    print(f"      - Manifest created at: {os.path.join(args.output_dir, 'source_manifest.json')}")
    print(f"      - Exported files: {len(manifest['files'])}")

    # 3. Populate Database if requested
    if not args.no_db:
        print("[3/4] Populating relational database...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            populate_database_from_dataset(db, dataset)
            print("      - Relational database populated successfully!")
        except Exception as e:
            print(f"      - Error loading database: {e}")
            db.rollback()
        finally:
            db.close()
    else:
        print("[3/4] Database population skipped via --no-db.")

    print("[4/4] Generation completed successfully!")
    print(f"============================================================")


if __name__ == "__main__":
    main()
