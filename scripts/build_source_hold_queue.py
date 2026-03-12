#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


INPUT_CSV = Path("data/materials_df_labeled_business_ready_v8.csv")
OUT_CSV = Path("data/source_hold_queue_v1.csv")

NUCLEOTIDE_PATTERNS = (
    "이노신산",
    "구아닐산",
    "아데닐산",
    "시티딜산",
    "핵산",
)


def main() -> None:
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    unresolved = df[df["resolved_status"].isna()].copy()
    names = unresolved["material_name"].fillna("").astype(str)

    nucleotide_mask = names.apply(lambda x: any(p in x for p in NUCLEOTIDE_PATTERNS))
    hold = unresolved.loc[nucleotide_mask, ["material_name"]].copy()
    hold = hold.drop_duplicates().sort_values("material_name").reset_index(drop=True)
    hold["hold_family"] = "핵산계 조미성분/뉴클레오타이드"
    hold["hold_reason"] = "현재 확보한 1차 출처만으로 일괄 halal/mashbooh 판정 근거 부족"
    hold["required_evidence"] = "제조사 스펙시트, 원료 출처, 발효/생산 공정, carrier/혼합 여부"
    hold["recommended_action"] = "manufacturer_spec_review"

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    hold.to_csv(OUT_CSV, index=False)

    print(f"hold_rows={len(hold)}")
    print(f"saved_hold_queue={OUT_CSV}")


if __name__ == "__main__":
    main()
