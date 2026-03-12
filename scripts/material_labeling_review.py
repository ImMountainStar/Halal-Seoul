#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


INPUT_CSV = Path("data/materials_df_labeled.csv")
REVIEWED_CSV = Path("data/materials_df_labeled_expert_reviewed.csv")
WEB_QUEUE_CSV = Path("data/materials_df_web_review_queue.csv")

HIGH = "high"
MEDIUM = "medium"

PORK_PATTERNS = (
    "돼지",
    "돈지",
    "돈육",
    "포크",
    "lard",
)

FISH_GELATIN_PATTERNS = (
    "생선젤라틴",
    "피쉬젤라틴",
    "fish gelatin",
)

EGG_PATTERNS = (
    "난백",
    "난황",
    "전란",
    "계란",
    "달걀",
    "알가공품",
    "알가공",
    "알부민",
)

GENERIC_GELATIN_PATTERNS = (
    "젤라틴",
    "gelatin",
)

QUESTIONABLE_DAIRY_PATTERNS = (
    "유청",
    "whey",
    "카제인",
    "casein",
    "렌넷",
    "rennet",
)

PLANT_FALSE_POSITIVE_PATTERNS = (
    "산사자",
    "서양산사자",
    "토사자",
    "코끼리마늘",
    "까마귀쪽나무",
    "인동덩굴꽃봉오리",
    "정향나무꽃봉오리",
    "칡꽃봉오리",
)

ALCOHOL_REVIEW_PATTERNS = (
    "주정",
    "알콜",
    "알코올",
    "alcohol",
    "ethanol",
    "에탄올",
)

OTHER_WEB_REVIEW_PATTERNS = (
    "레시틴",
    "lecithin",
    "글리세린",
    "glycerin",
    "글리세롤",
    "glycerol",
)

PLANT_SOURCE_HIGH_CONFIDENCE_PATTERNS = (
    "식물성글리세린",
    "대두레시틴",
)

SLAUGHTER_DEPENDENT_RE = re.compile(
    r"(소고기|쇠고기|우육|우지|우골|우피|한우|닭고기|닭뼈|닭육수|닭지방|닭추출|"
    r"양고기|양육|염소(?:$|고기|육|추출)|오리고기|오리육수|오리뼈|오리지방|^오리$|"
    r"사슴(?:고기|육골|추출)|타조(?:고기|뼈|육|추출)|낙타|칠면조)"
)

EGG_RE = re.compile(
    r"(난백|난황|전란|알부민|알가공품|알가공|"
    r"계란(?:$|노른자|흰자|분말|액|단백|추출|플레이크|과립)|"
    r"달걀(?:$|노른자|흰자|분말|액))"
)

ENZYME_RE = re.compile(
    r"(^효소$|효소(?:제|액|분말|분해|함유|처리)|[가-힣A-Za-z]+효소(?:$|제|액|분말|분해|함유|처리)|enzyme)"
)


def contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(pattern.lower() in lowered for pattern in patterns)


def is_pork(text: str) -> bool:
    return contains_any(text, PORK_PATTERNS)


def is_fish_gelatin(text: str) -> bool:
    return contains_any(text, FISH_GELATIN_PATTERNS)


def is_egg(text: str) -> bool:
    return bool(EGG_RE.search(text))


def is_generic_gelatin(text: str) -> bool:
    return contains_any(text, GENERIC_GELATIN_PATTERNS)


def is_questionable_dairy(text: str) -> bool:
    return contains_any(text, QUESTIONABLE_DAIRY_PATTERNS)


def is_plant_false_positive(text: str) -> bool:
    return contains_any(text, PLANT_FALSE_POSITIVE_PATTERNS)


def is_alcohol_review(text: str) -> bool:
    return contains_any(text, ALCOHOL_REVIEW_PATTERNS)


def is_other_web_review(text: str) -> bool:
    return contains_any(text, OTHER_WEB_REVIEW_PATTERNS) or bool(ENZYME_RE.search(text))


def is_plant_source_high_confidence(text: str) -> bool:
    return contains_any(text, PLANT_SOURCE_HIGH_CONFIDENCE_PATTERNS)


def is_slaughter_dependent(text: str) -> bool:
    return bool(SLAUGHTER_DEPENDENT_RE.search(text))


