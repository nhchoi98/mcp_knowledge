---
title: React
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# React

# 핵심 키워드

JSX, Virtual DOM, React fiber, Fiber Tree, Transpile, Reconciliation, 함수형 컴포넌트, 클래스형 컴포넌트, 렌더와 커밋, 동시성 렌더링, 메모이제이션, React hooks, context, Flux 패턴, shouldComponentUpdate, getChildContext, hook

# 참고 사이트

[https://d2.naver.com/helloworld/2690975](https://d2.naver.com/helloworld/2690975)

# React란?

### 1. 컴포넌트(Component) 기반의 개발

React의 가장 큰 특징은 UI를 **'컴포넌트'**라는 작은 단위로 쪼개서 관리한다는 점입니다.

- **재사용성:** 한 번 만든 버튼, 입력창, 네비게이션 바 등을 다른 페이지에서도 그대로 가져다 쓸 수 있습니다.
- **유지보수:** 코드가 레고 블록처럼 나누어져 있어, 특정 부분에 문제가 생기면 그 부분만 수정하면 됩니다.

### 2. 가상 DOM (Virtual DOM)을 통한 빠른 성능

일반적으로 웹 페이지의 요소(DOM)를 직접 수정하는 작업은 비용이 많이 들고 속도가 느립니다. React는 이 문제를 **가상 DOM**으로 해결합니다.

- 데이터가 바뀌면 실제 화면을 바로 바꾸는 게 아니라, 가상의 화면을 먼저 만듭니다.
- 이전 상태와 비교해서 **정말 바뀐 부분만** 골라 실제 화면에 적용합니다. 이 덕분에 사용자에게 훨씬 부드러운 경험을 제공합니다.

### 3. 선언적(Declarative) 프로그래밍

기존의 방식이 "어디로 가서, 무엇을 어떻게 바꿔라"라고 일일이 명령하는 방식(명령형)이었다면, React는 **"화면이 이 상태일 때는 이렇게 보여라"**라고 정의만 하면 됩니다.

- 상태(State)에 따라 UI가 어떻게 변할지 미리 선언해두기 때문에 코드가 훨씬 예측 가능하고 디버깅이 쉬워집니다.

### 4. 강력한 생태계와 커뮤니티

React는 메타(Facebook)에서 관리할 뿐만 아니라 전 세계적으로 가장 많은 개발자가 사용합니다.

- **풍부한 라이브러리:** 이미 만들어진 도구들이 많아 개발 속도가 매우 빠릅니다.
- **React Native 확장성:** React를 배우면 모바일 앱(iOS, Android)을 만드는 'React Native'로 쉽게 넘어갈 수 있습니다.
- **구인 구직:** 시장 수요가 압도적으로 많아 커리어 측면에서도 유리합니다.

# React의 중요 개념

Vue가 “미세한 **Reactivity(의존 추적 + 이펙트 스케줄링)**”를 핵심으로 삼는다면, React는 아래 **4축**이 핵심이에요.

1. **컴포넌트 & 선언적 UI**
    
    상태(state)와 props만으로 UI를 **선언**하면 React가 렌더-커밋 과정을 수행.
    
2. **단방향 데이터 흐름(Props ↓, Events ↑)**
    
    상위 → 하위로 데이터, 하위 → 상위로 이벤트 콜백. 예측 가능한 상태 관리가 가능.
    
3. **재조정(Reconciliation) / Fiber**
    
    변경 신호가 오면 **가상 트리 비교**로 필요한 곳만 업데이트. React 18은 우선순위·중단 가능한 작업 등 **스케줄링**을 포함.
    
4. **Hooks**
    
    함수형 컴포넌트에서 상태/부수효과/메모이제이션을 **조합**하는 핵심 API 세트(`useState`, `useEffect`, `useMemo`, `useCallback`, `useRef`, `useReducer`, `useTransition` 등).
    
    1. React Element
    
    React 앱의 가장 작은 단위입니다.
    
    엘리먼트는 화면에 표시할 내용을 기술합니다.
    
    여기서, 엘리먼트는 불변객체이다.
    

React에서는 [렌더링이 JSX의 순수한 계산](https://ko.react.dev/learn/keeping-components-pure)이어야 하며, DOM 수정과 같은 부수 효과를 포함해서는 안됩니다.

# Vue와 비슷한 개념

| Vue 개념 | 대표 API | React에서 대응/생각법 |
| --- | --- | --- |
| **반응성(reactivity) 시스템** | `ref()`, `reactive()` | **state 기반 재렌더**: `useState`, `useReducer` (값이 바뀌면 컴포넌트가 다시 렌더됨). 미세한 의존성 추적은 안 하고, 변경 신호를 **개발자가 명시적으로** 보냄(`setState`). |
| **computed(파생값 캐시)** | `computed(getter)` | **`useMemo`**: 비싼 계산/참조 동일성 유지가 필요할 때만 메모이즈. 값이 가볍다면 **렌더 중 즉시 계산**이 기본. |
| **watch / watchEffect(부수효과/구독)** | `watch(source, cb)`, `watchEffect(cb)` | **`useEffect`**: 의존성 배열을 **명시**해 언제 실행할지 제어. `watchEffect`의 “자동 의존 추적”과 달리, React는 **배열로 의존을 쓰는** 쪽을 권장. |
| **템플릿/지시자** | SFC 템플릿, `v-if`, `v-for` | **JSX/TSX**: JS/TS 표현식으로 UI를 선언. 조건부는 `if`/조기리턴/`&&` 등으로 구성(삼항 피하고 싶다면 조기 리턴 패턴 추천). |
| **반응형 참조** | `ref.value` | **`useRef`**: 변경돼도 **렌더를 트리거하지 않는** “박스”. DOM 접근/이전 값 보관에 사용. 값 변경로 UI 갱신하려면 `useState`를 써야 함. |

# React에서의 “파생 상태” 다루기 요령

- **가능하면 파생값은 저장하지 말고 계산**하세요. (소스: props/state → 파생: 합계/필터 결과)
- 정말 비용이 크거나 **참조 동일성**(메모이즈된 하위 컴포넌트 prop 유지)이 중요한 경우에만 **`useMemo`*를 사용.
- 리스트 핸들러 등 콜백은 **`useCallback`*으로 메모이즈해 불필요한 리렌더를 줄일 수 있음.

# **TSX 확장자**

**TSX = TypeScript + JSX**.

JSX 문법으로 UI를 적되 **타입 안전성**을 얻습니다. 컴포넌트 props/이벤트/제네릭까지 타입 검사 가능.

# 렌더링이 일어나는 조건

<함수형 렌더링의 반환값인 return을 평가함>

- useState의 setter가 실행되는 경우
- useReducer의 dispatch가 실행되는 경우
- key props가 변경되는 경우
- 부모의 props가 변경된 경우 → memo로 회피 가능

# 렌더와 커밋

- type, props, key가 변경되면 렌더 단계를 거침
- 커밋 단계에서는 렌더단계의 변경 사항을 실제 DOM에 적용함 → useLayoutEffect 훅을 호출

# Hook의 정의

Hook은 함수 컴포넌트에서 *React state와 생명주기 기능(lifecycle features)을 “연동(hook into)“할 수 있게 해주는 함수*이다

- **mutation** 이란, 서버에 Side-Effect 를 일으키도록 하는 함수다. 인계 받은 쿼리 값을 기반으로 새로운 결과를 도출하여 서버에 변경 사항을 적용하도록 요청하는 기능을 한다.
- 보통 **POST, PUT, DELETE** 같이 데이터를 수정하거나 추가하는 요청을 보낼 때 같이 사용되며, react-query 에서는 관련 작업을 위해 useMutation 훅을 지원한다.
- **목록/상세 조회, 검색 결과, 언어 리스트, 용어집 리스트…**
    - → `useXxxQuery` (React Query의 `useQuery`)
- **용어집 생성 / 수정 / 삭제, 상태 토글, 승인/거절 같은 액션**
    - → `useXxxMutation` (React Query의 `useMutation`)

# Mutator 역할

React에서

```
mutation
```

은**서버의 데이터를 생성, 수정, 삭제하는 역할**을 합니다.

[useMutation](https://www.google.com/search?q=useMutation&client=firefox-b-d&sca_esv=2286498253ea9ec4&sxsrf=AE3TifMSP8lIWhkk1FaJvRc_LXMzSrtCKA%3A1762927038159&ei=viEUaYWyCZ2P2roPgtaEoAk&ved=2ahUKEwie05KD9-uQAxWjgFYBHZ1rOCgQgK4QegQIARAC&uact=5&oq=react+mutation+%EC%97%AD%ED%95%A0&gs_lp=Egxnd3Mtd2l6LXNlcnAiFXJlYWN0IG11dGF0aW9uIOyXre2VoDIIEAAYgAQYogQyCBAAGIAEGKIEMgUQABjvBTIIEAAYgAQYogQyBRAAGO8FSPQOUBxY2A1wBXgBkAEAmAHFAaABjA2qAQMwLjm4AQPIAQD4AQGYAgegApsDwgIKEAAYsAMY1gQYR8ICCBAAGKIEGIkFmAMAiAYBkAYKkgcDNS4yoAfpGrIHAzAuMrgHgAPCBwMyLTfIBx4&sclient=gws-wiz-serp&mstk=AUtExfAU-aS44I7zC0dcm-Se8d3XQolXciNkeEha5QzL1sbtO8mimyxF_XftH6mGQsqVUyDyfKCv66QkeraLh7f_3XzJT9Yi2HJseAaw3VpNNx508GS1fOQt0GipaYQatRv894WPAV539ycSFC2oIU_adVTV31T1_01W9hmD3iczKs2t2jp83rHVb-urMednRfpWFLBl0QoH_wy6iTo957f9dA0PoJbgGRvpTyrypVTtW6tcaIZwBWfPkVEClbgdPG6AOzy45EKvfsDujHhqIX_ziphS&csui=3)훅을 사용하여 서버로 데이터를 변경하는 네트워크 요청을 보내는 데 사용되며, 이는

```
useQuery
```

가 데이터를 읽기(read)만 하는 것과 달리, 쓰기(write) 작업을 처리합니다

[상태관리](React/%EC%83%81%ED%83%9C%EA%B4%80%EB%A6%AC%2028ccee38e89a809793c4db10a935b568.md)

[Next.js](React/Next%20js%2028ccee38e89a80a89d4cc822bf2e5825.md)

[Design framework](React/Design%20framework%2028ccee38e89a808196a8fd35ccbad5c7.md)

[Hooks ](React/Hooks%2028ccee38e89a805d9a2df3be364432e2.md)

[ Vue와 비교 ](React/Vue%EC%99%80%20%EB%B9%84%EA%B5%90%2028ccee38e89a80208adbd048176062f7.md)

[최적화 ](React/%EC%B5%9C%EC%A0%81%ED%99%94%2028dcee38e89a80d28b90ec19143f47a5.md)

[JSX와 TSX, 그리고 React와의 관계 ](React/JSX%EC%99%80%20TSX,%20%EA%B7%B8%EB%A6%AC%EA%B3%A0%20React%EC%99%80%EC%9D%98%20%EA%B4%80%EA%B3%84%2028dcee38e89a805a9f5bf8ffb51b29ca.md)

[Flux 패턴](React/Flux%20%ED%8C%A8%ED%84%B4%20299cee38e89a80aa9fa8f11f2c69a98e.md)

[Best practice](React/Best%20practice%20299cee38e89a8086b69ae3fae6406283.md)

[MSW (Mock service worker) ](React/MSW%20(Mock%20service%20worker)%2029acee38e89a80cab35dced61ff88232.md)

[Zustand ](React/Zustand%202a7cee38e89a805f9e3fdaf765760ad9.md)

[tanstack query](React/tanstack%20query%202a9cee38e89a80e8992dfb3e371e68d4.md)

[Vercel의 최적과 agent 분석](React/Vercel%EC%9D%98%20%EC%B5%9C%EC%A0%81%EA%B3%BC%20agent%20%EB%B6%84%EC%84%9D%202edcee38e89a80bcb067cf971e2a7d71.md)

[Render](React/Render%202edcee38e89a8040add1e47802d694ba.md)

[Context API ](React/Context%20API%202eecee38e89a808fa97ada55cb5a36f5.md)

[렌더링 파이프라인](React/%EB%A0%8C%EB%8D%94%EB%A7%81%20%ED%8C%8C%EC%9D%B4%ED%94%84%EB%9D%BC%EC%9D%B8%202eecee38e89a80e384c1d30c1762b6b0.md)

[React compiler](React/React%20compiler%202eecee38e89a801b898ff0ac53b943cc.md)