#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


INPUT_CSV = Path("data/materials_df_labeled.csv")
FINAL_CSV = Path("data/materials_df_labeled_business_ready_v18.csv")
QUEUE_CSV = Path("data/operational_review_queue_v1.csv")
REPORT_MD = Path("docs/ingredient_labeling_quality_report_v18.md")


def pct(part: int, whole: int) -> str:
    if whole == 0:
        return "0.0%"
    return f"{(part / whole) * 100:.1f}%"


def main() -> None:
    raw = pd.read_csv(INPUT_CSV)
    final = pd.read_csv(FINAL_CSV, low_memory=False)
    queue = pd.read_csv(QUEUE_CSV)

    total = len(final)
    original_labeled = int(raw["halal_status"].notna().sum())
    final_labeled = int(final["resolved_status"].notna().sum())
    null_rows = total - final_labeled
    review_queue = len(queue)
    auto_applied = int(final["review_action"].eq("auto_apply").sum()) if "review_action" in final.columns else 0
    excluded_rows = int(final["excluded_flag"].fillna(False).astype(str).str.lower().eq("true").sum()) if "excluded_flag" in final.columns else 0

    status_counts = final["resolved_status"].fillna("(null)").value_counts(dropna=False)

    verdict = "Not ready for production decisioning"
    if final_labeled / total >= 0.95 and review_queue == 0:
        verdict = "Ready for production decisioning"
    elif final_labeled / total >= 0.8:
        verdict = "Usable for internal analyst review, not for automated production decisioning"

    lines = [
        "# Ingredient Labeling Quality Report v18",
        "",
        "Last updated: 2026-03-08",
        "",
        "## Summary",
        "",
        f"- Total rows: {total}",
        f"- Original labeled rows: {original_labeled} ({pct(original_labeled, total)})",
        f"- Final labeled rows: {final_labeled} ({pct(final_labeled, total)})",
        f"- Remaining unlabeled rows: {null_rows} ({pct(null_rows, total)})",
        f"- Excluded rows: {excluded_rows} ({pct(excluded_rows, total)})",
        f"- Auto relabeled rows: {auto_applied}",
        f"- Remaining operational review queue: {review_queue} ({pct(review_queue, total)})",
        f"- Verdict: {verdict}",
        "",
        "## Final Status Distribution",
        "",
    ]

    for label, count in status_counts.items():
        lines.append(f"- {label}: {count} ({pct(int(count), total)})")

    lines.extend(
        [
            "",
            "## Business Readiness Assessment",
            "",
            "- Current dataset is suitable as a review workspace, not as a production-grade halal decision engine.",
            "- Main blocker: most rows remain unlabeled because ingredient name alone is insufficient for source-sensitive judgments.",
            "- Conservative corrections improved false positives, but unresolved coverage is still too high for customer-facing automation.",
            "",
            "## Recommended Next Steps",
            "",
            "- Prioritize top-frequency unlabeled ingredients and build a reviewed ingredient master table.",
            "- Keep source-sensitive families (`enzyme`, `glycerin`, `lecithin`, `alcohol`) on a mandatory review path.",
            "- Add human-reviewed canonical mappings so repeated names do not require repeated investigation.",
        ]
    )

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"saved_report={REPORT_MD}")
    print(f"verdict={verdict}")


if __name__ == "__main__":
    main()
