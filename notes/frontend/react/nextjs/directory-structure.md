---
title: 디렉토리 구조 예시
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 디렉토리 구조 예시

```jsx
app/
  layout.tsx            // 전체 공통 레이아웃
  (marketing)/          // URL엔 안 보임 (route group)
    page.tsx            // /
    about/page.tsx      // /about
  (app)/
    dashboard/
      layout.tsx        // 대시보드 전용 레이아웃
      page.tsx          // /dashboard
      users/
        loading.tsx     // /dashboard/users 로딩 상태
        page.tsx
  api/
    terms/route.ts      // /api/terms

```