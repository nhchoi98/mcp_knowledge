---
title: JSX와 TSX, 그리고 React와의 관계
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# JSX와 TSX, 그리고 React와의 관계

# JSX란?

 **자바스크립트(JavaScript)의 XML(eXtensible Markup Language) 확장 문법**으로, 자바스크립트 코드 내에서 HTML과 유사한 형태로 UI를 작성할 수 있게 해줍니다. 이는 주로 리액트(React)와 함께 사용되며, 자바스크립트와 UI 코드를 통합하여 직관적이고 쉽게 UI를 구성하도록 돕습니다. JSX 자체는 브라우저에서 직접 실행되지 않으며, 바벨(Babel)과 같은 트랜스파일러를 통해 일반 자바스크립트 코드로 변환됩니다. 

JSX도 일종의 표현식으로, 런타임과 컴파일 타임에서 검사가 된다. 

> JSX는 HTML보다는 JavaScript에 가깝기 때문에, React DOM은 HTML 어트리뷰트 이름 대신 `camelCase` 프로퍼티 명명 규칙을 사용합니다.
> 
> 
> 예를 들어, JSX에서 `class`는 [`className`](https://developer.mozilla.org/ko/docs/Web/API/Element/className)가 되고 tabindex는 [`tabIndex`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/tabIndex)가 됩니다.
> 

# TSX란?

- **T**ype**S**cript + **JSX** 문법을 허용하는 파일 형식(.tsx).
- 컴파일될 때 **JSX 표현식 → 함수 호출**로 바뀜(React에선 `jsx()`/`createElement()` 호출).
- **타입 체크**가 된다: 컴포넌트 props, 이벤트 타입, 제네릭까지 안전하게.

# React란?

- **UI 라이브러리**: 상태가 바뀌면 컴포넌트를 다시 렌더하고, 바뀐 부분만 DOM에 커밋하는 역할(리컨실리에이션, 훅스 등).
- 웹에선 `react-dom`이 실제 렌더러, 모바일에선 `react-native`가 렌더러.

# 같이 쓰면 어떤 관계?

- TSX는 **컴파일 타임**에 JSX를 함수 호출로 바꾸고 타입을 확인.
- React는 **런타임**에 그 호출 결과(가상 노드)를 받아 **화면에 반영**.
- 그래서 흔히 “**React + TSX**” 조합을 씀.

# 서로 없이도 가능?

- **React ⭕, TSX ❌**: JSX 없이도 가능.