# Halal Classification Setup

## 1) Install dependency
```bash
pip install -r requirements.txt
```

## 2) Fill domain rules
Edit `config/halal_rules.json`.

- `overrides.exact`: exact material-name match rules
- `rules.haram_contains`: haram keyword list
- `rules.review_contains`: mashbooh(마슈부, 출처확인필요) keyword list
- `rules.halal_contains`: halal keyword list

Priority is:
1. exact override
2. haram keyword
3. review keyword (explicit mashbooh terms only)
4. halal keyword
5. no match -> `halal_status` is null (결측치)

## 3) Dry-run
```bash
python scripts/halal_classifier.py --dry-run
```

## 4) Write labeled output
```bash
python scripts/halal_classifier.py --output data/materials_df_labeled.csv
```

If you want to re-classify rows that already have `halal_status`, add `--overwrite`.
