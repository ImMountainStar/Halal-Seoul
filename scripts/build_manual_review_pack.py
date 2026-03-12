#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


FINAL_CSV = Path("data/materials_df_labeled_business_ready_v2.csv")
OUT_CSV = Path("data/manual_review_pack_v1.csv")
OUT_MD = Path("docs/manual_review_pack_v1.md")

FAMILIES = [
    (
        "산류/염류",
        r"(?:산$|산나트륨|산칼륨|산칼슘|산암모늄)",
        "원료 기원과 제조공정 확인",
        "공정 확인 전 자동 확정 금지",
        "P1",
    ),
    (
        "향미 화합물",
        r"(?:피라진|피롤|피리딘|티아졸|푸란|아세테이트|에스터|에시드|알데하이드|케톤|논|올$)",
        "합성/용매/기원 확인",
        "flavor carrier, solvent, alcohol 포함 여부 확인",
        "P2",
    ),
    (
        "미생물/유산균/배양",
        r"(?:유산균|균주|배양)",
        "배지 및 배양공정 확인",
        "배지 성분에 비할랄 유래물 포함 여부 확인",
        "P1",
    ),
    (
        "발효산물",
        r"(?:발효)",
        "발효 원료와 공정 확인",
        "알코올 생성/잔류 여부와 원료 출처 확인",
        "P1",
    ),
]


def main() -> None:
    final = pd.read_csv(FINAL_CSV)
    unlabeled = final[final["resolved_status"].isna()].copy()
    names = unlabeled["material_name"].fillna("").astype(str)

    packs: list[pd.DataFrame] = []
    md_lines = [
        "# Manual Review Pack v1",
        "",
        "Last updated: 2026-03-08",
        "",
        "This pack contains unresolved ingredient families that should not be auto-labeled without manual source/process review.",
        "",
    ]

    for family, pattern, review_focus, caution, priority_tier in FAMILIES:
        mask = names.str.contains(pattern, regex=True)
        subset = unlabeled.loc[mask, ["material_name"]].copy()
        subset = subset.drop_duplicates().sort_values("material_name")
        subset["review_family"] = family
        subset["review_focus"] = review_focus
        subset["caution"] = caution
        subset["priority_tier"] = priority_tier
        subset["recommended_action"] = "manual_web_review"
        packs.append(subset)

        md_lines.append(f"## {family}")
        md_lines.append("")
        md_lines.append(f"- Priority: {priority_tier}")
        md_lines.append(f"- Count: {len(subset)}")
        md_lines.append(f"- Review focus: {review_focus}")
        md_lines.append(f"- Caution: {caution}")
        md_lines.append("- Sample:")
        for sample in subset["material_name"].head(15).tolist():
            md_lines.append(f"  - {sample}")
        md_lines.append("")

    pack = pd.concat(packs, ignore_index=True).drop_duplicates(subset=["material_name"])
    pack = pack.sort_values(["priority_tier", "review_family", "material_name"]).reset_index(drop=True)
    pack.to_csv(OUT_CSV, index=False)
    OUT_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"pack_rows={len(pack)}")
    print(f"saved_csv={OUT_CSV}")
    print(f"saved_md={OUT_MD}")


if __name__ == "__main__":
    main()
