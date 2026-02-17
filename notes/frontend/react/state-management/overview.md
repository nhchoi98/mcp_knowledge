---
title: 상태관리 개요
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 상태관리 개요

## 선택 가이드
- 전역 상태: RTK/Redux, Zustand
- 서버 상태: TanStack Query (데이터 패칭/캐싱)
- 라우팅/도메인 의존 낮을 때: Context + reducer

## 공통 원칙
- 단일 진실 원천 유지, 상태는 read-only → 액션/업데이트 함수로만 변경
- 불변성 유지(Immer/RTK 기본 제공), 참조 안정성 관리
- 셀렉터/메모이제이션으로 리렌더 최소화

## Redux 핵심 흐름 (RTK 권장)
- Store 구성: `configureStore`
- Slice: `createSlice`로 상태+리듀서+액션 묶음
- Dispatch 흐름: action → reducer → new state
- Middleware: thunk 기본, 로깅/에러/측정 추가 가능
- Selector: `useSelector`, `createSelector`로 파생 상태

## Zustand 스냅샷
- 보일러플레이트 적음, action 정의 자유도가 높음
- selector + shallow로 리렌더 최소화

## TanStack Query 스냅샷
- 서버 데이터 패칭/캐싱/동기화 담당
- 캐시 키, stale-time, prefetch 전략 설계

## 실무 체크리스트
- [ ] 전역/서버/로컬 상태 역할 분리
- [ ] 불변성·참조 안정성 확인
- [ ] 선택적 구독/셀렉터 적용
- [ ] 코드 스플리팅/RTK Query 여부 검토
- [ ] DevTools/로깅으로 흐름 검증

## 관련 문서
- [Redux 설계 프롬프트](redux-prompts.md)
- [Pinia/Redux 비교](pinia-redux-overview.md)
- [Zustand](zustand.md)
- [TanStack Query](tanstack-query.md)

## Thunk

"thunk" is a programming term that means ["a piece of code that does some delayed work"](https://en.wikipedia.org/wiki/Thunk).

일반적으로 reducer는 sync function만 사용가능하다.

그래서 API에서 데이터를 불러오는 기능을 reducer로 구현하려고 하면 구현할 수 없다. (API에서 데이터를 불러오기 위해서는 asyncronous하게 구현해야하기 때문)

이를 위해 제공되는 것이 `createAsyncThunk` 이다.

`createAsyncThunk`는 action type과 콜백 함수를 받아 Promise를 반환하는 함수이다.

> **Why Client Components?**
> 
> 
> Any component that interacts with the Redux store (creating it, providing it, reading from it, or writing to it) needs to be a client component. This is because **accessing the store requires React context, and context is only available in client components.**
> 

## 비동기 처리 및 구성

### 핵심 keyword

Thunk, middleware, action, slice, state 

"thunk" is a programming term that means ["a piece of code that does some delayed work"](https://en.wikipedia.org/wiki/Thunk).

이를 위해 제공되는 것이 `createAsyncThunk` 이다.

`createAsyncThunk`는 action type과 콜백 함수를 받아 Promise를 반환하는 함수이다.

# Recoil

[Redux 설계 프롬프트 ](%EC%83%81%ED%83%9C%EA%B4%80%EB%A6%AC/Redux%20%EC%84%A4%EA%B3%84%20%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8%2029acee38e89a807a886ad5a19941fc12.md)
