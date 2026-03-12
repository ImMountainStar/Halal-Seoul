# Halal Seoul API Spec v1

Last updated: 2026-03-04
Base path: `/api/v1`
Auth: JWT (Bearer)
Trace header: `X-Trace-Id` (returned on responses; client may also send it)

## 1. Auth

### 1.1 회원가입
- `POST /auth/register`
- body
```json
{
  "email": "user@example.com",
  "password": "string",
  "name": "string"
}
```
- response `201`
```json
{
  "user_id": "uuid",
  "email": "user@example.com"
}
```

### 1.2 로그인
- `POST /auth/login`
- body
```json
{
  "email": "user@example.com",
  "password": "string"
}
```
- response `200`
```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "expires_in": 900
}
```

## 2. Catalog and Cart

### 2.1 상품 목록
- `GET /products?cursor=&limit=20&q=`
- response `200`
```json
{
  "items": [
    {
      "product_id": "uuid",
      "name": "Chicken Sausage",
      "price": 8900,
      "sale_status": "노출"
    }
  ],
  "next_cursor": "string|null"
}
```

### 2.2 상품 상세
- `GET /products/{product_id}`

### 2.3 장바구니 조회
- `GET /cart`
- headers
  - `Authorization: Bearer <access_token>` (required)
- response `200`
```json
{
  "cart_id": "uuid",
  "items": [
    {
      "cart_item_id": "uuid",
      "product_id": "uuid",
      "product_name": "Chicken Sausage",
      "unit_price": 8900,
      "quantity": 2,
      "line_total": 17800,
      "added_at": "2026-03-11T10:00:00Z"
    }
  ],
  "item_count": 2,
  "amount_total": 17800,
  "updated_at": "2026-03-11T10:00:00Z"
}
```

### 2.4 장바구니 아이템 추가
- `POST /cart/items`
- headers
  - `Authorization: Bearer <access_token>` (required)
- body
```json
{
  "product_id": "uuid",
  "quantity": 2
}
```
- response `200`
  - same as `GET /cart`

### 2.5 장바구니 아이템 수량 변경
- `PATCH /cart/items/{cart_item_id}`
- headers
  - `Authorization: Bearer <access_token>` (required)
- body
```json
{
  "quantity": 3
}
```
- response `200`
  - same as `GET /cart`

### 2.6 장바구니 아이템 삭제
- `DELETE /cart/items/{cart_item_id}`
- headers
  - `Authorization: Bearer <access_token>` (required)
- response `200`
  - same as `GET /cart`

## 3. Order and Payment

### 3.1 주문 생성
- `POST /orders`
- headers
  - `Authorization: Bearer <access_token>` (required)
- body
```json
{
  "cart_id": "uuid",
  "shipping_address": {
    "recipient": "string",
    "phone": "string",
    "line1": "string",
    "line2": "string",
    "postal_code": "string"
  },
  "customs_clearance_number": "string|null"
}
```
- response `201`
```json
{
  "order_id": "uuid",
  "status": "pending",
  "amount_total": 17800
}
```

### 3.2 결제 승인 요청
- `POST /payments/confirm`
- headers
  - `Authorization: Bearer <access_token>` (required, 회원 전용)
  - `Idempotency-Key: <unique_key>` (required)
- body
```json
{
  "order_id": "uuid",
  "payment_key": "string",
  "amount": 17800,
  "provider": "string"
}
```

### 3.3 주문 조회
- `GET /orders/{order_id}`
- headers
  - `Authorization: Bearer <access_token>` (required)
- response `200`
```json
{
  "order_id": "uuid",
  "order_number": "HS-20260311-1234ABCD",
  "status": "pending",
  "amount_total": 17800,
  "currency": "KRW",
  "customs_clearance_number": null,
  "shipping_address": {
    "recipient": "string",
    "phone": "string",
    "line1": "string",
    "line2": "string|null",
    "postal_code": "string"
  },
  "created_at": "2026-03-11T10:00:00Z",
  "updated_at": "2026-03-11T10:00:00Z",
  "items": [
    {
      "order_item_id": "uuid",
      "product_id": "uuid",
      "product_name": "Chicken Sausage",
      "unit_price": 8900,
      "quantity": 2,
      "line_total": 17800
    }
  ]
}
```

### 3.4 내 주문 목록
- `GET /orders?cursor=&limit=20`
- headers
  - `Authorization: Bearer <access_token>` (required)
- response `200`
```json
{
  "items": [
    {
      "order_id": "uuid",
      "order_number": "HS-20260311-1234ABCD",
      "status": "pending",
      "amount_total": 17800,
      "currency": "KRW",
      "created_at": "2026-03-11T10:00:00Z"
    }
  ],
  "next_cursor": "string|null"
}
```

### 3.5 주문 취소 요청
- `POST /orders/{order_id}/cancel`
- headers
  - `Authorization: Bearer <access_token>` (required)
- body
```json
{
  "reason": "string"
}
```
- response `200`
  - same as `GET /orders/{order_id}`

### 3.6 환불 요청
- `POST /refunds`
- headers
  - `Authorization: Bearer <access_token>` (required)
  - `Idempotency-Key: <unique_key>` (required)
- body
```json
{
  "order_id": "uuid",
  "refund_type": "full",
  "reason": "string"
}
```
- response `200`
```json
{
  "refund_id": "uuid",
  "order_id": "uuid",
  "refund_type": "full",
  "amount": 17800,
  "status": "requested",
  "reason": "string",
  "created_at": "2026-03-11T10:00:00Z",
  "items": [
    {
      "order_item_id": "uuid",
      "quantity": 2,
      "amount": 17800
    }
  ]
}
```

