# Halal Seoul API Spec v1

Last updated: 2026-03-04
Base path: `/api/v1`
Auth: JWT (Bearer)

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
      "price": 8900
    }
  ],
  "next_cursor": "string|null"
}
```

### 2.2 상품 상세
- `GET /products/{product_id}`

### 2.3 장바구니 조회
- `GET /cart`

### 2.4 장바구니 아이템 추가
- `POST /cart/items`
- body
```json
{
  "product_id": "uuid",
  "quantity": 2
}
```

### 2.5 장바구니 아이템 수량 변경
- `PATCH /cart/items/{cart_item_id}`
- body
```json
{
  "quantity": 3
}
```

### 2.6 장바구니 아이템 삭제
- `DELETE /cart/items/{cart_item_id}`

## 3. Order and Payment

### 3.1 주문 생성
- `POST /orders`
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
  }
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

### 3.4 내 주문 목록
- `GET /orders?cursor=&limit=20`

### 3.5 주문 취소 요청
- `POST /orders/{order_id}/cancel`
- body
```json
{
  "reason": "string"
}
```

### 3.6 환불 요청
- `POST /refunds`
- headers
  - `Idempotency-Key: <unique_key>` (required)
- body
```json
{
  "order_id": "uuid",
  "refund_type": "full",
  "reason": "string"
}
```

### 3.7 부분 환불 요청
- `POST /refunds/partial`
- headers
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

## 4. AI Scan

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
  "latency_ms": 1820,
  "ingredient_count": 7,
  "overall_risk": "mashbooh",
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
  - `status` can be `null` for unresolved/legacy rows

### 4.2 내 스캔 이력
- `GET /scan/sessions?cursor=&limit=20`

### 4.3 스캔 상세
- `GET /scan/sessions/{scan_session_id}`

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

### 6.1 오탐 신고 목록
- `GET /admin/reports?status=received&cursor=&limit=20`

### 6.2 오탐 신고 상태 변경
- `PATCH /admin/reports/{report_id}`
- body
```json
{
  "status": "reviewing",
  "admin_note": "string"
}
```

### 6.3 할랄 판정 데이터 등록/수정
- `POST /admin/halal-ingredients`
- `PATCH /admin/halal-ingredients/{ingredient_id}`

### 6.4 상품 등록/수정
- `POST /admin/products`
- `PATCH /admin/products/{product_id}`

## 6. Error Model

- common error response
```json
{
  "error_code": "INVALID_REQUEST",
  "message": "string",
  "trace_id": "string"
}
```

## 7. Non-Functional API Rules

- Scan API timeout budget: 3s p95
- OCR timeout: 2.2s per attempt
- API-level idempotency key required for payment/refund endpoints
  - header: `Idempotency-Key`
  - retention: 24 hours
  - same key + same payload: return original response
  - same key + different payload: `409 CONFLICT` (`IDEMPOTENCY_KEY_REUSED`)
- Image data must not be persisted after OCR processing
