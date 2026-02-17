---
title: 렌더링 개요
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 렌더링 개요

## 렌더링 모드 한눈에 보기
- CSR: 클라이언트에서 렌더링, 초기 JS 부담 큼
- SSR: 서버에서 HTML 생성, 초기 표시 빠름, 상호작용 위해 하이드레이션 필요
- SSG: 빌드 시 정적 생성, CDN 배포에 유리
- ISR: 정적+주기적 재생성으로 최신성/성능 균형

## 전역 최적화 포인트
- 번들 크기: 코드 분할, 중복 의존성 제거
- 메인 스레드: TBT 줄이기 (지연 로딩, 불필요 JS 제거)
- 레이아웃 안정성: CLS 방지(사이즈 예약), 이미지 프리로드
- 네트워크: prefetch/preload, 캐시 전략

## Core Web Vitals 요약
- LCP: 2.5s 이내, 히어로 이미지/텍스트 우선
- TBT: 200ms 이내, 코드 분할·실행 지연
- CLS: 0.1 이하, 사이즈 고정·폰트 FOUT/FOIT 관리
- FCP: 초기 표시 가속, critical CSS
- SI: 시각적 채움 속도, 위 지표들의 총합적 결과

## 체크리스트
- [ ] 렌더링 모드 선택(CSR/SSR/SSG/ISR) 명시
- [ ] 번들 분석(LCP/TBT 영향)
- [ ] 이미지/폰트 최적화
- [ ] 코드 스플리팅 및 지연 로딩
- [ ] prefetch/preload/presconnect 적용

## 관련 문서
- [CSR](csr.md)
- [렌더링 모드 비교](rendering-modes.md)
- [렌더링 최적화](rendering-optimization.md)
- [HTML 렌더링 최적화](html-rendering-optimization.md)
