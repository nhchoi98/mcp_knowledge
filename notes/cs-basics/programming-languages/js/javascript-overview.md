---
title: JavaScript 개요
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# JavaScript 개요

## ECMAScript vs JavaScript
- **ECMAScript**: 언어 표준(ES2015+ 등)
- **JavaScript**: ECMAScript + 호스트 API(브라우저/Node)

## 값과 타입
- 원시(불변): string, number, boolean, null, undefined, symbol, bigint
- 참조(가변): object/array/function 등
- 비교는 `===` 기본, `==` 지양

## 스코프·this·호이스팅
- 렉시컬 스코프, 블록 스코프(let/const), 함수 스코프(var)
- 실행 컨텍스트가 선언/this를 관리, 콜 스택으로 실행
- 호이스팅: 선언은 끌어올려지지만 let/const는 TDZ, 함수 선언은 전체 호이스팅

## 함수
- 선언식/표현식/화살표: this·arguments·호이스팅 차이
- 고차함수/메서드 체이닝/콜백 → Promise/async로 단순화

## 비동기와 이벤트 루프
- 태스크 큐(타이머/IO) vs 마이크로태스크(Promise/await)
- async/await + try/catch로 에러 관리, 필요 시 finally/AbortController

## 모듈
- ES Modules: `import/export`(정적, 트리쉐이킹 친화)
- CommonJS: `require/module.exports`(동적, 레거시)

## 체크리스트
- [ ] 원시/참조 구분 및 얕은/깊은 비교 주의
- [ ] 스코프/this/호이스팅 규칙 이해
- [ ] 비동기 흐름에서 마이크로태스크 우선순위 고려
- [ ] 모듈 시스템 일관성 유지(ESM 우선)
