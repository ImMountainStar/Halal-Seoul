# Deferred Implementation Notes

Date: 2026-03-11
Purpose: record items explicitly deferred for later implementation

## 1. Confirmed Deferred Items

### 1.1 Real OCR integration

Status:
- deferred

Reason:
- shopping mall app completion has higher priority than scan integration

Later scope:
- real OCR vendor integration
- real classification pipeline
- real persistence for scan execution results
- real retry execution
- real latency measurement

Current state:
- scan API skeleton exists
- no real OCR model/service is connected

## 1.2 Scan feature integration after commerce completion

Status:
- deferred

Reason:
- current product priority is commerce first, scan later

Later scope:
- complete scan feature as integrated secondary domain after cart/order/refund/admin commerce flow is stable

Current state:
- scan structure is prepared
- commerce flow is the active implementation track

## 1.3 Real database-based admin role management

Status:
- deferred

Reason:
- current stage uses a lightweight admin allowlist so commerce development can keep moving

Later scope:
- persist user role in real DB
- read role from DB at login/auth time
- support admin role promotion/demotion through admin tooling or console
- remove dependency on environment-based admin email allowlist

Current state:
- admin role is assigned from configured admin email allowlist
- admin API enforcement is implemented, but DB-backed role management is not

## 2. Current Temporary Decisions

Until deferred work is resumed, keep these temporary rules:

1. commerce-first execution order
2. scan remains skeleton/integration-ready only
3. admin role is enforced via configured admin email allowlist
4. no real OCR model connection yet

## 3. Resume Order Recommendation

When deferred work resumes, recommended order is:

1. complete remaining commerce stabilization
2. move auth/admin role handling to real DB-backed role management
3. connect real OCR integration to existing scan module skeleton
4. expand scan persistence and retry handling only after OCR flow is working
