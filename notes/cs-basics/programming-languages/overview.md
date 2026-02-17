---
title: 프로그래밍 언어 개요
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 프로그래밍 언어 개요

프론트엔드 중심으로 JS/TS 핵심만 요약했습니다.

## JS ↔ TS 한눈에 보기
- **JS**: 동적 타입, 인터프리터(JIT) 언어, 런타임 결정
- **TS**: 정적 타입 + JS 상위집합, 컴파일 단계에서 타입 검증
- 선택 가이드: 빠른 실험/런타임 유연성 → JS, 협업/리팩토링 안전성 → TS

## 실행 모델 핵심
- **실행 컨텍스트**: 스코프, this, 선언을 담는 박스 (콜 스택으로 관리)
- **메모리**: 스택(원시), 힙(객체 참조)
- **이벤트 루프**: 태스크 큐(타이머/IO) vs 마이크로태스크(Promise/await)

## 타입/비교 요약
- 원시값: 불변(문자열/숫자/불리언/null/undefined/symbol/bigint)
- 객체: 참조·가변, 얕은/깊은 비교 유의
- 비교: `===` 기본, `==` 지양

## 함수/모듈
- 선언식/표현식/화살표: this·호이스팅 차이
- 고차함수, 메모이제이션, 합성 활용
- ES Modules(`import/export`) 기본, CommonJS 레거시

## 비동기/이터러블
- Promise → async/await로 단순화, 에러는 try/catch
- 마이크로태스크 우선 처리, 장기 작업은 분할/지연
- Iterable/Iterator 프로토콜: `for...of`, 전개, `function*` 제너레이터

## 참고
- [JavaScript 개요](js/javascript-overview.md)
