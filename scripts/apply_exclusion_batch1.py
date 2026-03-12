#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v13.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v14.csv")
REVIEW_CSV = Path("data/exclusion_applied_batch1.csv")

EXCLUDE_EXACT = {
    "1-하이드록시에틸리덴-1",
    "2-메톡시-3",
    "2-에틸",
    "4-트리메틸",
    "5-리보뉴",
    "5-리보뉴클레오",
    "5-메틸-2",
    "가-164",
    "가-25",
    "가-26",
    "나-102",
    "나-157",
    "나-40",
    "리보",
    "메틸",
    "에틸",
    "이드",
}


def main() -> None:
    df = pd.read_csv(BASE_CSV, low_memory=False)

    mask = df["material_name"].astype(str).isin(EXCLUDE_EXACT) & df["resolved_status"].isna()
    df["excluded_flag"] = False
    df["excluded_reason"] = pd.NA

    df.loc[mask, "excluded_flag"] = True
    df.loc[mask, "excluded_reason"] = "추적 불가 코드/잘린 문자열/의미 불명 파편값으로 판단되어 운영 검수 큐에서 제외"

    review = df.loc[mask, ["material_name", "excluded_reason"]].copy()

    df.to_csv(OUT_CSV, index=False)
    review.to_csv(REVIEW_CSV, index=False)

    print(f"excluded_rows={int(mask.sum())}")
    print(f"saved_review={REVIEW_CSV}")
    print(f"saved_final={OUT_CSV}")


if __name__ == "__main__":
    main()
