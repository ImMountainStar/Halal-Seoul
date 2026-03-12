#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v16.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v17.csv")
REVIEW_CSV = Path("data/materials_df_web_review_batch16.csv")

MUIS_SOURCE_TITLE = "MUIS HC Recognition Scheme Terms and Conditions (Annex A)"
MUIS_SOURCE_URL = "https://www.muis.gov.sg/-/media/files/officeofthemufti/irsyad/2017/fhcb/fhcb-terms-and-conditions"

SAFE_EXACT = {
    "결정셀룰로오스",
    "셀룰로오스",
    "메틸셀룰로오스",
    "메틸세룰로오스나트륨",
    "메칠세룰로오즈나트륨",
    "알긴산",
    "알긴산나트륨",
    "젖산",
    "젖산나트륨",
    "젖산칼륨",
    "젖산칼슘",
    "젖산칼슘(고시형)",
    "젖산마그네슘(고시형)",
    "아디프산",
    "에리토브산",
    "에리토브산나트륨",
}


def review_row(name: str) -> tuple[str | None, str | None, str | None, str | None]:
    if name in SAFE_EXACT:
        return (
            "할랄",
            "MUIS Annex A에서 synthetic chemicals와 일반 food additives를 low~medium-low risk로 본다. 단품 셀룰로오스/알긴산/유기산 첨가물 성격이 명확해 할랄로 추론",
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
    reviewed["batch16_status"] = pd.Series(statuses, dtype="string")
    reviewed["batch16_note"] = pd.Series(notes, dtype="string")
    reviewed["batch16_source_title"] = pd.Series(source_titles, dtype="string")
    reviewed["batch16_source_url"] = pd.Series(urls, dtype="string")

    apply_mask = reviewed["batch16_status"].notna()
    reviewed.loc[apply_mask, "resolved_status"] = reviewed.loc[apply_mask, "batch16_status"]
    reviewed.loc[apply_mask, "resolved_reason"] = reviewed.loc[apply_mask, "batch16_note"]

    review_only = reviewed[apply_mask].copy()
    reviewed.to_csv(OUT_CSV, index=False)
    review_only.to_csv(REVIEW_CSV, index=False)

    print(f"batch16_applied={int(apply_mask.sum())}")
    print(review_only["batch16_status"].value_counts(dropna=False).to_string())
    print(f"saved_review={REVIEW_CSV}")
    print(f"saved_final={OUT_CSV}")


if __name__ == "__main__":
    main()
