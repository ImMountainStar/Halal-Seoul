# Scan Requests Alignment Check

Date: 2026-03-11
Scope: ERD / API / backend code comparison for scan request domain

## 1. Conclusion

Current repository does not use `scan_requests` as a real object name.

- ERD/SQL uses `scan_sessions`
- API uses `/scan/sessions`
- backend code uses `ScanSession`

So today’s comparison is effectively:

- expected business term: `scan_requests`
- current implemented term: `scan_sessions`

Decision taken:

- canonical term is `scan session`
- `scan request` remains an informal business synonym only

## 2. Evidence Base

- ERD: [`docs/sql/scanlog_db_v1.sql`](/Users/sanbyeol/Library/Mobile%20Documents/com~apple~CloudDocs/halal_seoul/docs/sql/scanlog_db_v1.sql)
- API: [`docs/api_v1.md`](/Users/sanbyeol/Library/Mobile%20Documents/com~apple~CloudDocs/halal_seoul/docs/api_v1.md)
- Code:
  - [`app/modules/scan/router.py`](/Users/sanbyeol/Library/Mobile%20Documents/com~apple~CloudDocs/halal_seoul/app/modules/scan/router.py)
  - [`app/modules/scan/schemas.py`](/Users/sanbyeol/Library/Mobile%20Documents/com~apple~CloudDocs/halal_seoul/app/modules/scan/schemas.py)
  - [`app/modules/scan/service.py`](/Users/sanbyeol/Library/Mobile%20Documents/com~apple~CloudDocs/halal_seoul/app/modules/scan/service.py)
  - [`app/modules/scan/repository.py`](/Users/sanbyeol/Library/Mobile%20Documents/com~apple~CloudDocs/halal_seoul/app/modules/scan/repository.py)

Note:

- no frontend scan code exists in current repository, so `code` below means backend implementation only

## 3. Scan Request Baseline Field List

For this check, the following fields were treated as the target comparison list:

1. `id`
2. `user_id`
3. `image_url`
4. `status`
5. `retry_count`
6. `timeout_ms`
7. `last_error_code`
8. `result_summary`
9. `created_at`

Current implemented design maps these mostly to:

1. `scan_session_id`
2. `user_id`
3. image is not persisted
4. `success` + `overall_risk`
5. `ocr_attempt_count`
6. runtime config only
7. not implemented
8. `overall_risk` + `ingredient_count`
9. `created_at`

## 4. Comparison Table

| 항목 | ERD 정의 | API 정의 | 코드 구현 | 불일치 여부 | 문제 | 조치 | 우선순위 |
|---|---|---|---|---|---|---|---|
| 객체명 | `scan_sessions` | `/scan/sessions` | `ScanSession` | 예 | 업무/기획 표현은 `scan_requests`, 실제 설계/구현은 `scan_sessions` | 명칭 표준화 결정 필요 | P0 |
| `id` | `scan_session_id` 있음 | `scan_session_id` 있음 | `scan_session_id` 사용 | 부분 | 의미는 같지만 이름이 다름 | `scan_requests.id`로 부를지 `scan_session_id` 유지할지 결정 | P0 |
| `user_id` | 있음 | 응답에는 없음 | 저장/권한 체크에 사용 | 예 | API 소비자는 소유 주체를 직접 볼 수 없음 | internal-only 필드로 유지 | P2 |
| `image_url` | 없음 | 없음 | 없음 | 아니오 | 스캔 이미지는 저장하지 않는 정책 | 현행 유지, 문서 설명 유지 | 유지 가능 |
| `status` | 요청 레벨 컬럼 없음 | 요청 레벨 `status` 없음, 결과 `ingredients[].status`만 있음 | 요청 레벨은 `success` + `overall_risk` 사용 | 예 | 요청 상태 머신이 없어서 `pending/processing/failed` 추적 불가 | 상태 모델 도입 여부 구조 검토 | P0 |
| `retry_count` | 없음, 대신 `ocr_attempt_count` 있음 | `ocr_attempt_count` 있음 | `ocr_attempt_count=1` 하드코딩 | 예 | 개념은 있으나 이름 다르고 실제 재시도 로직 없음 | `ocr_attempt_count` 유지 + 실제 retry 로직 구현 | P0 |
| `timeout_ms` | 컬럼 없음 | 컬럼 없음, config-only 명시 | 코드 사용 없음 | 부분 | timeout은 개념상 중요하지만 DB/API에서 추적 불가 | config-only로 유지할지 요청 단위 기록할지 결정 | P1 |
| `last_error_code` | 없음 | 없음 | 없음 | 예 | 실패 원인 추적 구조 없음 | 실패 추적이 필요하면 필드/에러 모델 추가 검토 | P1 |
| `result_summary` | 명시 컬럼 없음, `overall_risk` + `ingredient_count`로 표현 가능 | `overall_risk`, `ingredient_count` 제공 | 동일하게 제공 | 부분 | 단일 summary 필드는 없지만 대체 필드는 존재 | 별도 필드 없이 유지 가능, 용어만 정리 | P2 |
| `created_at` | 있음 | 있음 | 있음 | 아니오 | 정합 | 유지 | 유지 가능 |

