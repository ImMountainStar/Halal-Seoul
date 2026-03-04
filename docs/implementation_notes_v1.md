# Implementation Notes v1

Last updated: 2026-03-04

## 1) Role enum policy
- v1 write role is `admin` only.
- DB DDL and API auth logic both use `user | admin`.

## 2) Payment provider deferral policy
- Keep `provider` field in payment APIs/DB as string
- Final PG selection is deferred until payment integration milestone
