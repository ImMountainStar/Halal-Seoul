#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


QUEUE_CSV = Path("data/operational_review_queue_v1.csv")
OUT_CSV = Path("data/formula_hold_queue_v1.csv")


def main() -> None:
    queue = pd.read_csv(QUEUE_CSV)
    hold = queue[queue["review_family"] == "제제/혼합"].copy()
    hold = hold[["material_name", "review_family", "recommended_action", "required_evidence"]]
    hold["hold_reason"] = "carrier/부원료/제형 정보 없이는 의미가 달라져 이름만으로 판정 불가"
    hold.to_csv(OUT_CSV, index=False)

    print(f"hold_rows={len(hold)}")
    print(f"saved_hold={OUT_CSV}")


if __name__ == "__main__":
    main()