## 5. Implemented ERD Fields Check

Current real ERD fields in `scan_sessions` are:

1. `scan_session_id`
2. `user_id`
3. `success`
4. `lang`
5. `ocr_engine`
6. `ocr_attempt_count`
7. `ingredient_count`
8. `overall_risk`
9. `latency_ms`
10. `trace_id`
11. `created_at`

Comparison against API/code:

| 필드 | ERD | API | 코드 | 문제 | 조치 |
|---|---|---|---|---|---|
| `scan_session_id` | 있음 | 있음 | 있음 | 없음 | 유지 |
| `user_id` | 있음 | 비노출 | 있음 | 공개 범위 기준 불명확 | 내부 전용 여부 문서화 |
| `success` | 있음 | 있음 | 있음 | 없음 | 유지 |
| `lang` | 있음 | 있음 | 있음 | 없음 | 유지 |
| `ocr_engine` | 있음 | internal-only | 코드에 실제 값 세팅 없음 | 실제 OCR 연동 전까지 의미 약함 | OCR 연동 시 반영 |
| `ocr_attempt_count` | 있음 | 있음 | 있음 | 현재 값이 `1`로 고정 | retry 구현 시 갱신 |
| `ingredient_count` | 있음 | 있음 | 있음 | 현재 샘플값 기반 | OCR 연동 시 실값 반영 |
| `overall_risk` | 있음 | 있음 | 있음 | 현재 샘플값 기반 | OCR 연동 시 실값 반영 |
| `latency_ms` | 있음 | 있음 | 있음 | 현재 `1820` 하드코딩 | 측정값 연결 필요 |
| `raw_ocr_text` | 없음 | 비영속 정책 | 코드 저장 안 함 | 없음 | 비영속 정책 유지 |
| `trace_id` | 있음 | 있음 | 있음 | 요청 추적과 공통 에러 trace 통합 안 됨 | trace 발급 규칙 통합 |
| `created_at` | 있음 | 있음 | 있음 | 없음 | 유지 |

## 6. Confirmed Mismatch List

### 6.1 ERD has it / API does not

1. `user_id`
2. `ocr_engine`

### 6.2 API has it / code does not fully implement

1. `ocr_attempt_count`
   - field exists but retry logic is not implemented, so meaningful count가 아님
2. `latency_ms`
   - field exists but actual timing measurement 없음
3. `trace_id`
   - field exists but request-scoped trace pipeline와 연결 안 됨

### 6.3 Code has it / document meaning is weak

1. `success=True` stub 고정
2. `overall_risk="mashbooh"` stub 고정
3. `ingredient_count=1` stub 고정
4. `latency_ms=1820` stub 고정

### 6.4 Missing structures

1. request lifecycle status model (`pending`, `processing`, `completed`, `failed`)
2. last failure tracking (`last_error_code`, `last_error_message`)
3. real retry execution and retry history

## 7. Action Classification

### 즉시 수정

1. 없음

Reason:

- 지금 단계에서는 우선 구조 결정을 먼저 해야 하며, 섣불리 필드를 추가하면 다시 바뀔 가능성이 높음

### 문서 수정

1. `scan session`을 표준 용어로 확정 완료
2. `user_id`, `ocr_engine`를 internal-only 필드로 명시 완료
3. `result_summary`를 `overall_risk` + `ingredient_count`로 해석한다고 명시 완료

### 구조 검토

1. 요청 레벨 `status` 상태 머신 도입 여부
2. `timeout_ms`를 요청 단위 저장값으로 둘지, 런타임 설정으로만 둘지
3. `last_error_code` 같은 실패 추적 필드 추가 여부
4. retry를 단순 count로 볼지, retry event 별도 테이블로 뺄지

## 8. Completion Criteria Check

Today this task is complete in the following sense:

- mismatch 항목 목록화 완료
- 항목별 문제 설명 완료
- 항목별 다음 액션 분류 완료
- `즉시 수정 / 문서 수정 / 구조 검토 / 유지 가능` 분류 완료

What is still not done:

- actual design decision on request status model
- actual implementation of retry/error persistence
- frontend consumption check, because no frontend scan code is present in this repo
