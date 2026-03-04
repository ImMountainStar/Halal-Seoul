# Halal Classification Setup

> 프로젝트 방향 업데이트: **Halal Seoul은 쇼핑몰 앱이 메인**이며, 이 문서는 그 안에 탑재되는 **AI 스캔(할랄 분류) 기능 셋업 가이드**입니다.
> 제품/인프라 기준 스펙은 `docs/architecture_v1.md`를 따릅니다.

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
5. no match -> `halal_status` defaults to `unknown` (`null` is also allowed)

Matching notes:
- English keywords are matched by token boundary (to reduce substring false positives).
- Very short Korean keywords (e.g. `오리`, `타조`, `돼지`) use stricter matching to reduce collisions like `가오리`, `오리자놀`, `돼지감자`.
- If you want every row labeled, set optional fields in `config/halal_rules.json`:
```json
{
  "default_status": "unknown",
  "default_reason": "명시 규칙 미일치"
}
```

## 3) Dry-run
```bash
python scripts/halal_classifier.py --dry-run
```

## 4) Write labeled output
```bash
python scripts/halal_classifier.py --output data/materials_df_labeled.csv
```

If you want to re-classify rows that already have `halal_status`, add `--overwrite`.
