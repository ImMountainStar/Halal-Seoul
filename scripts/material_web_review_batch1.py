#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


PRIORITY_QUEUE_CSV = Path("data/materials_df_web_review_queue_priority.csv")
REVIEWED_BASE_CSV = Path("data/materials_df_labeled_expert_reviewed.csv")
BATCH1_QUEUE_OUT = Path("data/materials_df_web_review_batch1.csv")
BATCH1_REVIEWED_OUT = Path("data/materials_df_labeled_expert_reviewed_batch1.csv")

MUIS_BASIC_URL = "https://www.muis.gov.sg/halal/Religious-Guidelines/Food-and-Drinks-Categories"
MUIS_ETHANOL_URL = "https://www.muis.gov.sg/resources/khutbah-and-religious-advice/fatwa/ethanol--english"
IFANCA_URL = "https://ifanca.org/resources/halal-happenings-spring-2007/"


def is_alcohol_family(name: str) -> bool:
    lowered = name.lower()
    patterns = (
        "주정",
        "알콜",
        "알코올",
        "ethanol",
        "에탄올",
        "alcohol",
    )
    return any(pattern in lowered for pattern in patterns)


def review_row(name: str) -> tuple[str | None, str | None, str | None, str | None]:
    if name == "식물성글리세린":
        return (
            "할랄",
            "식물성 유래가 명시된 글리세린은 출처가 분명해 할랄로 권고",
            MUIS_BASIC_URL,
            "MUIS는 식물 유래 성분을 기본적으로 할랄로 보며, 출처가 명확한 경우 syubhah를 해소할 수 있음.",
        )

    if is_alcohol_family(name):
        return (
            "마슈부",
            "알코올/주정 계열은 MUIS 기준상 조건부 허용 가능성이 있어, 출처·용도·농도 정보 없이는 하람 확정이 아니라 마슈부로 권고",
            MUIS_ETHANOL_URL,
            "MUIS fatwa allows natural/synthetic ethanol as a solvent under conditions; therefore substring-only haram labeling is too coarse. This is an inference.",
        )

    if "향" in name:
        return (
            "마슈부",
            "향료 계열은 IFANCA 기준상 알코올 용매 및 동물성 유래 가능성이 있어 마슈부로 권고",
            IFANCA_URL,
            "IFANCA notes flavors can contain alcohol and animal-derived ingredients. This is an inference for unlabeled source.",
        )

    return (None, None, None, None)


def main() -> None:
    queue_df = pd.read_csv(PRIORITY_QUEUE_CSV).head(40).copy()
    reviewed_df = pd.read_csv(REVIEWED_BASE_CSV)

    final_statuses: list[str | None] = []
    review_notes: list[str | None] = []
    primary_urls: list[str | None] = []
    inference_notes: list[str | None] = []

    for name in queue_df["material_name"].fillna("").astype(str):
        status, note, url, inference = review_row(name)
        final_statuses.append(status)
        review_notes.append(note)
        primary_urls.append(url)
        inference_notes.append(inference)

    queue_df["web_review_status"] = pd.Series(final_statuses, dtype="string")
    queue_df["web_review_note"] = pd.Series(review_notes, dtype="string")
    queue_df["primary_source_url"] = pd.Series(primary_urls, dtype="string")
    queue_df["inference_note"] = pd.Series(inference_notes, dtype="string")

    batch1_resolved = reviewed_df.copy()
    batch1_resolved["batch1_web_status"] = pd.Series([pd.NA] * len(batch1_resolved), dtype="string")
    batch1_resolved["batch1_web_note"] = pd.Series([pd.NA] * len(batch1_resolved), dtype="string")
    batch1_resolved["batch1_web_source_url"] = pd.Series([pd.NA] * len(batch1_resolved), dtype="string")

    for _, row in queue_df.iterrows():
        material_name = row["material_name"]
        mask = batch1_resolved["material_name"] == material_name
        batch1_resolved.loc[mask, "batch1_web_status"] = row["web_review_status"]
        batch1_resolved.loc[mask, "batch1_web_note"] = row["web_review_note"]
        batch1_resolved.loc[mask, "batch1_web_source_url"] = row["primary_source_url"]
        if pd.notna(row["web_review_status"]):
            batch1_resolved.loc[mask, "resolved_status"] = row["web_review_status"]
            batch1_resolved.loc[mask, "resolved_reason"] = row["web_review_note"]

    BATCH1_QUEUE_OUT.parent.mkdir(parents=True, exist_ok=True)
    queue_df.to_csv(BATCH1_QUEUE_OUT, index=False)
    batch1_resolved.to_csv(BATCH1_REVIEWED_OUT, index=False)

    print(f"batch1_rows={len(queue_df)}")
    print(queue_df['web_review_status'].fillna('(null)').value_counts(dropna=False).to_string())
    print(f"saved_queue={BATCH1_QUEUE_OUT}")
    print(f"saved_reviewed={BATCH1_REVIEWED_OUT}")


if __name__ == "__main__":
    main()
