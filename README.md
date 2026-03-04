# Halal Seoul 프로젝트 개요

## 서비스 정체성 (변경 반영)
- **기존 목표**: AI 스캔 앱 개발
- **변경 목표**: **쇼핑몰 앱 개발 + AI 스캔 기능 탑재**

즉, **Halal Seoul은 쇼핑몰 서비스가 중심**이며,
AI 스캔 기능은 상품/원재료의 할랄 여부 확인을 돕는 **핵심 부가 기능**입니다.

공식 사이트: https://halalseoul.kr/

## v1 확정 스펙 문서
- 쇼핑몰+AI 스캔 통합 아키텍처/운영 기준은 아래 문서에 정리했습니다.
- `docs/architecture_v1.md`
- API 명세: `docs/api_v1.md`
- FastAPI 모듈 구조: `docs/backend_structure_v1.md`
- DB DDL: `docs/sql/commerce_db_v1.sql`, `docs/sql/scanlog_db_v1.sql`

## 현재 저장소의 역할
이 저장소는 AI 스캔 기능의 기초가 되는
**원재료명(rule-based) 할랄 분류 파이프라인**을 포함합니다.

- 입력: `data/materials_df.csv`
- 규칙: `config/halal_rules.json`
- 출력: `data/materials_df_labeled.csv`
- 실행 스크립트: `scripts/halal_classifier.py`

## 기능 요약
- 원재료명 정규화 후 키워드 기반 판정
- 우선순위 기반 분류
  1. exact override
  2. haram keyword
  3. review keyword (mashbooh)
  4. halal keyword
  5. no match -> null
- dry-run / overwrite 옵션 지원

## 다음 단계 (제품 관점)
1. 쇼핑몰 앱의 상품 데이터와 분류 파이프라인 연동
2. AI 스캔 결과를 상품 상세/검색/장바구니 UX에 노출
3. 운영자용 규칙 관리(검수/승인) 프로세스 구축
4. 룰 기반 + 모델 기반 하이브리드 판정으로 확장
