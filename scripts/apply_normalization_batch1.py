#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v12.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v13.csv")
REVIEW_CSV = Path("data/normalization_applied_batch1.csv")

SAFE_NORMALIZATIONS = {
    "글세린지방산에스테르": "글리세린지방산에스테르",
    "글레세린지방산에스테르": "글리세린지방산에스테르",
    "산성피로인산트륨": "산성피로인산나트륨",
    "글루산나트륨": "글루콘산나트륨",
    "무수결정포당": "무수결정포도당",
    "함수결정포당": "함수결정포도당",
    "2-메틸부틸아세티이트": "2-메틸부틸아세테이트",
    "시스-3-헥세닐아세티이트": "시스-3-헥세닐아세테이트",
}


def main() -> None:
    df = pd.read_csv(BASE_CSV, low_memory=False)
    canon = df.set_index("material_name")

    applied_rows = []
    for raw_name, canonical_name in SAFE_NORMALIZATIONS.items():
        raw_mask = df["material_name"].eq(raw_name) & df["resolved_status"].isna()
        if not raw_mask.any():
            continue
        if canonical_name not in canon.index:
            continue
        source = canon.loc[canonical_name]
        if pd.isna(source["resolved_status"]):
            continue

        df.loc[raw_mask, "resolved_status"] = source["resolved_status"]
        df.loc[raw_mask, "resolved_reason"] = (
            f"정규화 매핑 적용: {raw_name} -> {canonical_name}; canonical reviewed decision reused"
        )
        df.loc[raw_mask, "normalization_source_name"] = canonical_name

        applied_rows.append(
            {
                "raw_name": raw_name,
                "canonical_name": canonical_name,
                "applied_status": source["resolved_status"],
            }
        )

    applied = pd.DataFrame(applied_rows)
    df.to_csv(OUT_CSV, index=False)
    applied.to_csv(REVIEW_CSV, index=False)

    print(f"normalization_applied={len(applied)}")
    print(f"saved_review={REVIEW_CSV}")
    print(f"saved_final={OUT_CSV}")


if __name__ == "__main__":
    main()