### 3.7 부분 환불 요청
- `POST /refunds/partial`
- headers
  - `Authorization: Bearer <access_token>` (required)
  - `Idempotency-Key: <unique_key>` (required)
- body
```json
{
  "order_id": "uuid",
  "items": [
    { "order_item_id": "uuid", "quantity": 1 }
  ],
  "reason": "string"
}
```
- response `200`
  - same shape as `POST /refunds`

## 4. AI Scan

- terminology
  - canonical object name: `scan session`
  - `scan request` is treated as the same business concept in discussion, but API/ERD/code use `scan_session_id` and `/scan/sessions`

### 4.1 스캔 실행
- `POST /scan/sessions`
- multipart:
  - `image`: binary (required)
  - `lang`: `ko|en` (optional, default `ko`)
- response `200` (성공 또는 실패 모두 정상 응답)
```json
{
  "scan_session_id": "uuid",
  "success": true,
  "lang": "ko",
  "ocr_attempt_count": 1,
  "latency_ms": 1820,
  "ingredient_count": 7,
  "overall_risk": "mashbooh",
  "trace_id": "string",
  "created_at": "2026-03-06T10:00:00Z",
  "ingredients": [
    {
      "raw_text": "gelatin",
      "normalized_text": "gelatin",
      "status": "mashbooh",
      "confidence": 0.97,
      "reason": "animal source not specified",
      "source_title": null,
      "source_url": null
    }
  ]
}
```
- no-match handling:
  - default status is `unknown`
  - unresolved result is normalized to `unknown`
- internal-only fields:
  - `user_id`
  - `ocr_engine`
- result summary policy:
  - `result_summary` is not a separate API field
  - use `overall_risk` with `ingredient_count` as the summary view of a scan session
- runtime policy:
  - v1 does not expose a request-level `status` field
  - OCR timeout is managed by runtime config (`GOOGLE_VISION_TIMEOUT_MS`) and is not persisted as `timeout_ms` column
  - failure diagnostics should use `trace_id` first
  - raw OCR text is not persisted in v1

### 4.2 내 스캔 이력
- `GET /scan/sessions?cursor=&limit=20`
- response `200`
```json
{
  "items": [
    {
      "scan_session_id": "uuid",
      "success": true,
      "lang": "ko",
      "ocr_attempt_count": 1,
      "ingredient_count": 7,
      "overall_risk": "mashbooh",
      "latency_ms": 1820,
      "created_at": "2026-03-06T10:00:00Z"
    }
  ],
  "next_cursor": "string|null"
}
```

### 4.3 스캔 상세
- `GET /scan/sessions/{scan_session_id}`
- response `200`
```json
{
  "scan_session_id": "uuid",
  "success": true,
  "lang": "ko",
  "ocr_attempt_count": 1,
  "ingredient_count": 7,
  "overall_risk": "mashbooh",
  "latency_ms": 1820,
  "trace_id": "string",
  "created_at": "2026-03-06T10:00:00Z",
  "ingredients": [
    {
      "ingredient_result_id": "uuid",
      "raw_text": "gelatin",
      "normalized_text": "gelatin",
      "status": "mashbooh",
      "confidence": 0.97,
      "reason": "animal source not specified",
      "source_title": null,
      "source_url": null
    }
  ]
}
```

### 4.4 오탐 신고
- `POST /scan/reports`
- body
```json
{
  "scan_session_id": "uuid",
  "ingredient_result_id": "uuid",
  "reported_status": "halal",
  "reason": "string"
}
```

## 5. Admin

### 5.1 오탐 신고 목록
- `GET /admin/reports?status=received&cursor=&limit=20`

### 5.2 오탐 신고 상태 변경
- `PATCH /admin/reports/{report_id}`
- body
```json
{
  "status": "reviewing",
  "admin_note": "string"
}
```

### 5.3 할랄 판정 데이터 등록/수정
- `POST /admin/halal-ingredients`
- `PATCH /admin/halal-ingredients/{ingredient_id}`

### 5.4 상품 등록/수정
- `POST /admin/products`
- `PATCH /admin/products/{product_id}`
- headers
  - `Authorization: Bearer <access_token>` (required)
- body example for `POST /admin/products`
```json
{
  "name": "Halal Ramen",
  "price": 6500,
  "description": "string|null",
  "sale_status": "노출"
}
```
- body example for `PATCH /admin/products/{product_id}`
```json
{
  "name": "string|null",
  "price": 7000,
  "description": "string|null",
  "sale_status": "품절"
}
```
- response `200/201`
```json
{
  "product_id": "uuid",
  "name": "Halal Ramen",
  "price": 7000,
  "sale_status": "품절",
  "description": "string|null"
}
```
- note
  - current implementation enforces admin role
  - admin role is assigned from configured admin email allowlist in the current v1 implementation

## 6. Error Model

- common error response
```json
{
  "error_code": "INVALID_REQUEST",
  "message": "string",
  "trace_id": "string"
}
```
- all error responses should include `trace_id`

## 7. Non-Functional API Rules

- Scan API timeout budget: 3s p95
- OCR timeout: 2.2s per attempt
- Scan request canonical fields:
  - state outcome: `success`, `overall_risk`
  - retry count field: `ocr_attempt_count`
  - timeout is config-only, not persisted as `timeout_ms`
- API-level idempotency key required for payment/refund endpoints
  - header: `Idempotency-Key`
  - retention: 24 hours
  - same key + same payload: return original response
  - same key + different payload: `409 CONFLICT` (`IDEMPOTENCY_KEY_REUSED`)
- Image data must not be persisted after OCR processing
