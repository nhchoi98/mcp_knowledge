---
title: Frontend
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Frontend

## 카테고리

- browser: 브라우저 동작, 스토리지, iframe 등
- css: CSS/SCSS, 레이아웃
- rendering: CSR/SSR/SSG 등 렌더링 모드, 최적화
- react: 개요, 상태관리, hooks, render, Next.js
- vue: Vue 개요/반응성/최적화
- testing: FE 테스트, MSW
- web-essentials: SEO, 라우팅, 데이터 전송 등

## 이름/슬러그 규칙

- 소문자 영문-하이픈 조합 권장 (예: `browser-basics.md`, `react-rendering-overview.md`)
- 중복 주제는 canonical 파일로 병합 후 `Merged from ...` 섹션 추가

## 내부 링크

- 동일 카테고리 내: `./subdir/file.md`
- 다른 카테고리: `../<category>/.../file.md`

## TOC

- browser/
  - [browser-basics](browser/browser-basics.md)
  - [storage](browser/storage.md)
  - [iframe](browser/iframe.md)
  - [web-platform-interface](browser/web-platform-interface.md)
- css/
  - [css-overview](css/css-overview.md)
  - [layout](css/layout.md)
  - [scss](css/scss.md)
- rendering/
  - [rendering-overview](rendering/rendering-overview.md)
  - [csr](rendering/csr.md)
  - [rendering-optimization](rendering/rendering-optimization.md)
  - [rendering-modes](rendering/rendering-modes.md)
  - [html-rendering-optimization](rendering/html-rendering-optimization.md)
- react/
  - overview/
    - [jsx-tsx](react/overview/jsx-tsx.md)
    - [best-practices](react/overview/best-practices.md)
    - [design-framework](react/overview/design-framework.md)
  - state-management/
    - [overview](react/state-management/overview.md)
    - [redux-prompts](react/state-management/redux-prompts.md)
    - [pinia-redux-overview](react/state-management/pinia-redux-overview.md)
    - [tanstack-query](react/state-management/tanstack-query.md)
    - [zustand](react/state-management/zustand.md)
  - hooks/
    - [overview](react/hooks/overview.md)
    - [special-pages](react/hooks/special-pages.md)
  - render/
    - [react-rendering-overview](react/render/react-rendering-overview.md)
    - [react-rendering-pipeline](react/render/react-rendering-pipeline.md)
    - [i18n-rendering-optimization](react/render/i18n-rendering-optimization.md)
    - [vercel-optimizer-agent](react/render/vercel-optimizer-agent.md)
  - nextjs/
    - [overview](react/nextjs/overview.md)
    - [routing](react/nextjs/routing.md)
    - [directory-structure](react/nextjs/directory-structure.md)
- vue/
  - [overview](vue/overview.md)
  - [reactivity](vue/reactivity.md)
  - [optimization](vue/optimization.md)
  - [vue-vs-react](vue/vue-vs-react.md)
- testing/
  - [overview](testing/overview.md)
  - [msw](testing/msw.md)
  - [jest-vitest](testing/jest-vitest.md)
- web-essentials/
  - [seo](web-essentials/seo.md)
  - [router](web-essentials/router.md)
  - [html-data-transfer](web-essentials/html-data-transfer.md)
