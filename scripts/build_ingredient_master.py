#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


FINAL_CSV = Path("data/materials_df_labeled_business_ready_v18.csv")
KOR_UNIQUE_CSV = Path("data/unique_materials_kor.csv")
MASTER_CSV = Path("data/ingredient_master_v18.csv")
KOR_BACKFILLED_CSV = Path("data/unique_materials_kor_backfilled_v18.csv")


def main() -> None:
    final = pd.read_csv(FINAL_CSV, low_memory=False)
    kor = pd.read_csv(KOR_UNIQUE_CSV)

    existing_master = None
    if MASTER_CSV.exists():
        existing_master = pd.read_csv(MASTER_CSV, low_memory=False)
        if "canonical_name" in existing_master.columns:
            existing_master = existing_master[
                [col for col in ("canonical_name", "primary_source_url", "primary_source_title") if col in existing_master.columns]
            ].drop_duplicates(subset=["canonical_name"])

    master = final[final["resolved_status"].notna()].copy()
    keep_cols = [
        "material_name",
        "resolved_status",
        "resolved_reason",
        "review_action",
        "review_confidence",
    ]
    master = master[keep_cols].rename(
        columns={
            "material_name": "canonical_name",
            "resolved_status": "final_status",
            "resolved_reason": "final_reason",
        }
    )
    master = master.drop_duplicates(subset=["canonical_name"]).sort_values("canonical_name")

    if existing_master is not None:
        master = master.merge(existing_master, on="canonical_name", how="left")
    else:
        master["primary_source_url"] = pd.NA
        master["primary_source_title"] = pd.NA

    backfilled = kor.merge(
        master,
        left_on="normalized_name",
        right_on="canonical_name",
        how="left",
    )

    MASTER_CSV.parent.mkdir(parents=True, exist_ok=True)
    master.to_csv(MASTER_CSV, index=False)
    backfilled.to_csv(KOR_BACKFILLED_CSV, index=False)

    print(f"master_rows={len(master)}")
    print(f"kor_backfilled_rows={int(backfilled['final_status'].notna().sum())}")
    print(f"saved_master={MASTER_CSV}")
    print(f"saved_backfilled={KOR_BACKFILLED_CSV}")


if __name__ == "__main__":
    main()
