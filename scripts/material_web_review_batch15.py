#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v15.csv")
QUEUE_CSV = Path("data/operational_review_queue_v1.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v16.csv")
REVIEW_CSV = Path("data/materials_df_web_review_batch15.csv")

IFANCA_SOURCE_TITLE = "IFANCA Shopper's Guide"
IFANCA_SOURCE_URL = "https://ifanca.org/resources/shoppers-guide/"
MUIS_SOURCE_TITLE = "MUIS Ethanol (English)"
MUIS_SOURCE_URL = "https://www.muis.gov.sg/resources/khutbah-and-religious-advice/fatwa/ethanol--english"


def main() -> None:
    df = pd.read_csv(BASE_CSV, low_memory=False)
    queue = pd.read_csv(QUEUE_CSV)

    target_names = set(
        queue.loc[queue["review_family"] == "향료/향미", "material_name"].astype(str)
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
            "Source-based inference: IFANCA는 flavorings를 investigate further 대상으로 둔다. MUIS는 ethanol/solvent를 조건부로 다루므로 향료/향미는 carrier와 solvent 정보 없이는 할랄 확정이 어려워 마슈부로 분류"
        )
        source_titles.append(f"{IFANCA_SOURCE_TITLE}; {MUIS_SOURCE_TITLE}")
        urls.append(f"{IFANCA_SOURCE_URL} | {MUIS_SOURCE_URL}")

    reviewed = df.copy()
    reviewed["batch15_status"] = pd.Series(statuses, dtype="string")
    reviewed["batch15_note"] = pd.Series(notes, dtype="string")
    reviewed["batch15_source_title"] = pd.Series(source_titles, dtype="string")
    reviewed["batch15_source_url"] = pd.Series(urls, dtype="string")

    apply_mask = reviewed["batch15_status"].notna()
    reviewed.loc[apply_mask, "resolved_status"] = reviewed.loc[apply_mask, "batch15_status"]
    reviewed.loc[apply_mask, "resolved_reason"] = reviewed.loc[apply_mask, "batch15_note"]

    review_only = reviewed[apply_mask].copy()
    reviewed.to_csv(OUT_CSV, index=False)
    review_only.to_csv(REVIEW_CSV, index=False)

    print(f"batch15_applied={int(apply_mask.sum())}")
    print(review_only["batch15_status"].value_counts(dropna=False).to_string())
    print(f"saved_review={REVIEW_CSV}")
    print(f"saved_final={OUT_CSV}")


if __name__ == "__main__":
    main()
