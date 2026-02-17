---
title: FE 테스트 개요
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# FE 테스트 개요

## 계층별 테스트
- 단위(Unit): 함수/훅/작은 컴포넌트
- 통합(Integration): 컴포넌트+데이터 흐름
- E2E: 실제 사용자 시나리오 (Cypress/Playwright)

## 도구 맵
- Jest/Vitest: 단위·통합
- React Testing Library: 사용자 관점 렌더/쿼리
- MSW: 네트워크 모킹(브라우저/Node)
- Cypress/Playwright: 브라우저 자동화 E2E

## MSW 간단 예시
```js
// mocks/handlers.js
import { rest } from 'msw';
export const handlers = [
  rest.get('/user', (_req, res, ctx) => res(ctx.json({ username: 'john.doe' }))),
];
```
```js
// setupTests.js
import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';
const server = setupServer(...handlers);
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## 체크리스트
- [ ] 어떤 계층의 테스트인지 명시
- [ ] 네트워크 의존 시 MSW 등 모킹 적용
- [ ] 사용자 관점 쿼리(스크린 텍스트) 우선
- [ ] E2E는 핵심 경로만 최소화
