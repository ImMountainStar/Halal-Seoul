#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v4.csv")
PACK_CSV = Path("data/manual_review_pack_v1.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v5.csv")
REVIEW_CSV = Path("data/materials_df_web_review_batch6.csv")

IFANCA_SOURCE_TITLE = "IFANCA Shopper's Guide"
IFANCA_SOURCE_URL = "https://ifanca.org/resources/shoppers-guide-fall-2001/"


def main() -> None:
    df = pd.read_csv(BASE_CSV)
    pack = pd.read_csv(PACK_CSV)

    flavor_names = set(
        pack.loc[
            (pack["priority_tier"] == "P2") & (pack["review_family"] == "향미 화합물"),
            "material_name",
        ].astype(str)
    )

    statuses: list[str | None] = []
    notes: list[str | None] = []
    source_titles: list[str | None] = []
    urls: list[str | None] = []

    for _, row in df.iterrows():
        name = str(row.get("material_name", "")).strip()
        if pd.notna(row.get("resolved_status")):
            statuses.append(None)
            notes.append(None)
            source_titles.append(None)
            urls.append(None)
            continue

        if name in flavor_names:
            statuses.append("마슈부")
            notes.append(
                "IFANCA Shopper's Guide는 artificial/natural flavorings를 investigate further 대상으로 본다. 향미 화합물은 원료와 carrier/solvent 정보 없이는 확정할 수 없어 마슈부로 분류"
            )
            source_titles.append(IFANCA_SOURCE_TITLE)
            urls.append(IFANCA_SOURCE_URL)
        else:
            statuses.append(None)
            notes.append(None)
            source_titles.append(None)
            urls.append(None)

    reviewed = df.copy()
    reviewed["batch6_status"] = pd.Series(statuses, dtype="string")
    reviewed["batch6_note"] = pd.Series(notes, dtype="string")
    reviewed["batch6_source_title"] = pd.Series(source_titles, dtype="string")
    reviewed["batch6_source_url"] = pd.Series(urls, dtype="string")

    apply_mask = reviewed["batch6_status"].notna()
    reviewed.loc[apply_mask, "resolved_status"] = reviewed.loc[apply_mask, "batch6_status"]
    reviewed.loc[apply_mask, "resolved_reason"] = reviewed.loc[apply_mask, "batch6_note"]

    review_only = reviewed[apply_mask].copy()
    reviewed.to_csv(OUT_CSV, index=False)
    review_only.to_csv(REVIEW_CSV, index=False)

    print(f"batch6_applied={int(apply_mask.sum())}")
    print(review_only["batch6_status"].value_counts(dropna=False).to_string())
    print(f"saved_review={REVIEW_CSV}")
    print(f"saved_final={OUT_CSV}")


if __name__ == "__main__":
    main()
