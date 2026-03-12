#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_CSV = Path("data/materials_df_labeled_business_ready_v1.csv")
OUT_CSV = Path("data/materials_df_labeled_business_ready_v2.csv")
REVIEW_CSV = Path("data/materials_df_web_review_batch3.csv")

MUIS_FOOD_URL = "https://www.muis.gov.sg/halal/Religious-Guidelines/Food-and-Drinks-Categories"
IFANCA_ISTIHALA_URL = "https://ifanca.org/resources/change-of-state-istihala/"

SUGAR_STARCH_PATTERNS = (
    "과당",
    "포도당",
    "말토덱스트린",
    "덱스트린",
    "전분",
    "올리고당",
    "설탕",
    "시럽",
)

EXCLUSION_PATTERNS = (
    "소고기",
    "쇠고기",
    "우육",
    "닭",
    "오리",
    "양고기",
    "염소",
    "돼지",
    "돈지",
    "비프",
    "포크",
    "젤라틴",
    "효소",
    "레시틴",
    "글리세린",
    "알코올",
    "알콜",
    "주정",
    "향",
)


def contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern in text for pattern in patterns)


def is_safe_sugar_starch(text: str) -> bool:
    if not contains_any(text, SUGAR_STARCH_PATTERNS):
        return False
    if contains_any(text, EXCLUSION_PATTERNS):
        return False
    return True


def is_safe_vinegar(text: str) -> bool:
    if "식초" not in text:
        return False
    if "식초향" in text or "향" in text:
        return False
    return True


def review_row(name: str) -> tuple[str | None, str | None, str | None]:
    if is_safe_sugar_starch(name):
        return (
            "할랄",
            "MUIS 기본 원칙상 명시적 금지 성분이 아닌 일반 당류/전분/덱스트린 계열은 할랄로 분류",
            MUIS_FOOD_URL,
        )

    if is_safe_vinegar(name):
        return (
            "할랄",
            "IFANCA istihala 기준상 vinegar는 wine에서 전환된 경우도 최종 상태가 식초이면 할랄로 분류 가능",
            IFANCA_ISTIHALA_URL,
        )

    return (None, None, None)


def main() -> None:
    df = pd.read_csv(BASE_CSV)

    statuses: list[str | None] = []
    notes: list[str | None] = []
    urls: list[str | None] = []

    for _, row in df.iterrows():
        if pd.notna(row.get("resolved_status")):
            statuses.append(None)
            notes.append(None)
            urls.append(None)
            continue

        status, note, url = review_row(str(row.get("material_name", "")).strip())
        statuses.append(status)
        notes.append(note)
        urls.append(url)

    reviewed = df.copy()
    reviewed["batch3_status"] = pd.Series(statuses, dtype="string")
    reviewed["batch3_note"] = pd.Series(notes, dtype="string")
    reviewed["batch3_source_url"] = pd.Series(urls, dtype="string")

    apply_mask = reviewed["batch3_status"].notna()
    reviewed.loc[apply_mask, "resolved_status"] = reviewed.loc[apply_mask, "batch3_status"]
    reviewed.loc[apply_mask, "resolved_reason"] = reviewed.loc[apply_mask, "batch3_note"]

    review_only = reviewed[apply_mask].copy()

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    reviewed.to_csv(OUT_CSV, index=False)
    review_only.to_csv(REVIEW_CSV, index=False)

    print(f"batch3_applied={int(apply_mask.sum())}")
    print(review_only["batch3_status"].value_counts(dropna=False).to_string())
    print(f"saved_review={REVIEW_CSV}")
    print(f"saved_final={OUT_CSV}")


if __name__ == "__main__":
    main()
