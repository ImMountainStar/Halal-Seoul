#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


PRIORITY_QUEUE_CSV = Path("data/materials_df_web_review_queue_priority.csv")
REVIEWED_BASE_CSV = Path("data/materials_df_labeled_expert_reviewed_batch1.csv")
BATCH2_QUEUE_OUT = Path("data/materials_df_web_review_batch2.csv")
BATCH2_REVIEWED_OUT = Path("data/materials_df_labeled_business_ready_v1.csv")

MUIS_ETHANOL_URL = "https://www.muis.gov.sg/resources/khutbah-and-religious-advice/fatwa/ethanol--english"
MUIS_FOOD_URL = "https://www.muis.gov.sg/halal/Religious-Guidelines/Food-and-Drinks-Categories"
IFANCA_GUIDE_URL = "https://ifanca.org/resources/shoppers-guide/"
IFANCA_INGREDIENTS_URL = "https://ifanca.org/resources/halal-for-entrepreneurs-your-key-to-new-markets/"


def contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(pattern.lower() in lowered for pattern in patterns)


def review_row(name: str) -> tuple[str | None, str | None, str | None]:
    if contains_any(name, ("주정", "알콜", "알코올", "ethanol", "에탄올", "alcohol")):
        return (
            "마슈부",
            "알코올/주정 계열은 MUIS 기준상 조건부 허용 가능성이 있어 출처·용도·농도 정보 없이는 마슈부로 유지",
            MUIS_ETHANOL_URL,
        )

    if contains_any(name, ("레시틴", "lecithin")):
        return (
            "마슈부",
            "MUIS는 레시틴을 식물/동물 유래에 따라 달라지는 syubhah 예시로 제시하므로 마슈부로 분류",
            MUIS_FOOD_URL,
        )

    if contains_any(name, ("글리세린", "glycerin", "글리세롤", "glycerol")):
        return (
            "마슈부",
            "IFANCA는 glycerin을 출처 검증이 필요한 성분군으로 다루므로 출처 미확인 상태에서는 마슈부로 분류",
            IFANCA_INGREDIENTS_URL,
        )

    if contains_any(name, ("효소", "enzyme")):
        return (
            "마슈부",
            "IFANCA는 enzyme을 할랄 검토 대상 성분군으로 명시하므로 출처 미확인 상태에서는 마슈부로 분류",
            IFANCA_INGREDIENTS_URL,
        )

    if "향" in name:
        return (
            "마슈부",
            "IFANCA는 flavors/flavorings를 검토 대상으로 보며 동물성·알코올 용매 가능성이 있어 마슈부로 분류",
            IFANCA_GUIDE_URL,
        )

    return (None, None, None)


def main() -> None:
    queue_df = pd.read_csv(PRIORITY_QUEUE_CSV).copy()
    reviewed_df = pd.read_csv(REVIEWED_BASE_CSV)

    statuses: list[str | None] = []
    notes: list[str | None] = []
    urls: list[str | None] = []

    for name in queue_df["material_name"].fillna("").astype(str):
        status, note, url = review_row(name)
        statuses.append(status)
        notes.append(note)
        urls.append(url)

    queue_df["batch2_web_status"] = pd.Series(statuses, dtype="string")
    queue_df["batch2_web_note"] = pd.Series(notes, dtype="string")
    queue_df["batch2_source_url"] = pd.Series(urls, dtype="string")

    resolved = reviewed_df.copy()
    resolved["batch2_web_status"] = pd.Series([pd.NA] * len(resolved), dtype="string")
    resolved["batch2_web_note"] = pd.Series([pd.NA] * len(resolved), dtype="string")
    resolved["batch2_source_url"] = pd.Series([pd.NA] * len(resolved), dtype="string")

    for _, row in queue_df.iterrows():
        material_name = row["material_name"]
        mask = resolved["material_name"] == material_name
        resolved.loc[mask, "batch2_web_status"] = row["batch2_web_status"]
        resolved.loc[mask, "batch2_web_note"] = row["batch2_web_note"]
        resolved.loc[mask, "batch2_source_url"] = row["batch2_source_url"]
        if pd.notna(row["batch2_web_status"]):
            resolved.loc[mask, "resolved_status"] = row["batch2_web_status"]
            resolved.loc[mask, "resolved_reason"] = row["batch2_web_note"]

    BATCH2_QUEUE_OUT.parent.mkdir(parents=True, exist_ok=True)
    queue_df.to_csv(BATCH2_QUEUE_OUT, index=False)
    resolved.to_csv(BATCH2_REVIEWED_OUT, index=False)

    print(f"batch2_rows={len(queue_df)}")
    print(queue_df["batch2_web_status"].fillna("(null)").value_counts(dropna=False).to_string())
    print(f"saved_queue={BATCH2_QUEUE_OUT}")
    print(f"saved_reviewed={BATCH2_REVIEWED_OUT}")


if __name__ == "__main__":
    main()
