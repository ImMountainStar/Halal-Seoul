# FastAPI Modular Monolith Structure v1

Last updated: 2026-02-25

## 1. Directory Layout

```text
app/
  main.py
  core/
    config.py
    security.py
    database.py
    exceptions.py
    logging.py
  common/
    schemas/
    utils/
    pagination.py
  modules/
    auth/
      router.py
      service.py
      repository.py
      schemas.py
      models.py
    commerce/
      products/
        router.py
        service.py
        repository.py
        schemas.py
        models.py
      cart/
      orders/
      payments/
      refunds/
    scan/
      router.py
      service.py
      repository.py
      schemas.py
      models.py
      ocr/
        google_vision_client.py
      classifier/
        normalize.py
        classify.py
    admin/
      reports/
      halal_ingredients/
  workers/
    scan_retry_worker.py
  tests/
    unit/
    integration/
```

## 2. Module Boundaries

- `auth`: 회원/소셜 액세스 토큰 발급
- `commerce`: 상품, 장바구니, 주문, 결제, 환불
- `scan`: OCR, 성분 분리/정규화, 판별, 스캔 이력
- `admin`: 오탐 신고 처리, 할랄 판정 데이터 운영

규칙:
- 라우터는 서비스만 호출
- 서비스는 여러 리포지토리를 조합
- 리포지토리는 DB I/O만 담당
- 모듈 간 직접 DB 접근 금지, 서비스 레이어를 통해서만 접근

## 3. FastAPI App Wiring

```python
# app/main.py
from fastapi import FastAPI
from app.modules.auth.router import router as auth_router
from app.modules.commerce.products.router import router as products_router
from app.modules.commerce.cart.router import router as cart_router
from app.modules.commerce.orders.router import router as orders_router
from app.modules.scan.router import router as scan_router
from app.modules.admin.reports.router import router as admin_reports_router

app = FastAPI(title="Halal Seoul API", version="v1")

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products_router, prefix="/api/v1/products", tags=["products"])
app.include_router(cart_router, prefix="/api/v1/cart", tags=["cart"])
app.include_router(orders_router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(scan_router, prefix="/api/v1/scan", tags=["scan"])
app.include_router(admin_reports_router, prefix="/api/v1/admin/reports", tags=["admin"])
```

## 4. Runtime Flow

### 4.1 Scan request flow
1. `POST /scan/sessions`
2. API receives image in memory
3. OCR request to Google Vision
4. ingredient split/normalize/classify
5. save `scan_sessions` + `ingredient_results`
6. return response and immediately dispose image bytes

### 4.2 Retry flow
1. OCR timeout/failure in sync path
2. one immediate retry in API path
3. enqueue SQS message if still failed
4. worker retries up to max 5 attempts
5. persist final result as success or `success=false`

## 5. Cross-Cutting Concerns

- `trace_id` issued per request and logged to CloudWatch
- rate limit on `POST /scan/sessions` and payment APIs
- idempotency key required for payment/refund requests
- no scan image persistence (in-memory only)
- secrets via AWS Secrets Manager

## 6. Environment Variables (initial)

```bash
APP_ENV=prod
JWT_ACCESS_TTL_MIN=15
DB_COMMERCE_DSN=postgresql+psycopg://...
DB_SCANLOG_DSN=postgresql+psycopg://...
GOOGLE_VISION_ENDPOINT=https://vision.googleapis.com
GOOGLE_VISION_TIMEOUT_MS=2200
SCAN_MAX_RETRY=5
AWS_REGION=ap-northeast-2
SQS_SCAN_RETRY_URL=https://sqs.ap-northeast-2.amazonaws.com/...
```
