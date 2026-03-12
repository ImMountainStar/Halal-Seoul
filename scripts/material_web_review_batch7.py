#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v5.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v6.csv")
REVIEW_CSV = Path("data/materials_df_web_review_batch7.csv")

IFANCA_FATTY_TITLE = "IFANCA Shopper's Guide"
IFANCA_FATTY_URL = "https://ifanca.org/resources/shoppers-guide/"
IFANCA_AMINO_TITLE = "IFANCA Halal for Entrepreneurs"
IFANCA_AMINO_URL = "https://ifanca.org/resources/halal-for-entrepreneurs-your-key-to-new-markets/"

FATTY_KEYWORDS = (
    "스테아린산",
    "스테아레이트",
    "라우릭산",
    "라우린산",
    "미리스트산",
    "팔미트산",
)

FATTY_EXACT = {
    "라우릭산",
    "라우린산",
    "미리스트산",
    "스테아린산",
    "스테아린산마그네슘",
    "스테아린산마그네슘(고시형)",
    "스테아린산마그네슘1",
    "스테아린산칼슘",
    "팔미트산",
}

GLUTAMATE_EXACT = {
    "1-글루타민산나트륨",
    "구로타민산나트륨",
    "글루타만산나트륨",
    "루타민산나트륨",
    "엘글루타민산나트륨",
}


def review_row(name: str) -> tuple[str | None, str | None, str | None, str | None]:
    if name in FATTY_EXACT or any(keyword in name for keyword in FATTY_KEYWORDS):
        return (
            "마슈부",
            "IFANCA Shopper's Guide는 fatty acids, stearic acid, magnesium stearate 등을 investigate further 대상으로 둔다. 지방산/스테아레이트 계열은 원료가 식물성인지 동물성인지 이름만으로 알 수 없어 마슈부로 분류",
            IFANCA_FATTY_TITLE,
            IFANCA_FATTY_URL,
        )

    if name in GLUTAMATE_EXACT:
        return (
            "마슈부",
            "IFANCA는 amino acid를 halal review 대상 성분군으로 본다. 글루탐산나트륨 계열은 제조공정과 원료 정보 없이는 이름만으로 확정하기 어려워 마슈부로 분류",
            IFANCA_AMINO_TITLE,
            IFANCA_AMINO_URL,
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
    reviewed["batch7_status"] = pd.Series(statuses, dtype="string")
    reviewed["batch7_note"] = pd.Series(notes, dtype="string")
    reviewed["batch7_source_title"] = pd.Series(source_titles, dtype="string")
    reviewed["batch7_source_url"] = pd.Series(urls, dtype="string")

    apply_mask = reviewed["batch7_status"].notna()
    reviewed.loc[apply_mask, "resolved_status"] = reviewed.loc[apply_mask, "batch7_status"]
    reviewed.loc[apply_mask, "resolved_reason"] = reviewed.loc[apply_mask, "batch7_note"]

    review_only = reviewed[apply_mask].copy()
    reviewed.to_csv(OUT_CSV, index=False)
    review_only.to_csv(REVIEW_CSV, index=False)

    print(f"batch7_applied={int(apply_mask.sum())}")
    print(review_only['batch7_status'].value_counts(dropna=False).to_string())
    print(f"saved_review={REVIEW_CSV}")
    print(f"saved_final={OUT_CSV}")


if __name__ == "__main__":
    main()
