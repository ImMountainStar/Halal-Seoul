#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v3.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v4.csv")
REVIEW_CSV = Path("data/materials_df_web_review_batch5.csv")

MUIS_SOURCE_TITLE = "MUIS HC Recognition Scheme Terms and Conditions (Annex A)"
MUIS_SOURCE_URL = "https://www.muis.gov.sg/-/media/files/officeofthemufti/irsyad/2017/fhcb/fhcb-terms-and-conditions"

SAFE_ADDITIVE_EXACT = {
    "데히드로초산나트륨",
    "메타중아황산나트륨",
    "메타중아황산칼륨",
    "무수아황산",
    "무수아황산나트륨",
    "산성아황산나트륨",
    "아황산",
    "아황산나트륨",
    "아황산나트륨(표백제)",
    "차아황산나트륨",
    "차아황산나트륨(표백제)",
    "표백제(차아황산나트륨)",
    "메타인산나트륨",
    "메타인산칼륨",
    "메티인산나트륨",
    "복합인산나트륨",
    "복합인산염",
    "산도조절제폴리인산나트륨",
    "산성인산나트륨",
    "산성피로인산나트륨",
    "인산나트륨",
    "제1인산나트륨(무수)",
    "제3인산나트륨",
    "제삼인산나트륨",
    "제이인산나트륨",
    "제일인산나트륨",
    "포리인산나트륨",
    "폴리인산나트륨",
    "폴리인산나트륨(식첨가-295)",
    "플리인산나트륨",
    "피로인산나트륨",
    "피로인산나트륨(무수)",
    "재2인산칼륨",
    "제2인산칼륨",
    "제삼인산칼륨",
    "제이인산칼륨",
    "제이인산칼륨(고시형)",
    "제일인산칼륨",
    "제일인산칼륨(고시형)",
    "폴리인산칼륨",
    "풀리인산칼륨",
    "피로인산칼륨",
}


def review_row(name: str) -> tuple[str | None, str | None, str | None, str | None]:
    if name in SAFE_ADDITIVE_EXACT:
        return (
            "할랄",
            "MUIS Annex A에서 food additives(excl E400s)와 synthetic chemicals를 low~medium-low risk로 본다. 명칭이 명확한 무기염/보존제/인산염 첨가물이라 할랄로 추론",
            MUIS_SOURCE_TITLE,
            MUIS_SOURCE_URL,
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
    reviewed["batch5_status"] = pd.Series(statuses, dtype="string")
    reviewed["batch5_note"] = pd.Series(notes, dtype="string")
    reviewed["batch5_source_title"] = pd.Series(source_titles, dtype="string")
    reviewed["batch5_source_url"] = pd.Series(urls, dtype="string")

    apply_mask = reviewed["batch5_status"].notna()
    reviewed.loc[apply_mask, "resolved_status"] = reviewed.loc[apply_mask, "batch5_status"]
    reviewed.loc[apply_mask, "resolved_reason"] = reviewed.loc[apply_mask, "batch5_note"]

    review_only = reviewed[apply_mask].copy()

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    reviewed.to_csv(OUT_CSV, index=False)
    review_only.to_csv(REVIEW_CSV, index=False)

    print(f"batch5_applied={int(apply_mask.sum())}")
    print(review_only["batch5_status"].value_counts(dropna=False).to_string())
    print(f"saved_review={REVIEW_CSV}")
    print(f"saved_final={OUT_CSV}")


if __name__ == "__main__":
    main()
