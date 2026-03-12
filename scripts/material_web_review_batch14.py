#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v14.csv")
QUEUE_CSV = Path("data/operational_review_queue_v1.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v15.csv")
REVIEW_CSV = Path("data/materials_df_web_review_batch14.csv")

IFANCA_SOURCE_TITLE = "IFANCA Shopper's Guide"
IFANCA_SOURCE_URL = "https://ifanca.org/resources/shoppers-guide/"
MUIS_SOURCE_TITLE = "MUIS Ethanol (English)"
MUIS_SOURCE_URL = "https://www.muis.gov.sg/resources/khutbah-and-religious-advice/fatwa/ethanol--english"


def main() -> None:
    df = pd.read_csv(BASE_CSV, low_memory=False)
    queue = pd.read_csv(QUEUE_CSV)

    target_names = set(
        queue.loc[queue["review_family"] == "추출/농축", "material_name"].astype(str)
    )

    statuses: list[str | None] = []
    notes: list[str | None] = []
    source_titles: list[str | None] = []
    urls: list[str | None] = []

    for _, row in df.iterrows():
        name = str(row.get("material_name", "")).strip()
        if pd.notna(row.get("resolved_status")) or name not in target_names:
            statuses.append(None)
            notes.append(None)
            source_titles.append(None)
            urls.append(None)
            continue

        statuses.append("마슈부")
        notes.append(
            "Source-based inference: IFANCA는 flavorings를 investigate further 대상으로 두고, MUIS는 solvent ethanol 허용을 조건부로 본다. 추출/농축 원료는 용매와 공정 정보 없이는 할랄 확정이 어려워 마슈부로 분류"
        )
        source_titles.append(f"{IFANCA_SOURCE_TITLE}; {MUIS_SOURCE_TITLE}")
        urls.append(f"{IFANCA_SOURCE_URL} | {MUIS_SOURCE_URL}")

    reviewed = df.copy()
    reviewed["batch14_status"] = pd.Series(statuses, dtype="string")
    reviewed["batch14_note"] = pd.Series(notes, dtype="string")
    reviewed["batch14_source_title"] = pd.Series(source_titles, dtype="string")
    reviewed["batch14_source_url"] = pd.Series(urls, dtype="string")

    apply_mask = reviewed["batch14_status"].notna()
    reviewed.loc[apply_mask, "resolved_status"] = reviewed.loc[apply_mask, "batch14_status"]
    reviewed.loc[apply_mask, "resolved_reason"] = reviewed.loc[apply_mask, "batch14_note"]

    review_only = reviewed[apply_mask].copy()
    reviewed.to_csv(OUT_CSV, index=False)
    review_only.to_csv(REVIEW_CSV, index=False)

    print(f"batch14_applied={int(apply_mask.sum())}")
    print(review_only["batch14_status"].value_counts(dropna=False).to_string())
    print(f"saved_review={REVIEW_CSV}")
    print(f"saved_final={OUT_CSV}")


if __name__ == "__main__":
    main()
