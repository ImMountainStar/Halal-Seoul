# Ingredient Labeling Policy v1

Last updated: 2026-03-08

## Goal

Replace brittle substring labeling with a conservative halal review policy suitable for production data cleanup.

## High-confidence automatic relabel rules

1. Explicit pork/swine terms -> `하람`
2. Fish gelatin terms -> `할랄`
3. Egg-derived terms (`난백`, `난황`, `전란`, `알부민`) -> `할랄`
4. Plant-name false positives (`산사자`, `토사자`, `코끼리마늘`, `까마귀쪽나무`) -> `할랄`
5. Whey/casein/rennet family -> `마슈부`
6. Slaughter-dependent meat/poultry ingredients -> `마슈부`
7. Generic gelatin -> `마슈부`

## Web review queue rules

These require source/process review and are not auto-finalized:

1. `주정`, `에탄올`, `알코올`, `알콜`
2. `효소`, `레시틴`, `글리세린`
3. Any current label produced by obvious short-keyword false positive logic

## Source basis

- IFANCA highlights gelatin, whey, rennet and similar ingredients as common questionable ingredients because origin and processing matter.
  - <https://ifanca.org/resources/halal-happenings-spring-2007/>
- MUIS ethanol guidance treats ethanol with condition-based rules rather than a blanket substring rule, so direct `알코올` keyword matching is too coarse.
  - <https://www.muis.gov.sg/resources/khutbah-and-religious-advice/fatwa/ethanol--english>

## Operational stance

- If slaughter method is required but absent from the ingredient name, classify as `마슈부` instead of `할랄`.
- If plant origin is explicit and the previous label came from an animal-name substring false positive, correct to `할랄`.
- For web review queue items, do not finalize labels without source-backed manual verification.
