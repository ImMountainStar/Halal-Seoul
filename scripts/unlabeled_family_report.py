#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


FINAL_CSV = Path("data/materials_df_labeled_business_ready_v1.csv")
REPORT_MD = Path("docs/unlabeled_family_report_v1.md")

FAMILY_PATTERNS = {
    "당류/전분/덱스트린": r"(과당|포도당|말토덱스트린|전분|시럽|당|덱스트린)",
    "식초/발효산물": r"(식초|발효)",
    "산류/염류": r"(산$|산나트륨|산칼륨|산칼슘|산암모늄)",
    "향미 화합물": r"(피라진|피롤|피리딘|티아졸|푸란|아세테이트|에스터|에시드|알데하이드|케톤|논|올$)",
    "미생물/유산균": r"(유산균|균주|배양)",
}


def main() -> None:
    final = pd.read_csv(FINAL_CSV)
    unlabeled = final[final["resolved_status"].isna()].copy()
    names = unlabeled["material_name"].fillna("").astype(str)

    lines = [
        "# Unlabeled Family Report v1",
        "",
        "Last updated: 2026-03-08",
        "",
        f"- Unlabeled rows: {len(unlabeled)}",
        "",
        "## Family Counts",
        "",
    ]

    for family, pattern in FAMILY_PATTERNS.items():
        mask = names.str.contains(pattern, regex=True)
        count = int(mask.sum())
        lines.append(f"- {family}: {count}")
        sample = unlabeled.loc[mask, "material_name"].head(15).tolist()
        if sample:
            lines.append(f"  sample: {', '.join(sample)}")

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"saved_report={REPORT_MD}")


if __name__ == "__main__":
    main()
