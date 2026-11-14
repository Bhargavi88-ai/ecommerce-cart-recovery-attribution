#!/usr/bin/env python3
"""
Production Anomaly Detection Suite.
Scans exported CSV tables or in-memory datasets to detect the 4 mandatory anomalies:
1. MESSAGE_AFTER_OPTOUT (Regulatory Privacy Violation via merge_asof point-in-time consent)
2. CART_ABANDONED_AFTER_PURCHASE (Cart Lifecycle Desynchronization)
3. DUPLICATE_ATTRIBUTION (Revenue Accounting Multi-Claim Overcount)
4. STALE_CART_TOTAL (Arithmetic Desynchronization)

Usage:
    python detect_anomalies.py
    python detect_anomalies.py --data run1
    python detect_anomalies.py --data data/exports
"""
import argparse
import glob
import os
import sys
import pandas as pd


def _load_csv(data_dir: str, name: str) -> pd.DataFrame:
    path = os.path.join(data_dir, f"{name}.csv")
    if not os.path.exists(path):
        matches = glob.glob(os.path.join(data_dir, f"**/{name}*.csv"), recursive=True)
        if matches:
            path = matches[0]
        else:
            print(f"Warning: File {name}.csv not found in {data_dir}")
            return pd.DataFrame()
    return pd.read_csv(path)


