#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v10.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v11.csv")
REVIEW_CSV = Path("data/materials_df_web_review_batch12.csv")

MUIS_SOURCE_TITLE = "MUIS HC Recognition Scheme Terms and Conditions (Annex A)"
MUIS_SOURCE_URL = "https://www.muis.gov.sg/-/media/files/officeofthemufti/irsyad/2017/fhcb/fhcb-terms-and-conditions"

SAFE_EXACT = {
    "염화칼슘",
    "염화칼슘(응고제)",
    "염화마그네슘",
    "염화마그네슘(고시형)",
    "염화마그네슘(응고제)",
    "염화칼륨",
    "염화칼륨(고시형)",
    "수산화칼슘",
    "수산화마그네슘",
    "수산화마그네슘(고시형)",
    "수산화칼륨",
    "산화칼슘",
    "산화칼슘(고시형)",
    "산화마그네슘",
    "산화마그네슘(고시형)",
    "요오드산칼륨",
    "요오드칼륨",
    "요오드칼륨(고시형)",
    "셀렌산나트륨",
    "아셀렌산나트륨",
    "인산칼슘",
    "제3인산칼슘",
    "제3인산칼슘(식첨가-211)",
    "제삼인산칼슘",
    "제삼인산칼슘(고시형)",
    "제이인산칼슘",
    "제이인산칼슘(고시형)",
    "제일인산칼슘",
    "제일인산칼슘(고시형)",
    "제이인산암모늄",
    "제일인산암모늄",
    "인산철",
    "인산철(고시형)",
}


def review_row(name: str) -> tuple[str | None, str | None, str | None, str | None]:
    if name in SAFE_EXACT:
        return (
            "할랄",
            "MUIS Annex A에서 synthetic chemicals와 일반 food additives를 low~medium-low risk로 본다. 단품 무기염/무기 첨가물 성격이 명확해 할랄로 추론",
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
    reviewed["batch12_status"] = pd.Series(statuses, dtype="string")
    reviewed["batch12_note"] = pd.Series(notes, dtype="string")
    reviewed["batch12_source_title"] = pd.Series(source_titles, dtype="string")
    reviewed["batch12_source_url"] = pd.Series(urls, dtype="string")

    apply_mask = reviewed["batch12_status"].notna()
    reviewed.loc[apply_mask, "resolved_status"] = reviewed.loc[apply_mask, "batch12_status"]
    reviewed.loc[apply_mask, "resolved_reason"] = reviewed.loc[apply_mask, "batch12_note"]

    review_only = reviewed[apply_mask].copy()
    reviewed.to_csv(OUT_CSV, index=False)
    review_only.to_csv(REVIEW_CSV, index=False)

    print(f"batch12_applied={int(apply_mask.sum())}")
    print(review_only["batch12_status"].value_counts(dropna=False).to_string())
    print(f"saved_review={REVIEW_CSV}")
    print(f"saved_final={OUT_CSV}")


if __name__ == "__main__":
    main()
