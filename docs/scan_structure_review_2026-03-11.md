# Scan Structure Review

Date: 2026-03-11
Scope: request-level scan state and failure/retry model for v1

## 1. Goal

This document turns the open scan alignment issues into concrete recommendations.

Target questions:

1. Should scan requests have a request-level `status` field?
2. Should `timeout_ms` be stored per request?
3. Should `last_error_code` be stored?
4. Should `raw_ocr_text` be persisted?
5. Should retry be modeled as a simple count or a separate event table?

## 2. Recommended Direction

| 항목 | 권장안 | 이유 |
|---|---|---|
| request-level `status` | v1에서는 추가하지 않음 | 현재 API/코드가 sync-first이며 `success` + `overall_risk`로 충분함 |
| `timeout_ms` | config-only 유지 | 현재는 요청별 값이 아니라 운영 설정값임 |
| `last_error_code` | 지금은 추가하지 않음 | 아직 실제 OCR 실패 분류 체계가 없음 |
| `raw_ocr_text` | 영구 저장하지 않음 | 데이터 최소화 원칙과 이미지 비저장 정책에 더 맞음 |
| retry model | `ocr_attempt_count` 단일 카운터 유지 | v1에서는 별도 retry event 테이블까지 갈 필요가 없음 |

## 3. Decision Detail

### 3.1 Request-Level `status`

Recommendation:

- v1에서는 `scan_sessions.status`를 추가하지 않는다.
- 외부 API 기준 결과 표현은 현재대로 유지한다:
  - `success`
  - `overall_risk`

Reason:

- 현재 설계와 코드가 synchronous request/response에 가깝다.
- `status`를 넣으면 보통 `pending`, `processing`, `completed`, `failed` 같은 상태 머신이 따라와야 한다.
- 그런데 현재 저장소에는 worker, queue consumer, background completion API가 없다.
- 지금 `status`를 먼저 넣으면 실제보다 과한 구조만 생기고, 나중에 다시 손볼 가능성이 높다.

Easy explanation:

- 지금은 “요청을 넣으면 바로 결과를 돌려주는 형태”에 가깝다.
- 이런 구조에서 `status`를 먼저 넣는 건, 아직 엘리베이터도 없는데 층별 운행 전광판부터 다는 것과 비슷하다.

When to revisit:

- worker 기반 비동기 처리 흐름이 실제로 구현될 때
- “스캔 상태 조회”를 사용자에게 분리 노출해야 할 때

### 3.2 `timeout_ms`

Recommendation:

- DB 컬럼으로 저장하지 않는다.
- 운영 설정값으로만 유지한다:
  - `GOOGLE_VISION_TIMEOUT_MS`

Reason:

- 지금 timeout은 “이 요청이 특별해서 다른 timeout을 썼다”가 아니라 시스템 설정값이다.
- 설정값은 코드/환경변수에서 관리하는 편이 더 단순하다.
- 요청마다 timeout을 다르게 쓸 계획이 생기기 전까지는 저장값으로 만들 이유가 약하다.

Easy explanation:

- `timeout_ms`는 현재 주문 정보 같은 “데이터”가 아니라 서버 설정 같은 “환경 옵션”이다.
- 에어컨 온도 설정값을 주문 테이블에 넣지 않는 것과 비슷하다.

### 3.3 `last_error_code`

Recommendation:

- v1 현재 단계에서는 추가하지 않는다.
- 실제 OCR 연동 후 실패 유형이 안정적으로 나오면 internal-only 필드로 재검토한다.

Reason:

- 아직 실패 코드 체계가 없다.
- 지금 추가하면 대부분 `unknown_error` 같은 값으로 남을 가능성이 높다.
- 그 상태에서는 구조 복잡도만 증가하고 실질 운영 가치가 낮다.

Easy explanation:

- 에러코드는 “고장 분류표”가 있어야 의미가 있다.
- 아직 어떤 고장이 실제로 나는지 모르는 상태에서 코드 칸부터 만들면 빈칸만 늘어난다.

### 3.4 `raw_ocr_text`

Recommendation:

- 영구 저장하지 않는 방향으로 정리한다.
- 필요하면 디버그 환경 또는 단기 운영 로그에서만 제한적으로 다룬다.

Reason:

- 현재 문서 기조가 이미지 비저장, 데이터 최소화 쪽이다.
- `raw_ocr_text`를 저장하면 예상보다 민감하거나 불필요한 텍스트가 쌓일 수 있다.
- v1 운영 목적상 핵심은 결과(`overall_risk`, `ingredient_count`, ingredients)이지 원문 저장이 아니다.

Easy explanation:

- 정답만 남기면 되는 시험지에 초안 메모까지 전부 보관하는 셈이 될 수 있다.
- 문제가 생겼을 때만 잠깐 확인하는 수준이 더 맞다.

### 3.5 Retry Model

Recommendation:

- v1에서는 `ocr_attempt_count`만 유지한다.
- retry event 별도 테이블은 도입하지 않는다.

Reason:

- 현재 문서 기준 최대 retry는 제한적이다.
- 운영상 “몇 번 시도했는가”가 먼저 중요하지, 개별 retry event 전부가 꼭 필요한 단계는 아니다.
- event 테이블은 향후 관측/분석 요구가 커질 때 추가해도 늦지 않다.

Easy explanation:

- 지금 필요한 건 “재시도 몇 번 했는지”이지, “1번째 시도는 몇 시 몇 분 몇 초에 왜 실패했는지”까지는 아니다.
- v1에서는 단순 카운터가 더 적절하다.

## 4. Proposed V1 Rule Set

For v1, the scan request domain should work like this:

1. canonical entity name: `scan session`
2. request outcome fields:
   - `success`
   - `overall_risk`
3. retry field:
   - `ocr_attempt_count`
4. timeout handling:
   - config-only
5. failure diagnostics:
   - `trace_id` first
   - `last_error_code` deferred
6. raw OCR persistence:
   - do not persist by default

## 5. Recommended Follow-Up Changes

### 문서 수정 후보

1. `docs/sql/scanlog_db_v1.sql`에서 `raw_ocr_text` 비영속 결정 반영 완료
2. `docs/backend_structure_v1.md`에 v1은 sync-first이며 request-level `status`를 두지 않는다고 명시 완료
3. `docs/api_v1.md`에 failure diagnostics는 `trace_id` 중심이라고 보강 완료

### 구현 후보

1. 실제 OCR 연동 시 `ocr_attempt_count`, `latency_ms`, `trace_id`를 실측값으로 채우기
2. `success=false` 응답 시 trace propagation 정리
3. OCR 실패 유형이 안정화되면 internal-only `last_error_code` 재검토

## 6. Final Recommendation

Do not grow the scan request model yet.

For v1, keep it simple:

- no request-level `status`
- no per-request `timeout_ms`
- no `last_error_code` yet
- no persisted `raw_ocr_text`
- keep `ocr_attempt_count` only

This is the lowest-risk path and matches the current repository maturity.
