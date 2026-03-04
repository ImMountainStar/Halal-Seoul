# Halal Seoul v1 Architecture and Product Spec

Last updated: 2026-03-04

## 1. Product Scope (MVP)

### 1.1 Commerce core
- Product list and detail
- Cart
- Payment
- Order history and status

### 1.2 AI scan scope
- Input: ingredient-label image (camera capture)
- OCR: Google Vision (English only)
- Pipeline:
  1. OCR text extraction
  2. Ingredient split and normalization
  3. Per-ingredient classification
  4. Evidence and source field output (source can be null for now)
  5. Overall risk summary
- Output statuses:
  - `halal`
  - `haram`
  - `mashbooh`
  - `unknown`

### 1.3 Scan logging policy
- Save scan logs except images
- Do not store raw image files
- Discard image immediately after OCR
- Store OCR text and classification results only
- Success definition:
  - success: extracted ingredient count >= 1
  - failure: extracted ingredient count = 0
  - failure is returned as a normal response with `success=false`

## 2. Classification and Dispute Policy

### 2.1 Source of truth
- Ingredient classification data is managed in an internal DB
- Current preprocessed ingredient dataset is the base source

### 2.2 Quality target
- Classification accuracy target: >= 95% (gold-label benchmark)

### 2.3 Dispute handling (false-positive report)
- User can submit a misclassification report
- Reported ingredients are stored in a separate admin queue/table
- Basic workflow:
  - `received`
  - `reviewing`
  - `resolved` or `rejected`

## 3. Tech Stack Decisions

### 3.1 Client and backend
- Mobile app: React Native
- Backend: FastAPI
- Architecture style: modular monolith
  - Single repository and server
  - Internal module split: commerce / AI scan / admin

### 3.2 OCR runtime policy
- Provider: Google Vision
- Language support: Korean and English (`ko`, `en`) in v1
- Retry and timeout:
  - Per-request timeout: 2.2 seconds
  - Max retry count: up to 5
  - Recommended operation:
    - Synchronous API path: max 1 retry
    - Background worker path: remaining retries up to 5 total

## 4. Data Architecture

### 4.1 Database recommendation (confirmed direction)
- Engine: PostgreSQL (AWS RDS)
- Logical split:
  - `commerce_db`: products, users, orders, payments
  - `scanlog_db`: OCR text, scan sessions, ingredient results, dispute reports
- v1 deployment:
  - One RDS PostgreSQL instance
  - Two logical databases for separation

### 4.2 Domain data groups
- Group A: commerce product data
- Group B: halal classification data for AI decisions

## 5. AWS Deployment Recommendation (v1)
- API runtime: ECS Fargate + ALB
- Async processing: SQS + ECS worker
- Database: RDS PostgreSQL
- Cache/rate-limit/session support: ElastiCache Redis
- Logging/metrics: CloudWatch
- File handling: no S3 for scan images (in-memory temporary handling only)

## 6. Auth and Role Baseline
- Login methods:
  - Email/password
  - Social login (`google`, `kakao`)
- JWT baseline:
  - Access token TTL: 15 minutes
- Basic roles:
  - `user`
  - `admin`

## 7. Payment Baseline
- Payment provider selection is deferred in spec freeze stage
- Keep provider field/interface, finalize PG before payment integration milestone
- Refund support: required
- Partial refund support: required

### 7.1 Idempotency baseline (payment/refund)
- Header: `Idempotency-Key`
- Required endpoints:
  - `POST /payments/confirm`
  - `POST /refunds`
  - `POST /refunds/partial`
- Retention window: 24 hours
- Duplicate handling:
  - same key + same payload -> return original response
  - same key + different payload -> `409 CONFLICT`

## 8. Operations Targets (v1)
- Classification accuracy: >= 95%
  - Measure: against gold-label data
- Scan API latency: <= 3s at p95
  - Measure field: `scan_session.latency_ms`
- Scan success rate: >= 98%
  - Rule: ingredient_count >= 1
- DAU target: 1,000 within first month
  - Measure: `distinct(user_pseudo_id)`

## 9. Deferred Items
- Detailed mashbooh/unknown rule design
- Source/evidence content completion
- Monitoring dashboard design
- Policy/legal detail expansion

## 10. Regional Policy
- Primary market and policy focus: South Korea first
