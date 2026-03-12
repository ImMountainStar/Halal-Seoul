#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v2.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v3.csv")
REVIEW_CSV = Path("data/materials_df_web_review_batch4.csv")

IFANCA_FERMENT_URL = "https://ifanca.org/resources/fermenting-foods-for-future-fare/"
MUIS_RISK_URL = "https://www.muis.gov.sg/-/media/files/officeofthemufti/irsyad/2017/fhcb/fhcb-terms-and-conditions"

FERMENTATION_KEYWORDS = (
    "발효",
)

CULTURE_KEYWORDS = (
    "유산균",
    "균주",
    "배양",
)

SAFE_HALAL_EXACT = {
    "결정구연산",
    "구연산",
    "구연산(결정)",
    "구연산(무수)",
    "구연산(함수)",
    "구연산나트륨",
    "구연산삼나트륨",
    "구연산소다",
    "구연산칼륨",
    "구연산칼륨(고시형)",
    "구연산칼슘",
    "구연산칼슘(고시형)",
    "무수구연산",
    "무수구연산분말",
    "무수구연산소다",
    "글루콘산",
    "글루콘산나트륨",
    "글루콘산마그네슘",
    "글루콘산마그네슘(고시형)",
    "글루콘산아연",
    "글루콘산아연(고시형)",
    "글루콘산철",
    "글루콘산철(고시형)",
    "글루콘산칼륨",
    "글루콘산칼슘",
    "규산칼슘",
    "중탄산암모늄(팽창제)",
}


def contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def review_row(name: str) -> tuple[str | None, str | None, str | None, str | None]:
    if name in SAFE_HALAL_EXACT:
        return (
            "할랄",
            "MUIS FHCB 기준에서 synthetic chemicals와 일반 food additives는 low~medium-low risk로 분류된다. 성분명이 비동물성 산류/염류 첨가물로 명확해 할랄로 추론",
            "MUIS FHCB Terms and Conditions",
            MUIS_RISK_URL,
        )

    if contains_any(name, CULTURE_KEYWORDS):
        return (
            "마슈부",
            "IFANCA는 발효식품에 대해 starter culture, 배지, 효소, 부산물 검토가 필요하다고 설명한다. 배양/유산균 원료는 공정 정보 없이는 확정할 수 없어 마슈부로 분류",
            "IFANCA Fermenting Foods for Future Fare",
            IFANCA_FERMENT_URL,
        )

    if contains_any(name, FERMENTATION_KEYWORDS):
        return (
            "마슈부",
            "IFANCA는 fermentation에서 culture, enzyme, residual alcohol 검토가 필요하다고 설명한다. 발효 추출물/발효액은 원료와 공정 정보 없이는 확정할 수 없어 마슈부로 분류",
            "IFANCA Fermenting Foods for Future Fare",
            IFANCA_FERMENT_URL,
        )

    return (None, None, None, None)


def main() -> None:
    df = pd.read_csv(BASE_CSV)

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
    reviewed["batch4_status"] = pd.Series(statuses, dtype="string")
    reviewed["batch4_note"] = pd.Series(notes, dtype="string")
    reviewed["batch4_source_title"] = pd.Series(source_titles, dtype="string")
    reviewed["batch4_source_url"] = pd.Series(urls, dtype="string")

    apply_mask = reviewed["batch4_status"].notna()
    reviewed.loc[apply_mask, "resolved_status"] = reviewed.loc[apply_mask, "batch4_status"]
    reviewed.loc[apply_mask, "resolved_reason"] = reviewed.loc[apply_mask, "batch4_note"]

    review_only = reviewed[apply_mask].copy()

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    reviewed.to_csv(OUT_CSV, index=False)
    review_only.to_csv(REVIEW_CSV, index=False)

    print(f"batch4_applied={int(apply_mask.sum())}")
    print(review_only["batch4_status"].value_counts(dropna=False).to_string())
    print(f"saved_review={REVIEW_CSV}")
    print(f"saved_final={OUT_CSV}")


if __name__ == "__main__":
    main()
