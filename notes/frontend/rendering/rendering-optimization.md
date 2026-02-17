---
title: 최적화
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 최적화

# Chunking

1. **Vite manualChunks** - 라이브러리별 청크 분리
    - react-vendor: React 코어 (11 KB)
    - `chakra-ui`: UI 컴포넌트 (497 KB)
    - data: 상태관리/API (73 KB)
    - i18n: 다국어 (55 KB)
    - `xlsx`: 엑셀 처리 (332 KB)
    - router: 라우팅 (83 KB)
2. **Route-based Lazy Loading** - 페이지별 코드 스플리팅
    - 각 페이지가 별도 청크로 분리
    - 방문하지 않은 페이지는 로드하지 않음
3. **Suspense Fallback** - 로딩 중 스피너 표시

## **manualChunks 설정으로 기대할 수 있는 이점**

### 1. 네트워크 레벨 최적화

| 항목 | Before (단일 번들) | After (청크 분리) |
| --- | --- | --- |
| **초기 다운로드** | 1.6MB 전체 | 필요한 청크만 (~300KB) |
| **HTTP/2 병렬 로드** | 1개 파일 순차 | 6~10개 청크 동시 다운로드 |
| **CDN 캐시 효율** | 배포마다 전체 무효화 | 라이브러리 청크 장기 캐시 |

배포 시나리오:
├── react-vendor.js   → 6개월간 캐시 (React 업데이트 드묾)
├── chakra-ui.js      → 3개월간 캐시 (UI 라이브러리 안정)
├── xlsx.js           → 6개월간 캐시 (거의 변경 없음)
└── index.js          → 배포마다 새로 다운로드 (비즈니스 로직)

### 2. 렌더링 성능 개선

### JavaScript 파싱 시간 감소

```jsx
Before:
[Main Thread] ████████████████████████ 1.6MB 파싱 (200~400ms 블로킹)
              ↓
              렌더링 시작

After:
[Main Thread] ████ react-vendor (11KB, ~5ms)
              ████ router (83KB, ~20ms)
              ↓
              렌더링 시작 ← 훨씬 빠름
              
[Background]  ████████ chakra-ui (497KB, lazy)
              ████████ xlsx (332KB, 필요할 때만)
```

### Critical Rendering Path 단축

| 메트릭 | 개선 이유 |
| --- | --- |
| **FCP (First Contentful Paint)** | 작은 코어 번들만 파싱 후 즉시 렌더링 |
| **LCP (Largest Contentful Paint)** | 페이지별 청크만 로드, 불필요한 코드 제외 |
| **TBT (Total Blocking Time)** | 큰 JS 파싱이 여러 작은 태스크로 분산 |
| **TTI (Time to Interactive)** | 메인 스레드 블로킹 감소 |

// 현재 route/index.ts의 lazy loading과 결합

/login 접속 시:
├── react-vendor.js (11KB)     ✅ 로드
├── router.js (83KB)           ✅ 로드
├── chakra-ui.js (497KB)       ✅ 로드 (UI 필요)
├── login-xxx.js (5KB)         ✅ 로드
├── xlsx.js (332KB)            ❌ 로드 안함 (glossary에서만 필요)
└── i18n.js (55KB)             ✅ 로드

/glossaries 접속 시:
└── xlsx.js (332KB)            ✅ 이때 로드 (엑셀 업로드 기능)

## Vite 관련 Chunking 전략

https://vite.dev/guide/build.html#chunking-strategy

[https://vite.dev/guide/build#chunking-strategy](https://vite.dev/guide/build#chunking-strategy)

https://web.dev/articles/reduce-javascript-payloads-with-code-splitting

# 정적 컨텐츠 관련 캐시 전략

## nginx에서 설정

1차 배포 (v1):
index-abc123.js → 1년 캐시 설정

2차 배포 (v2, 코드 변경):
index-xyz789.js → 새 파일명, 새 캐시
index-abc123.js → 아무도 요청 안함 (HTML이 새 파일 참조)

### `immutable`의 의미

| 헤더 | 효과 |
| --- | --- |
| `public` | CDN/프록시에서 캐시 가능 |
| `immutable` | 브라우저가 재검증 요청(304) 안 함 |

Vite의 해시 기반 빌드와 완벽하게 호환됩니다.

## vite의 해시 기반 빌드

### 참고자료

https://vite.dev/guide/build.html#public-base-path

[https://vitejs.dev/guide/build.html#public-base-path](https://vitejs.dev/guide/build.html#public-base-path) → content hasing 설명

---

https://rollupjs.org/configuration-options/#output-hashcharacters

https://web.dev/articles/love-your-cache

---

# Suspense 적용

- 4 references
    - 
    - 
    - 
    - 

### Copilot said: 이제 React Best Practices 문서의 Suspense 관련

이제 React Best Practices 문서의 Suspense 관련 규칙을 더 자세히 살펴보겠습니다. vercel-labs/agent-skills 레포지토리의 **React Best Practices** 문서(AGENTS. md)를 확인했습니다. 해당 문서의 **1. 5 Strategic Suspense Boundaries** 섹션에서 Suspense가 필요한 이유를 명확하게 설명하고 있네요.

## Main Layout에서 Suspense가 필요한 이유

당신이 보여준 코드에서:

```jsx
<Suspense
  fallback={
    <Center h="100%" minH="200px">
      <Spinner size="xl" color="blue.500" />
    </Center>
  }
>
  <Outlet />
</Suspense>
```

### 핵심 이유: **Faster Initial Paint (더 빠른 초기 렌더링)**

1. **Waterfall 방지**: `<Outlet />`이 렌더링하는 자식 라우트 컴포넌트가 데이터를 비동기로 가져올 때, Suspense가 없으면 **전체 레이아웃이 데이터 로딩을 기다리며 블로킹**됩니다.
2. **레이아웃 즉시 표시**: Suspense를 사용하면 Main Layout의 나머지 부분(헤더, 사이드바, 푸터 등)은 **즉시 렌더링**되고, `<Outlet />` 영역만 로딩 스피너를 보여줍니다.
3. **스트리밍 지원**: 문서에서 설명하듯이 "wrapper shows immediately, data streams in" - 래퍼 UI는 바로 보이고, 데이터는 스트리밍으로 들어옵니다.

### React Router의 `<Outlet />`과 함께 사용하는 이유

`<Outlet />`은 중첩 라우트의 자식 컴포넌트를 렌더링합니다. 이 자식들이:

- `React.lazy()`로 코드 스플리팅되어 있거나
- 비동기 데이터 페칭을 수행하거나
- React 18의 `use()` 훅을 사용하는 경우

Suspense 없이는 전체 앱이 해당 작업이 완료될 때까지 기다려야 합니다.

### 문서의 Trade-off 언급

> "Trade-off: Faster initial paint vs potential layout shift.  Choose based on your UX priorities."
> 

| Suspense 사용 | Suspense 미사용 |
| --- | --- |
| 빠른 초기 렌더링 | 느린 초기 렌더링 |
| 로딩 → 콘텐츠 전환 시 layout shift 가능 | Layout shift 없음 |
| 사용자가 빠르게 UI 확인 가능 | 완전한 상태로 한번에 표시 |

Main Layout에서는 **사용자 경험을 위해 빠른 초기 렌더링**이 더 중요하므로 Suspense 사용이 권장됩니다.