def classify_with_policy(material_name: str) -> tuple[str | None, str | None, str | None, str | None]:
    text = str(material_name or "").strip()
    if not text:
        return None, None, None, None

    if is_pork(text):
        return "하람", "돼지/돈지 계열 명시 원료는 하람으로 확정", "auto_apply", HIGH

    if is_fish_gelatin(text):
        return "할랄", "생선 유래 젤라틴은 고신뢰 할랄로 재분류", "auto_apply", HIGH

    if is_egg(text):
        return "할랄", "난백/난황/전란 등 알 유래 원료는 고신뢰 할랄로 재분류", "auto_apply", HIGH

    if is_plant_false_positive(text):
        return "할랄", "동물명 포함 식물성 명칭 오탐을 식물성 원료로 교정", "auto_apply", HIGH

    if is_questionable_dairy(text):
        return "마슈부", "유청/카제인/렌넷 계열은 원료·공정 의존성이 있어 마슈부로 보수 재분류", "auto_apply", HIGH

    if is_slaughter_dependent(text):
        return "마슈부", "도축 방식 확인이 필요한 육류/가금류 유래 원료는 마슈부로 보수 재분류", "auto_apply", HIGH

    if is_generic_gelatin(text):
        return "마슈부", "유래 동물 확인이 필요한 젤라틴 일반 항목은 마슈부 유지", "auto_apply", HIGH

    if is_plant_source_high_confidence(text):
        return "할랄", "식물성/대두 유래가 명시된 원료는 고신뢰 할랄로 분류", "auto_apply", HIGH

    if is_alcohol_review(text):
        return None, "주정/알코올 계열은 농도·용도·합성 경로 확인이 필요해 웹 검수 대상으로 분리", "web_review", HIGH

    if is_other_web_review(text):
        return None, "효소/레시틴/글리세린 계열은 출처 의존성이 있어 웹 검수 대상으로 분리", "web_review", MEDIUM

    return None, None, None, None


def main() -> None:
    df = pd.read_csv(INPUT_CSV)

    expert_status: list[str | None] = []
    expert_reason: list[str | None] = []
    review_action: list[str | None] = []
    review_confidence: list[str | None] = []

    for material_name in df["material_name"].fillna("").astype(str):
        status, reason, action, confidence = classify_with_policy(material_name)
        expert_status.append(status)
        expert_reason.append(reason)
        review_action.append(action)
        review_confidence.append(confidence)

    reviewed = df.copy()
    reviewed["expert_status"] = pd.Series(expert_status, dtype="string")
    reviewed["expert_reason"] = pd.Series(expert_reason, dtype="string")
    reviewed["review_action"] = pd.Series(review_action, dtype="string")
    reviewed["review_confidence"] = pd.Series(review_confidence, dtype="string")

    reviewed["resolved_status"] = reviewed["expert_status"].fillna(reviewed["halal_status"])
    reviewed["resolved_reason"] = reviewed["expert_reason"].fillna(reviewed["reason"])
    reviewed.loc[reviewed["review_action"] == "web_review", "resolved_status"] = pd.NA
    reviewed.loc[reviewed["review_action"] == "web_review", "resolved_reason"] = "웹 검수 필요"

    web_queue = reviewed[reviewed["review_action"] == "web_review"].copy()
    if "halal_status" in web_queue.columns:
        web_queue = web_queue[
            web_queue["halal_status"].notna()
            | web_queue["material_name"].fillna("").astype(str).str.len().gt(0)
        ]

    REVIEWED_CSV.parent.mkdir(parents=True, exist_ok=True)
    reviewed.to_csv(REVIEWED_CSV, index=False)
    web_queue.to_csv(WEB_QUEUE_CSV, index=False)

    auto_applied = reviewed["review_action"].eq("auto_apply").sum()
    relabeled = (
        reviewed["expert_status"].notna()
        & (reviewed["expert_status"].fillna("") != reviewed["halal_status"].fillna(""))
    ).sum()
    print(f"rows={len(reviewed)}")
    print(f"auto_applied={int(auto_applied)}")
    print(f"relabeled={int(relabeled)}")
    print(f"web_review_queue={len(web_queue)}")
    print(f"saved_reviewed={REVIEWED_CSV}")
    print(f"saved_web_queue={WEB_QUEUE_CSV}")


if __name__ == "__main__":
    main()
