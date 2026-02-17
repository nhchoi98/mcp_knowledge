---
title: 상태관리 (Pinia, Redux)
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 상태관리 (Pinia, Redux)

# 사용 이유

### 1. **컴포넌트 간 상태 공유의 불편함**

### 2. **전역 상태 관리 필요성**

## 일관성 문제

- 여러 컴포넌트가 같은 데이터를 따로따로 관리하면, 값이 서로 달라질 수 있음.
- 예: 헤더에 표시된 장바구니 수량과 장바구니 페이지의 아이템 수량이 다르면 안 됨.

## **비동기 처리 난이도**

- API 요청으로 상태를 바꾸는 경우(로그인, 장바구니 업데이트 등) → 상태 변경 흐름을 추적하기 어려움.
- “어디서 상태가 바뀌었지?”를 알 수 없으면 디버깅 어려움.

# Pinia

- Vue 3 공식 상태 관리 라이브러리 (Vuex 후속)
- Composition API 친화적
- **가벼움 + 타입스크립트 호환성**이 강점
- **Store 기반 구조**
    - `defineStore()`로 상태 저장소(store)를 정의
    - 각 store는 state, getter, action을 가짐
- **TypeScript 친화적**
    - 자동으로 타입 추론 지원
- **반응성 활용**
    - Vue의 반응성 시스템(Reactivity API)을 그대로 사용 → 직관적
- **간단한 사용법**

## Vuex 대신 사용하는 이유

| 항목 | Vuex | Pinia |
| --- | --- | --- |
| 상태 변경 방식 | **Mutation** 필수 (commit) | 직접 state 변경 (actions 안에서 가능) |
| 코드량/보일러플레이트 | 많음 (mutation/action 구분) | 적음 (mutation 제거, 직관적) |
| TS 호환성 | 약함, 타입 정의 불편 | 강함, 자동 추론 지원 |
| Vue 버전 | Vue 2/3에서 사용 가능 | Vue 3 권장 공식 상태 관리 |
| 학습 난이도 | 상대적으로 높음 (패턴 엄격) | 낮음 (Composition API와 유사) |
| DevTools | Vue Devtools 통합 지원 | Vue Devtools (v6)와 통합, 더 가볍고 직관 |