#!/usr/bin/env python3
from __future__ import annotations

import re
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd


INPUT_CSV = Path("data/materials_df_labeled_business_ready_v11.csv")
OUT_CSV = Path("data/normalization_candidates_v1.csv")


def simplify(text: str) -> str:
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"[^0-9A-Za-z가-힣]", "", text)
    return text.strip()


def main() -> None:
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    resolved = sorted(set(df.loc[df["resolved_status"].notna(), "material_name"].astype(str)))
    unresolved = sorted(set(df.loc[df["resolved_status"].isna(), "material_name"].astype(str)))

    resolved_simple = {name: simplify(name) for name in resolved}
    unresolved_simple = {name: simplify(name) for name in unresolved}

    candidates: list[dict[str, object]] = []
    for unresolved_name, unresolved_key in unresolved_simple.items():
        if len(unresolved_key) < 4:
            continue
        best_name = None
        best_score = 0.0
        suffix = unresolved_key[-4:]
        prefix = unresolved_key[:4]
        for resolved_name, resolved_key in resolved_simple.items():
            if resolved_key == unresolved_key:
                continue
            if not (resolved_key.startswith(prefix) or resolved_key.endswith(suffix)):
                continue
            score = SequenceMatcher(None, unresolved_key, resolved_key).ratio()
            if score > best_score:
                best_score = score
                best_name = resolved_name
        if best_name and best_score >= 0.9:
            candidates.append(
                {
                    "raw_name": unresolved_name,
                    "candidate_canonical_name": best_name,
                    "similarity": round(best_score, 3),
                    "recommended_action": "manual_normalization_review",
                }
            )

    out = pd.DataFrame(candidates).sort_values(
        ["similarity", "raw_name"], ascending=[False, True]
    ) if candidates else pd.DataFrame(columns=["raw_name", "candidate_canonical_name", "similarity", "recommended_action"])

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)

    print(f"candidate_rows={len(out)}")
    print(f"saved_candidates={OUT_CSV}")


if __name__ == "__main__":
    main()
