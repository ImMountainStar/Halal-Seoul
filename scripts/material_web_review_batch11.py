#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v9.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v10.csv")
REVIEW_CSV = Path("data/materials_df_web_review_batch11.csv")

MUIS_SOURCE_TITLE = "MUIS HC Recognition Scheme Terms and Conditions (Annex A)"
MUIS_SOURCE_URL = "https://www.muis.gov.sg/-/media/files/officeofthemufti/irsyad/2017/fhcb/fhcb-terms-and-conditions"

SAFE_EXACT = {
    "소르빈산",
    "소르빈산나트륨",
    "소르빈산칼륨",
    "소르빈산칼슘",
    "소르빈칼륨",
    "소브산",
    "소브산칼륨",
    "소브산칼슘",
    "솔빈산",
    "솔빈산나트륨",
    "소로빈산칼륨",
    "소르반산칼륨",
    "아세설파칼륨",
    "아세설팜칼륨",
    "아세셀팜칼륨",
}


def review_row(name: str) -> tuple[str | None, str | None, str | None, str | None]:
    if name in SAFE_EXACT:
        return (
            "할랄",
            "MUIS Annex A에서 synthetic chemicals와 일반 food additives를 low~medium-low risk로 본다. 단품 보존제/합성 감미료 성격이 명확해 할랄로 추론",
            MUIS_SOURCE_TITLE,
            MUIS_SOURCE_URL,
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
    reviewed["batch11_status"] = pd.Series(statuses, dtype="string")
    reviewed["batch11_note"] = pd.Series(notes, dtype="string")
    reviewed["batch11_source_title"] = pd.Series(source_titles, dtype="string")
    reviewed["batch11_source_url"] = pd.Series(urls, dtype="string")

    apply_mask = reviewed["batch11_status"].notna()
    reviewed.loc[apply_mask, "resolved_status"] = reviewed.loc[apply_mask, "batch11_status"]
    reviewed.loc[apply_mask, "resolved_reason"] = reviewed.loc[apply_mask, "batch11_note"]

    review_only = reviewed[apply_mask].copy()
    reviewed.to_csv(OUT_CSV, index=False)
    review_only.to_csv(REVIEW_CSV, index=False)

    print(f"batch11_applied={int(apply_mask.sum())}")
    print(review_only["batch11_status"].value_counts(dropna=False).to_string())
    print(f"saved_review={REVIEW_CSV}")
    print(f"saved_final={OUT_CSV}")


if __name__ == "__main__":
    main()
