#!/usr/bin/env python3
"""
Independent Frequency-Cap Auditor.
Audits send attempts independently from the generator and validator
to verify that no customer receives more than 3 messages per channel
within any rolling 7-day window [t - 7d, t].

Usage:
    python check_cap.py
    python check_cap.py --data run1
"""
import argparse
import glob
import os
import sys
import pandas as pd
from datetime import timedelta


def audit_frequency_cap(data_path: str = "run1"):
    # Look for send_attempts file
    if os.path.isfile(data_path):
        csv_file = data_path
    else:
        candidates = glob.glob(os.path.join(data_path, "**/send_attempts*.csv"), recursive=True)
        if not candidates:
            candidates = glob.glob(os.path.join(data_path, "send_attempts*.csv"))
        if not candidates:
            candidates = glob.glob("run1/**/send_attempts*.csv", recursive=True)
        if not candidates:
            candidates = glob.glob("data/exports/send_attempts*.csv")
        if not candidates:
            print(f"Error: No send_attempts*.csv found in '{data_path}'")
            sys.exit(1)
        csv_file = candidates[0]

    print(f"Auditing frequency cap from: {csv_file}")
    df = pd.read_csv(csv_file)

    # Filter to successfully SENT attempts
    sent_df = df[(df["status"] == "SENT") & df["sent_at"].notnull()].copy()
    sent_df["sent_at"] = pd.to_datetime(sent_df["sent_at"])

    over_cap_records = []

    # Group by customer and channel
    for (cust_id, channel), group in sent_df.groupby(["customer_id", "channel"]):
        timestamps = sorted(group["sent_at"].tolist())
        for idx, t1 in enumerate(timestamps):
            # Rolling 7-day window [t1, t1 + 7 days]
            window_end = t1 + timedelta(days=7)
            sends_in_window = sum(1 for t2 in timestamps[idx:] if t1 <= t2 <= window_end)
            if sends_in_window > 3:
                over_cap_records.append({
                    "customer_id": cust_id,
                    "channel": channel,
                    "first_send": t1,
                    "sends_count": sends_in_window
                })

    print(f"Total sent attempts checked: {len(sent_df)}")
    print(f"customers over cap: {len(over_cap_records)}")

    if len(over_cap_records) > 0:
        for r in over_cap_records[:5]:
            print(f"  Violation: {r['customer_id']} on {r['channel']}: {r['sends_count']} sends starting at {r['first_send']}")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Independent Frequency-Cap Auditor")
    parser.add_argument("--data", type=str, default="run1", help="Path to data directory or send_attempts.csv")
    args = parser.parse_args()
    audit_frequency_cap(args.data)