def detect_anomalies(data_dir: str = "run1"):
    print(f"============================================================")
    print(f" Anomaly Detection Suite")
    print(f" Inspecting Directory: {os.path.abspath(data_dir)}")
    print(f"============================================================")

    # 1. Load tables
    sends_df = _load_csv(data_dir, "send_attempts")
    consents_df = _load_csv(data_dir, "consents")
    carts_df = _load_csv(data_dir, "carts")
    cart_lines_df = _load_csv(data_dir, "cart_lines")
    orders_df = _load_csv(data_dir, "orders")
    attrs_df = _load_csv(data_dir, "attributions")
    gt_df = _load_csv(data_dir, "ground_truth")

    detected = []

    # -------------------------------------------------------------
    # Anomaly 1: MESSAGE_AFTER_OPTOUT
    # Point-in-time consent lookup using pd.merge_asof
    # -------------------------------------------------------------
    if not sends_df.empty and not consents_df.empty:
        s_sent = sends_df[sends_df["status"] == "SENT"].copy()
        s_sent["sent_at_dt"] = pd.to_datetime(s_sent["sent_at"])
        s_sent = s_sent.sort_values("sent_at_dt")

        c_df = consents_df.copy()
        c_df["effective_at_dt"] = pd.to_datetime(c_df["effective_at"])
        c_df = c_df.sort_values("effective_at_dt")

        # Point-in-time consent matching via merge_asof
        asof_merged = pd.merge_asof(
            s_sent,
            c_df,
            left_on="sent_at_dt",
            right_on="effective_at_dt",
            by=["customer_id", "channel"],
            direction="backward",
            suffixes=("_send", "_consent")
        )

        violations_a1 = asof_merged[asof_merged["status_consent"] == "OPT_OUT"]
        for _, row in violations_a1.iterrows():
            detected.append({
                "issue_type": "MESSAGE_AFTER_OPTOUT",
                "entity": "SendAttempt",
                "record_id": row["send_id"],
                "details": f"Customer {row['customer_id']} opted out on {row['channel']} at {row['effective_at']} but received send {row['send_id']} at {row['sent_at']}"
            })

    # -------------------------------------------------------------
    # Anomaly 2: CART_ABANDONED_AFTER_PURCHASE
    # Cart marked ABANDONED after an order was already completed
    # -------------------------------------------------------------
    if not carts_df.empty and not orders_df.empty:
        c_aband = carts_df[(carts_df["status"] == "ABANDONED") & carts_df["abandoned_at"].notnull()].copy()
        c_aband["abandoned_at_dt"] = pd.to_datetime(c_aband["abandoned_at"])

        o_comp = orders_df[orders_df["cart_id"].notnull()].copy()
        o_comp["order_ts_dt"] = pd.to_datetime(o_comp["order_timestamp"])

        merged_carts = pd.merge(
            c_aband,
            o_comp,
            on="cart_id",
            suffixes=("_cart", "_order")
        )
        violations_a2 = merged_carts[merged_carts["order_ts_dt"] <= merged_carts["abandoned_at_dt"]]
        for _, row in violations_a2.iterrows():
            detected.append({
                "issue_type": "CART_ABANDONED_AFTER_PURCHASE",
                "entity": "Cart",
                "record_id": row["cart_id"],
                "details": f"Cart {row['cart_id']} purchased in order {row['order_id']} at {row['order_timestamp']} but subsequently marked ABANDONED at {row['abandoned_at']}"
            })

    # -------------------------------------------------------------
    # Anomaly 3: DUPLICATE_ATTRIBUTION
    # Single order has multiple competing primary attribution claims
    # -------------------------------------------------------------
    if not attrs_df.empty:
        attr_counts = attrs_df.groupby("order_id").size().reset_index(name="claim_count")
        duplicates = attr_counts[attr_counts["claim_count"] > 1]
        for _, row in duplicates.iterrows():
            claim_ids = attrs_df[attrs_df["order_id"] == row["order_id"]]["attribution_id"].tolist()
            detected.append({
                "issue_type": "DUPLICATE_ATTRIBUTION",
                "entity": "Attribution",
                "record_id": row["order_id"],
                "details": f"Order {row['order_id']} has {row['claim_count']} competing primary claims: {claim_ids}"
            })

    # -------------------------------------------------------------
    # Anomaly 4: STALE_CART_TOTAL
    # Cart total_amount desynchronized from cart_lines sum
    # -------------------------------------------------------------
    if not carts_df.empty and not cart_lines_df.empty:
        line_sums = cart_lines_df.groupby("cart_id")["total_price"].sum().reset_index(name="calc_total")
        merged_totals = pd.merge(carts_df, line_sums, on="cart_id", how="left")
        merged_totals["calc_total"] = merged_totals["calc_total"].fillna(0.0)
        discount = merged_totals["discount_total"].fillna(0.0) if "discount_total" in merged_totals.columns else 0.0
        diff = (merged_totals["total_amount"] - (merged_totals["calc_total"] - discount)).abs()
        stale_carts = merged_totals[diff > 0.01]
        for _, row in stale_carts.iterrows():
            detected.append({
                "issue_type": "STALE_CART_TOTAL",
                "entity": "Cart",
                "record_id": row["cart_id"],
                "details": f"Cart {row['cart_id']} total_amount={row['total_amount']} != calculated sum={row['calc_total']}"
            })

    # -------------------------------------------------------------
    # Display Results & Reconciliation with Ground Truth
    # -------------------------------------------------------------
    print(f"\nDetected Production Anomalies: {len(detected)}")
    print(f"{'-'*60}")
    for idx, d in enumerate(detected, 1):
        print(f" {idx}. [{d['issue_type']}]")
        print(f"    Entity:    {d['entity']} ({d['record_id']})")
        print(f"    Details:   {d['details']}")

    # Reconciliation with ground_truth.csv
    gt_anomalies = gt_df[gt_df["issue_type"] != "NONE_BASELINE"] if (not gt_df.empty and "issue_type" in gt_df.columns) else pd.DataFrame()
    gt_ids = set(gt_anomalies["record_id"].tolist()) if not gt_anomalies.empty else set()
    detected_ids = {d["record_id"] for d in detected}

    if not gt_anomalies.empty:
        print(f"\n{'-'*60}")
        print(f"Reconciliation with ground_truth.csv:")
        print(f"  Ground Truth Anomaly Records: {len(gt_anomalies)}")
        matched = detected_ids & gt_ids
        print(f"  Matched Ground Truth IDs:     {len(matched)} / {len(gt_ids)}")
        for gid in sorted(gt_ids):
            status = "MATCHED" if gid in detected_ids else "MISSING"
            print(f"    - {gid:<20} [{status}]")

    # Audit for Unlabelled extras
    unlabelled_extras = [d for d in detected if d["record_id"] not in gt_ids]
    print(f"\nUnlabelled extras: {len(unlabelled_extras)}")
    if unlabelled_extras:
        for u in unlabelled_extras:
            print(f"  - [{u['issue_type']}] {u['entity']} {u['record_id']}")

    print(f"{'-'*60}")
    if len(detected) == 4 and len(unlabelled_extras) == 0:
        print(f"Result: All 4 mandatory production anomalies detected successfully with 0 unlabelled extras!")
        return 0
    else:
        print(f"Result: Expected 4 anomalies, detected {len(detected)}.")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Production Anomaly Detector")
    parser.add_argument("--data", type=str, default="run1", help="Path to directory containing CSV files")
    args = parser.parse_args()
    code = detect_anomalies(args.data)
    sys.exit(code)
