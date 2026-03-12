# Ingredient Labeling Progress

Last updated: 2026-03-09

## Goal

- Build an internally usable halal ingredient review dataset from `data/materials_df_labeled.csv`.

## Current Working Files

- Source labeled input: `data/materials_df_labeled.csv`
- Current working dataset: `data/materials_df_labeled_business_ready_v18.csv`
- Reviewed ingredient master: `data/ingredient_master_v18.csv`
- Backfilled normalized table: `data/unique_materials_kor_backfilled_v18.csv`
- Operational review queue: `data/operational_review_queue_v1.csv`
- Formula hold queue: `data/formula_hold_queue_v1.csv`
- Normalization candidates: `data/normalization_candidates_v1.csv`
- Removed values archive: `data/source_hold_removed_v1.csv`

## Editing Rule

- Update only `resolved_status` and `resolved_reason` in `data/materials_df_labeled_business_ready_v18.csv`.
- Treat all other generated files as derived outputs and rebuild them after manual edits.

## Current Counts

- Halal: 655
- Mashbooh: 4201
- Haram: 112
- Unlabeled: 12134
- Excluded from active queue: 39

## What Has Been Done

- Corrected obvious false positives from naive keyword matching.
- Built conservative web-review rules using IFANCA and MUIS primary sources.
- Labeled high-confidence single additives, salts, mineral salts, preservatives, sweeteners, acids, cellulose/alginates, and similar low-risk ingredients.
- Moved extraction/concentrate materials to `Mashbooh` because solvent/process data is missing.
- Moved flavoring materials to `Mashbooh` because carrier/solvent data is missing.
- Removed source-hold nucleotide rows from the working dataset.
- Applied first-pass normalization backfill for typo-level variants.
- Excluded clearly broken or untraceable fragment values from the active review queue.
- Applied direct in-place typo normalization for safe canonical matches.
- Excluded formula/base values with attached internal product codes from the active review queue.

## Queue Policy

- `operational_review_queue_v1.csv`: active internal review queue
- `formula_hold_queue_v1.csv`: formula/base/mix items requiring component-level review
- `source_hold_removed_v1.csv`: unified archive of all values removed from the working dataset, including source-hold removals and excluded noise values

## Current Operating Rule

- Use `Halal` only when the ingredient is clearly low-risk from name and source-backed policy.
- Use `Mashbooh` when origin, solvent, carrier, or process information is missing.
- Use `Haram` only when the prohibited origin is explicit.
- Exclude broken, truncated, or untraceable strings from the active queue.

## Next Focus

- Continue reducing `기타 미해결 단품` with high-confidence single-ingredient reviews.
- Expand normalization only for typo-level or spelling-level variants that preserve meaning.
- Keep formula/base/mix items out of automatic decisioning until supporting specs exist.
