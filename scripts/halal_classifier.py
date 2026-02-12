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


def normalize(text: str) -> str:
    if not isinstance(text, str):
        return ""
    lowered = text.strip().lower()
    lowered = re.sub(r"\s+", "", lowered)
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


def keyword_match(normalized_text: str, keyword: str) -> bool:
    normalized_keyword = normalize(keyword)
    if not normalized_keyword:
        return False
    if len(normalized_keyword) == 1:
        return normalized_text == normalized_keyword
    return normalized_keyword in normalized_text


def classify_material(material_name: str, ruleset: dict) -> Tuple[Optional[str], Optional[str]]:
    status_labels = ruleset["status_labels"]
    rules = ruleset["rules"]
    overrides = ruleset.get("overrides", {}).get("exact", {})

    raw = material_name if isinstance(material_name, str) else ""
    normalized = normalize(raw)

    for key, value in overrides.items():
        if normalize(key) == normalized:
            status_key = value["status"]
            reason = value.get("reason", "정확 일치 오버라이드")
            return status_labels[status_key], reason

    for keyword in rules.get("haram_contains", []):
        if keyword_match(normalized, keyword):
            return status_labels["haram"], f"하람 키워드 포함: {keyword}"

    for keyword in rules.get("review_contains", []):
        if keyword_match(normalized, keyword):
            return status_labels["review"], f"추가 검토 필요 키워드 포함: {keyword}"

    for keyword in rules.get("halal_contains", []):
        if keyword_match(normalized, keyword):
            return status_labels["halal"], f"할랄 키워드 포함: {keyword}"

    # Unmatched or source-unknown items must stay missing, not forced to mashbooh.
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
    # Keep target columns string-typed to avoid incompatible dtype assignment.
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
