# Commerce Execution Plan

Date: 2026-03-11
Scope: shopping mall core first, scan integration later

## 1. Direction

Product priority is fixed as:

1. shopping mall app completion
2. scan feature integration later

This means the repository should treat `scan` as a secondary integration domain, not the main delivery blocker for v1 commerce release.

## 2. Current Status

### Implemented now

- auth
  - register
  - login
  - token refresh
- products
  - product list
  - product detail
- payments
  - member-only payment confirm skeleton
- scan
  - API skeleton only
  - no real OCR integration

### Missing for commerce completion

- cart
  - cart read
  - add item
  - update quantity
  - delete item
- orders
  - create order
  - order detail
  - my orders list
  - cancel order
- refunds
  - full refund
  - partial refund
- admin commerce operations
  - product create/update
  - report operations can remain later than core purchase flow

## 3. Commerce Completion Definition

The shopping mall app can be considered functionally complete for v1 when the following user flow works end-to-end:

1. user registers or logs in
2. user browses products
3. user adds products to cart
4. user edits cart
5. user creates order from cart
6. user confirms payment
7. user checks order history/detail
8. user can request cancel or refund according to order state

If this flow is incomplete, scan integration should not become the primary implementation focus.

## 4. Execution Order

### Phase 1

Cart first.

Reason:

- order creation depends on cart state
- cart is the first missing core commerce object after products

Deliverables:

- `GET /cart`
- `POST /cart/items`
- `PATCH /cart/items/{cart_item_id}`
- `DELETE /cart/items/{cart_item_id}`

### Phase 2

Orders next.

Reason:

- payment confirm is meaningful only when order creation/detail exists
- current payment skeleton is ahead of order domain

Deliverables:

- `POST /orders`
- `GET /orders/{order_id}`
- `GET /orders?cursor=&limit=20`
- `POST /orders/{order_id}/cancel`

### Phase 3

Refunds after orders.

Reason:

- refund logic depends on payment + order state
- should come after order lifecycle is defined

Deliverables:

- `POST /refunds`
- `POST /refunds/partial`

### Phase 4

Admin commerce operations.

Reason:

- core buyer flow is more important than internal operations for current milestone

Deliverables:

- `POST /admin/products`
- `PATCH /admin/products/{product_id}`

### Phase 5

Real scan integration later.

Reason:

- scan is already structured enough to integrate later
- OCR/vendor/retry/ops complexity should not block commerce completion

Deliverables:

- OCR integration
- real classification pipeline
- real persistence

## 5. First API Bundle To Build

The first concrete implementation bundle should be `cart`.

### Included endpoints

1. `GET /api/v1/cart`
2. `POST /api/v1/cart/items`
3. `PATCH /api/v1/cart/items/{cart_item_id}`
4. `DELETE /api/v1/cart/items/{cart_item_id}`

### Why this bundle first

- smallest complete commerce object still missing
- directly unlocks order creation work
- easy to implement with current in-memory repository pattern

## 6. Recommended Module Shape

Follow existing project style:

- `app/modules/commerce/cart/models.py`
- `app/modules/commerce/cart/schemas.py`
- `app/modules/commerce/cart/repository.py`
- `app/modules/commerce/cart/service.py`
- `app/modules/commerce/cart/router.py`

Use the same layered pattern already used in:

- `auth`
- `products`
- `scan`

## 7. Scope Guardrails

While building commerce core:

- do not start real OCR integration
- do not expand scan data model further
- do not introduce guest checkout again
- do not over-design async flows before basic order lifecycle works

## 8. Immediate Next Action

Start implementing `cart` as the next code change.
