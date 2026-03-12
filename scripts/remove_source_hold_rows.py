#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v17.csv")
HOLD_CSV = Path("data/source_hold_queue_v1.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v18.csv")
REMOVED_CSV = Path("data/source_hold_removed_v1.csv")


def main() -> None:
    df = pd.read_csv(BASE_CSV, low_memory=False)
    hold = pd.read_csv(HOLD_CSV)

    hold_names = set(hold["material_name"].astype(str))
    remove_mask = df["material_name"].astype(str).isin(hold_names)

    removed = df.loc[remove_mask].copy()
    kept = df.loc[~remove_mask].copy()

    kept.to_csv(OUT_CSV, index=False)
    removed.to_csv(REMOVED_CSV, index=False)

    print(f"removed_rows={int(remove_mask.sum())}")
    print(f"saved_final={OUT_CSV}")
    print(f"saved_removed={REMOVED_CSV}")


if __name__ == "__main__":
    main()
