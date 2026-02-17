---
title: CSS 개요
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# CSS 개요

## 핵심 원칙
- 박스 모델과 `box-sizing: border-box`
- 캐스케이딩/특이도/레이어(@layer) 이해
- display/position/stacking context 기본

## 현대 레이아웃
- Flexbox: 1차원 정렬, `gap`, `flex: 1`, `min-width: 0` 주의
- Grid: 2차원, `repeat/minmax/auto-fit|fill`, 필요 시 subgrid
- 비율 유지: `aspect-ratio`
- 간격: `gap` 우선

## 반응형
- 미디어쿼리 + 환경쿼리(pointer/hover/contrast)
- 컨테이너 쿼리: `container-type: inline-size` + `@container`
- 유동 타이포: `clamp()` 패턴, 모바일 뷰포트 `svh/dvh`

## 타이포·미디어
- 라인 높이: 단위 없는 `line-height`
- 폰트: `@font-face`, `font-display: swap`, preload 필요 시
- 이미지/비디오: `object-fit`, `srcset/sizes`, `aspect-ratio`

## 상호작용/애니메이션
- `transform/opacity` 기반, `prefers-reduced-motion` 대응
- 상태 스타일: `:focus-visible`, `:has()`

## 구조/아키텍처
- 리셋/프리플라이트, 토큰(CSS 변수), 테마 전환
- 네이밍(BEM 등)·스코프(CSS Modules/CSS-in-JS/Shadow DOM)
- `@layer base, components, utilities`로 충돌 최소화

## 체크리스트
- [ ] box-sizing 적용, 레이아웃 기본 규칙 이해
- [ ] Flex/Grid에서 overflow·min-width 확인
- [ ] 반응형(미디어/컨테이너 쿼리) 적용
- [ ] 폰트/이미지 로딩 최적화 반영
- [ ] 애니메이션이 compositor 친화적인가?

[SCSS](CSS/SCSS%2026ccee38e89a808bb01fd62a41ff92ab.md)
