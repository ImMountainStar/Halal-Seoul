#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v11.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v12.csv")
REVIEW_CSV = Path("data/materials_df_web_review_batch13.csv")

IFANCA_SOURCE_TITLE = "IFANCA Salt"
IFANCA_SOURCE_URL = "https://ifanca.org/resources/salt/"

SAFE_EXACT = {
    "1회구운소금",
    "3회구운죽염",
    "9회구운죽염",
    "9회자죽염",
    "9회죽염",
    "가는소금",
    "간수뺀천일염",
    "구운소금",
    "구운죽염",
    "구은소금",
    "기타소금",
    "꽃소금",
    "미네랄소금",
    "물죽염",
    "산인죽염",
    "서해안천일염",
    "식염",
    "식염1",
    "식염2",
    "신안비금도천일염",
    "신안천일염",
    "알카리소금",
    "용융소금",
    "자죽염",
    "재재소금",
    "재제소금(재제조소금)",
    "재제식염",
    "저제소금",
    "정제소금",
    "정제식염",
    "정제염",
    "제재소금",
    "제제소금",
    "죽염",
    "죽염1",
    "천일염",
    "천일염소금",
    "토소금",
    "한주소금",
    "해양심층수소금",
    "황토소금",
}


def review_row(name: str) -> tuple[str | None, str | None, str | None, str | None]:
    if name in SAFE_EXACT:
        return (
            "할랄",
            "IFANCA Salt 자료는 salt를 sodium chloride 기반 mineral로 설명한다. 성분명 자체가 단품 소금/염 계열이므로 할랄로 분류",
            IFANCA_SOURCE_TITLE,
            IFANCA_SOURCE_URL,
        )

    return (None, None, None, None)


def main() -> None:
    df = pd.read_csv(BASE_CSV, low_memory=False)

    statuses: list[str | None] = []
    notes: list[str | None] = []
    source_titles: list[str | None] = []
    urls: list[str | None] = []

    for _, row in df.iterrows():
        if pd.notna(row.get("resolved_status")):
            statuses.append(None)
            notes.append(None)
            source_titles.append(None)
            urls.append(None)
            continue

        status, note, source_title, url = review_row(str(row.get("material_name", "")).strip())
        statuses.append(status)
        notes.append(note)
        source_titles.append(source_title)
        urls.append(url)

    reviewed = df.copy()
    reviewed["batch13_status"] = pd.Series(statuses, dtype="string")
    reviewed["batch13_note"] = pd.Series(notes, dtype="string")
    reviewed["batch13_source_title"] = pd.Series(source_titles, dtype="string")
    reviewed["batch13_source_url"] = pd.Series(urls, dtype="string")

    apply_mask = reviewed["batch13_status"].notna()
    reviewed.loc[apply_mask, "resolved_status"] = reviewed.loc[apply_mask, "batch13_status"]
    reviewed.loc[apply_mask, "resolved_reason"] = reviewed.loc[apply_mask, "batch13_note"]

    review_only = reviewed[apply_mask].copy()
    reviewed.to_csv(OUT_CSV, index=False)
    review_only.to_csv(REVIEW_CSV, index=False)

    print(f"batch13_applied={int(apply_mask.sum())}")
    print(review_only["batch13_status"].value_counts(dropna=False).to_string())
    print(f"saved_review={REVIEW_CSV}")
    print(f"saved_final={OUT_CSV}")


if __name__ == "__main__":
    main()
