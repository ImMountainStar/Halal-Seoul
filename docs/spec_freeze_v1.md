# Halal Seoul v1 Spec Freeze

Last updated: 2026-03-04
Status: In progress (owner decisions reflected)

## 1) Scope Freeze (Confirmed)
- Product direction: commerce app first, AI scan integrated feature
- MVP domains:
  - Auth
  - Catalog/Cart
  - Order/Payment
  - AI Scan
  - Admin (report + data/product management)
- API base path: `/api/v1`
- Backend architecture: FastAPI modular monolith
- Database direction:
  - PostgreSQL (RDS)
  - logical split: `commerce_db`, `scanlog_db`

## 2) Non-Functional Freeze (Confirmed)
- Scan API target latency: `p95 <= 3s`
- OCR timeout per attempt: `2.2s`
- OCR retry policy:
  - sync path: max 1 retry
  - worker path: up to 5 total attempts
- Scan image policy:
  - do not persist raw image
  - keep OCR text/result only

## 3) Data/Status Freeze (Confirmed)
- Scan statuses: `halal`, `haram`, `mashbooh`, `unknown`
- Misclassification workflow: `received -> reviewing -> resolved|rejected`
- Scan success rule:
  - success: ingredient_count >= 1
  - failure: ingredient_count = 0 (normal response with `success=false`)
- No-match fallback:
  - default: `unknown`
  - `null` is allowed for legacy/unresolved rows

## 4) Owner Decisions (Confirmed)
1. Payment provider finalization
   - Decision: provider selection can be deferred.
   - v1 action: keep provider interface in API/DB, finalize actual PG before payment integration milestone.
   - freeze deadline: before starting API implementation of `3.2 결제 승인 요청 (POST /payments/confirm)`.

2. Social login provider set
   - v1 providers: `google`, `kakao`

3. Classification fallback policy
   - default no-match value: `unknown`
   - `null` allowed: yes

4. OCR language policy
   - v1 supported languages: `en`, `ko`

5. Idempotency enforcement details (recommended and adopted)
   - Header name: `Idempotency-Key`
   - Required endpoints:
     - `POST /payments/confirm`
     - `POST /refunds`
     - `POST /refunds/partial`
   - Retention window: 24 hours
   - Duplicate handling:
     - same key + same payload -> return original status/body
     - same key + different payload -> `409 CONFLICT` (`IDEMPOTENCY_KEY_REUSED`)
     - same key while first request still in-flight -> `409 CONFLICT` (`REQUEST_IN_PROGRESS`)

6. Admin authority boundaries
   - v1 admin role policy: single write role `admin` only
   - `super_admin` is out of v1 scope

## 5) Freeze Exit Criteria
- All section 4 decisions are confirmed.
- API/DB naming mismatches are mapped in implementation notes.
- v1 implementation order is fixed and approved.

## 6) Immediate Next Actions
1. Update `docs/api_v1.md` and related docs only where decisions change behavior.
2. Start implementation from Auth -> Catalog/Cart -> Order/Payment -> Scan -> Admin.
