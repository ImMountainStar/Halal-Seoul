#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


INPUT_CSV = Path("data/materials_df_labeled_business_ready_v18.csv")
HOLD_CSV = Path("data/formula_hold_queue_v1.csv")
OUT_CSV = Path("data/operational_review_queue_v1.csv")

RULES = [
    ("제제/혼합", ("제제", "혼합", "베이스", "프리믹스"), "manual_formula_review", "carrier/부원료 확인"),
    ("조미/뉴클레오타이드", ("조미료", "핵산", "이노신산", "구아닐산", "뉴클레오티드"), "manufacturer_spec_review", "원료 출처 및 발효/생산 공정 확인"),
    ("향료/향미", ("향", "향료", "플레이버"), "manual_flavor_review", "carrier/solvent/alcohol 확인"),
    ("추출/농축", ("추출", "농축", "엑기스", "원액"), "manual_source_review", "추출용매 및 원료 출처 확인"),
    ("발효/배양", ("발효", "배양", "유산균", "균주"), "process_review", "배지, 효소, 잔류 알코올 확인"),
]


def classify(name: str) -> tuple[str, str, str]:
    for family, keywords, action, evidence in RULES:
        if any(keyword in name for keyword in keywords):
            return family, action, evidence
    return "기타 미해결 단품", "manual_ingredient_review", "단품 성분 정의 및 출처 확인"


def main() -> None:
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    hold = pd.read_csv(HOLD_CSV)
    hold_set = set(hold["material_name"].astype(str))

    excluded = df.get("excluded_flag")
    if excluded is None:
        excluded_mask = False
    else:
        excluded_mask = df["excluded_flag"].fillna(False)
    unresolved = df[df["resolved_status"].isna() & ~excluded_mask][["material_name"]].copy()
    unresolved = unresolved.drop_duplicates().sort_values("material_name").reset_index(drop=True)
    unresolved["queue_type"] = unresolved["material_name"].apply(
        lambda x: "hold_queue" if str(x) in hold_set else "review_queue"
    )

    classified = unresolved["material_name"].astype(str).apply(classify)
    unresolved["review_family"] = classified.apply(lambda x: x[0])
    unresolved["recommended_action"] = classified.apply(lambda x: x[1])
    unresolved["required_evidence"] = classified.apply(lambda x: x[2])

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    unresolved.to_csv(OUT_CSV, index=False)

    print(f"queue_rows={len(unresolved)}")
    print(unresolved["review_family"].value_counts().to_string())
    print(f"saved_queue={OUT_CSV}")


if __name__ == "__main__":
    main()
