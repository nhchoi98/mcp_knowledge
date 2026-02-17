---
title: SPA Framework - Vue
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# SPA Framework - Vue

# SPA란?

페이지 전체를 다시 받지 않고, 한 번 받은 페이지 안에서 자바스크립트로 화면을 바꿔 가는 방식”**이야. 서버는 주로 **데이터(JSON)**만 주고, **라우팅·렌더링은 브라우저(클라이언트)**가 맡아

- **SPA = 하나의 HTML + JS 앱에서 필요한 부분만 동적으로 교체하는 방식**
- 장점: 빠른 화면 전환, 네이티브 앱 같은 UX
- 단점: 초기 로딩, SEO, 상태 관리 문제

# 핵심 키워드

반응성

# Teleport

## 설명

- 컴포넌트를 **현재 위치가 아닌 DOM 트리의 다른 위치**에 렌더링하도록 도와주는 기능.
- 흔히 모달, 툴팁, 드롭다운 등 부모 스타일 영향에서 벗어나야 할 UI에 사용.

**특징**

- `to` 속성에 CSS 선택자(`body`, `#modal-root`) 지정.
- 실제 렌더링은 다른 DOM 위치지만, **상위 컴포넌트의 반응성/상태는 그대로** 유지.

**장점**

- z-index, overflow 문제 회피.
- 모달/알림 UI 구현에 최적.

```jsx
<template>
  <div>
    <h1>본문</h1>
    <Teleport to="body">
      <div class="modal">나는 body 바로 밑에 붙음!</div>
    </Teleport>
  </div>
</template>

```

# Suspend

### 설명

`<Suspense>` (비동기 컴포넌트 대기)

- 비동기 컴포넌트(예: `defineAsyncComponent`)가 로딩되는 동안 **대체 UI(fallback)** 를 보여주는 컴포넌트.
- React의 Suspense와 유사

```jsx
<Suspense>
<template #default>
<AsyncComponent />
</template>
<template #fallback>
<div>로딩 중...</div>
</template>
</Suspense>
```

### 비동기 컴포넌트

# KeepAlive (컴포넌트 캐싱)

**개념**

- 동적 컴포넌트를 캐싱해 두었다가, 다시 나타날 때 **기존 상태 그대로 복원**하는 기능.
- 탭 전환 같은 UI에서 유용.

```jsx
<template>
  <KeepAlive>
    <component :is="currentView"></component>
  </KeepAlive>
</template>

<script setup>
import ViewA from './ViewA.vue'
import ViewB from './ViewB.vue'
const currentView = ref('ViewA')
</script>
```

**특징**

- `<component>` 또는 `<router-view>`와 함께 사용.
- `include`/`exclude` props로 캐싱할 컴포넌트 제어.
- 캐시된 컴포넌트는 `deactivated`/`activated` 훅 호출.
- 내부 컴포넌트를 **캐싱해 두고**, `v-if`로 제거하더라도 실제 인스턴스는 메모리에 보존.
- 다시 나타나면 **기존 상태를 복원**하고, `activated` / `deactivated` 훅이 호출됨.

✅ 장점: 라우트 전환, 탭 UI 같은 곳에서 **상태 유지** 가능.

❌ 단점: 캐싱이 누적되면 메모리 점유 증가.

## 요약

| 컴포넌트 | 역할 | 주 사용 사례 | 특징 |
| --- | --- | --- | --- |
| **Suspense** | 비동기 컴포넌트 로딩 대기 | 로딩 중 스피너, AsyncComponent | fallback UI 제공 |
| **Teleport** | 다른 DOM 노드에 렌더링 | 모달, 툴팁, 드롭다운 | 부모 상태는 유지, DOM 위치만 이동 |
| **KeepAlive** | 컴포넌트 캐싱/복원 | 탭 전환, 라우트 캐싱 | 상태 유지, activated/deactivated 훅 |
- **`<Suspense>`** → 비동기 로딩 기다리며 fallback 표시
- **`<Teleport>`** → DOM 구조를 이동해 UI 문제 해결
- **`<KeepAlive>`** → 컴포넌트 상태를 캐싱해 성능과 UX 개선

[반응성 원리](SPA%20Framework%20-%20Vue/%EB%B0%98%EC%9D%91%EC%84%B1%20%EC%9B%90%EB%A6%AC%20268cee38e89a80cfad5bd8fb3fc0e6e1.md)

[렌더링 매커니즘](SPA%20Framework%20-%20Vue/%EB%A0%8C%EB%8D%94%EB%A7%81%20%EB%A7%A4%EC%BB%A4%EB%8B%88%EC%A6%98%20268cee38e89a805da4d5fda042dc3607.md)

[최적화 ](SPA%20Framework%20-%20Vue/%EC%B5%9C%EC%A0%81%ED%99%94%2026ccee38e89a80558cc9e9b2e983ed85.md)