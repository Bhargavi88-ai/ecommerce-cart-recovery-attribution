#!/usr/bin/env python3
"""
CLI Synthetic Data Generator Wrapper.
Usage:
    python generate.py --seed 20261022 --out run1
    python generate.py --scale full --seed 20261022 --out run1
"""
import argparse
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.generator.synthetic_data_generator import SyntheticDataGenerator
from app.exports.exporter import DatasetExporter


def main():
    parser = argparse.ArgumentParser(description="Synthetic Data Generator")
    parser.add_argument("--scale", type=str, default="full", choices=["starter", "full"], help="Scale (starter, full)")
    parser.add_argument("--seed", type=int, default=20261022, help="Deterministic random seed")
    parser.add_argument("--out", type=str, default="data/exports", help="Output directory path")

    args = parser.parse_args()

    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    print(f"============================================================")
    print(f" Synthetic Data Generator")
    print(f" Scale: {args.scale.upper()} | Seed: {args.seed}")
    print(f" Output Directory: {out_dir}")
    print(f"============================================================")

    gen = SyntheticDataGenerator(scale=args.scale, seed=args.seed)
    print("[1/3] Generating dependency-ordered synthetic records...")
    dataset = gen.generate_dataset()

    print("[2/3] Exporting files and generating manifest...")
    exporter = DatasetExporter(export_dir=out_dir)
    manifest = exporter.export_all(dataset, scale=args.scale, seed=args.seed)

    print(f"[3/3] Successfully generated and exported {len(manifest.get('files', {}))} files to {out_dir}!")
    print(f"============================================================")


if __name__ == "__main__":
    main()

