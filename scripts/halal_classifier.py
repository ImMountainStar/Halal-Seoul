#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd


DEFAULT_INPUT = Path("data/materials_df.csv")
DEFAULT_OUTPUT = Path("data/materials_df_labeled.csv")
DEFAULT_RULES = Path("config/halal_rules.json")

# For very short Korean animal keywords, allow match only when the keyword is
# standalone or followed by typical meat/ingredient suffixes.
KOREAN_SHORT_SUFFIXES = (
    "고기",
    "육",
    "지방",
    "뼈",
    "추출",
    "추출물",
    "분말",
    "농축액",
    "엑기스",
    "오일",
    "유래",
)


def normalize_compact(text: str) -> str:
    if not isinstance(text, str):
        return ""
    lowered = text.strip().lower()
    lowered = re.sub(r"\s+", "", lowered)
    return lowered


def normalize_for_match(text: str) -> str:
    if not isinstance(text, str):
        return ""
    lowered = text.strip().lower()
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered


def strip_json_comments(raw_text: str) -> str:
    """Remove // and /* */ comments from JSONC-like text while preserving strings."""
    result = []
    i = 0
    in_string = False
    escaped = False
    n = len(raw_text)

    while i < n:
        ch = raw_text[i]
        nxt = raw_text[i + 1] if i + 1 < n else ""

        if in_string:
            result.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            result.append(ch)
            i += 1
            continue

        if ch == "/" and nxt == "/":
            i += 2
            while i < n and raw_text[i] not in ("\n", "\r"):
                i += 1
            continue

        if ch == "/" and nxt == "*":
            i += 2
            while i + 1 < n and not (raw_text[i] == "*" and raw_text[i + 1] == "/"):
                i += 1
            i += 2 if i + 1 < n else 0
            continue

        result.append(ch)
        i += 1

    return "".join(result)


def load_rules(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        raw_text = f.read()
    clean_text = strip_json_comments(raw_text)
    return json.loads(clean_text)


def contains_hangul(text: str) -> bool:
    return bool(re.search(r"[가-힣]", text))


def match_ascii_keyword(text: str, keyword: str) -> bool:
    if not keyword:
        return False
    escaped = re.escape(keyword)
    pattern = rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"
    return bool(re.search(pattern, text))


def match_short_korean_keyword(text: str, keyword: str, allow_end: bool = False) -> bool:
    escaped = re.escape(keyword)

    # Standalone token-like case
    standalone_pattern = rf"(^|[^가-힣]){escaped}($|[^가-힣])"
    if re.search(standalone_pattern, text):
        return True

    # Suffix case for terms often appended to longer words (e.g. 곡물주정)
    if allow_end:
        end_pattern = rf"{escaped}$"
        if re.search(end_pattern, text):
            return True

    # Common ingredient-form suffixes to allow terms like 오리고기, 타조육
    suffix_group = "|".join(re.escape(s) for s in KOREAN_SHORT_SUFFIXES)
    suffix_pattern = rf"{escaped}(?:{suffix_group})"
    return bool(re.search(suffix_pattern, text))


def keyword_match(
    text_for_match: str,
    compact_text: str,
    keyword: str,
    strict_short_korean: bool = False,
    allow_end_for_short_korean: bool = False,
) -> bool:
    normalized_keyword = normalize_compact(keyword)
    if not normalized_keyword:
        return False

    if strict_short_korean and contains_hangul(normalized_keyword) and len(normalized_keyword) <= 2:
        return match_short_korean_keyword(
            text_for_match,
            normalized_keyword,
            allow_end=allow_end_for_short_korean,
        )

    if contains_hangul(normalized_keyword):
        return normalized_keyword in compact_text

    return match_ascii_keyword(text_for_match, normalized_keyword)


def classify_material(material_name: str, ruleset: dict) -> Tuple[Optional[str], Optional[str]]:
    status_labels = ruleset["status_labels"]
    rules = ruleset["rules"]
    overrides = ruleset.get("overrides", {}).get("exact", {})

    raw = material_name if isinstance(material_name, str) else ""
    compact = normalize_compact(raw)
    text_for_match = normalize_for_match(raw)

    for key, value in overrides.items():
        if normalize_compact(key) == compact:
            status_key = value["status"]
            reason = value.get("reason", "정확 일치 오버라이드")
            return status_labels[status_key], reason

    for keyword in rules.get("haram_contains", []):
        if keyword_match(
            text_for_match,
            compact,
            keyword,
            strict_short_korean=True,
            allow_end_for_short_korean=True,
        ):
            return status_labels["haram"], f"하람 키워드 포함: {keyword}"

    for keyword in rules.get("review_contains", []):
        if keyword_match(text_for_match, compact, keyword):
            return status_labels["review"], f"추가 검토 필요 키워드 포함: {keyword}"

    for keyword in rules.get("halal_contains", []):
        if keyword_match(text_for_match, compact, keyword, strict_short_korean=True):
            return status_labels["halal"], f"할랄 키워드 포함: {keyword}"

    default_status_key = ruleset.get("default_status")
    if default_status_key:
        if default_status_key not in status_labels:
            raise ValueError("default_status must be one of status_labels keys")
        default_reason = ruleset.get("default_reason", "명시 규칙 미일치: 기본 라벨")
        return status_labels[default_status_key], default_reason

    return None, None


def should_update(existing_status: str, overwrite: bool) -> bool:
    if overwrite:
        return True
    if pd.isna(existing_status):
        return True
    if isinstance(existing_status, str) and existing_status.strip() == "":
        return True
    return False


def run(input_csv: Path, output_csv: Path, rules_path: Path, overwrite: bool, dry_run: bool) -> None:
    df = pd.read_csv(input_csv)
    ruleset = load_rules(rules_path)

    if "material_name" not in df.columns:
        raise ValueError("`material_name` column is required")

    if "halal_status" not in df.columns:
        df["halal_status"] = ""
    if "reason" not in df.columns:
        df["reason"] = ""
    df["halal_status"] = df["halal_status"].astype("string")
    df["reason"] = df["reason"].astype("string")

    updated = 0

    for idx, row in df.iterrows():
        if not should_update(row.get("halal_status", ""), overwrite):
            continue

        status, reason = classify_material(row.get("material_name", ""), ruleset)
        df.at[idx, "halal_status"] = status if status is not None else pd.NA
        df.at[idx, "reason"] = reason if reason is not None else pd.NA
        updated += 1

    counts = df["halal_status"].fillna("(null)").value_counts(dropna=False)
    print("[Summary]")
    print(f"rows: {len(df)}")
    print(f"updated: {updated}")
    print("status_counts:")
    for label, count in counts.items():
        print(f"  - {label}: {count}")

    if dry_run:
        print("dry-run mode: output file is not written")
        return

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"saved: {output_csv}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rule-based halal classifier for materials CSV")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output CSV path")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES, help="Rules JSON path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing halal_status values")
    parser.add_argument("--dry-run", action="store_true", help="Run without writing output")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(
        input_csv=args.input,
        output_csv=args.output,
        rules_path=args.rules,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )
