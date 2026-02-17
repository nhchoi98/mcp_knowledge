---
title: HTML 렌더링 최적화
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# HTML 렌더링 최적화

## 기본 개념
- **Reflow/Layout**: 크기·위치 변화로 레이아웃 재계산 → 비용 큼
- **Repaint**: 시각 속성만 변경 → 상대적으로 가벼움
- **Compositor 친화 속성**: `transform`, `opacity` 위주로 애니메이션

## 모범 사례
- 읽기/쓰기 분리해 **layout thrashing** 방지 (`requestAnimationFrame` 등으로 배치)
- 스타일은 `<head>`에, 초기 화면용 **크리티컬 CSS**만 최소 인라인
- 폰트: `preload` + `font-display: swap`으로 FOUT/FOUC 완화
- 이미지/미디어: `loading="lazy"`, `decoding="async"`, 적절한 `srcset/sizes`
- 애니메이션: `transform/opacity` 사용, `prefers-reduced-motion` 대응
- 성능 측정: DevTools Performance/Rendering로 Recalc/Layout 확인

## 체크리스트
- [ ] 읽기-쓰기 교차로 layout thrashing 유발하지 않는가?
- [ ] 크리티컬 CSS만 인라인, 나머지 분리/지연 로드인가?
- [ ] 웹폰트 로딩 전략(font-display/preload) 적용했는가?
- [ ] 애니메이션이 Compositor 레이어(transform/opacity)에서 동작하는가?
- [ ] 이미지/미디어를 lazy 로딩하고 적절한 포맷/크기/`srcset`을 쓰는가?
