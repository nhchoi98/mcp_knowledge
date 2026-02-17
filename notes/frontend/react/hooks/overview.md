---
title: Hooks
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Hooks

# UseState

컴포넌트는 상호 작용의 결과로 화면의 내용을 변경해야 하는 경우가 많습니다. 폼에 입력하면 입력 필드가 업데이트되어야 하고, 이미지 캐러셀에서 “다음”을 클릭할 때 표시되는 이미지가 변경되어야 하고, “구매”를 클릭하면 상품이 장바구니에 담겨야 합니다. 컴포넌트는 현재 입력값, 현재 이미지, 장바구니와 같은 것들을 “기억”해야 합니다. React는 이런 종류의 컴포넌트별 메모리를 *state*라고 부릅니다.

### Reducer를 통해 불필요한 변수 제거는 중요하다.

### 기본구조는 아래와 같이 쌍이다.

> 이 쌍의 이름은 `const [something, setSomething]`과 같이 지정하는 것이 규칙입니다. 원하는 대로 이름을 지을 수 있지만, 규칙을 사용하면 프로젝트 전반에 걸쳐 상황을 더 쉽게 이해할 수 있습니다.
> 

### 다른 방식의 변수 보관과 차이점

- **일반 변수(`let/const`)**: 렌더마다 **다시 초기화**. 값이 바뀌어도 **리렌더 안 됨**. 상태 보관용으로 부적합.
- **`useState`**: 렌더 사이에 값이 **보존**되고, **setter 호출 시 리렌더**. “화면에 보여야 하는 값”의 **단일 출처**.
- **`useRef`**: 렌더 사이에 값 **보존**되지만 **바꿔도 리렌더 안 됨**. DOM 참조나 타이머 ID 같은 **보조 저장소(인스턴스 변수)**.

| 구분 | 일반 변수 | `useState` | `useRef` |
| --- | --- | --- | --- |
| 렌더 간 보존 | X | O | O |
| 값 변경 시 리렌더 | X | O (`setState`) | X (`ref.current = …`) |
| 주용도 | 렌더 내부 계산용 일시 값 | 화면에 보여야 하는 UI 상태 | DOM 핸들/타이머/최근 값 보관 등 “리렌더 불필요한” 값 |
| 초기화 타이밍 | 매 렌더 | 최초 마운트 시 초기값 적용 | 최초 마운트 시 `current` 초기화 |
| 주의점 | 매 렌더 재설정·클로저 갱신 안 됨 | 비동기·배칭됨 → 함수형 업데이트 권장 | 바꿔도 화면이 안 바뀜(표시용으로 쓰지 말 것) |

### 동일 컴포넌트의 인스턴스가 여러개 렌더링 되었더라도, 각 State는 독립적으로 작동한다.

> **State는 격리되고 비공개로 유지됩니다**
> 

> State는 화면에서 컴포넌트 인스턴스에 지역적입니다. 다시 말해, **동일한 컴포넌트를 두 번 렌더링한다면 각 복사본은 완전히 격리된 state를 가집니다!** 그중 하나를 변경해도 다른 하나에는 영향을 미치지 않습니다.
> 

> 이 예시에서 이전에 나왔던 `Gallery` 컴포넌트가 로직 변경 없이 두 번 렌더링되었습니다. 각각의 갤러리 내부 버튼을 클릭해 보세요. 그들의 state가 서로 독립적임을 주목하세요.
> 

### 타이핑 자체가 리렌더를 만드는 게 아니라, `setState`가 리렌더를 만든다.

# (참조: [https://ko.react.dev/learn/state-a-components-memory](https://ko.react.dev/learn/state-a-components-memory))

# UseEffect

(렌더링 된 후, 특정 조건이 만족된다면) props이던 뭐던 렌더링 하고 싶으면 쓰는게 UseEffect 

클린업은 useEffect의 “클린업(cleanup)”은 그 이펙트가 만들어 놓은 ‘바깥 세계의 상태’를 원상복구(해제·중단·닫기)하는 단계예요. 안 하면 중복 구독/타이머 누수/언마운트 후 setState 에러/성능 저하가 생깁니다.

## Effect?

## **Effect란 무엇이고 이벤트와는 어떻게 다른가요?**

Effect에 대해 자세히 알아보기 전에, 컴포넌트 내부의 2가지 로직 유형에 대해 알아야 합니다.

- **렌더링 코드**([UI 표현하기](https://ko.react.dev/learn/describing-the-ui)에 소개됨)를 주관하는 로직은 컴포넌트의 최상단에 위치하며, props와 state를 적절히 변형해 결과적으로 JSX를 반환합니다. [렌더링 코드 로직은 순수해야 합니다.](https://ko.react.dev/learn/keeping-components-pure) 수학 공식처럼 결과만 계산해야 하고, 그 외에는 아무것도 하지 말아야 합니다.
- **이벤트 핸들러**([상호작용 더하기](https://ko.react.dev/learn/adding-interactivity)에 소개됨)는 단순한 계산 용도가 아닌 무언가를 *하는* 컴포넌트 내부의 중첩 함수입니다. 이벤트 핸들러는 입력 필드를 업데이트하거나, 제품을 구입하기 위해 HTTP POST 요청을 보내거나, 사용자를 다른 화면으로 이동시킬 수 있습니다. 이벤트 핸들러에는 특정 사용자 작업(예: 버튼 클릭 또는 입력)으로 인해 발생하는 [“부수 효과”](https://en.wikipedia.org/wiki/Side_effect_(computer_science))(이러한 부수 효과가 프로그램 상태를 변경합니다.)를 포함합니다.

즉, Effect는 순수함수, 이벤트 핸들링은 부수효과를 발생시키는 비순수 함수에 해당됨

(참고: [https://ko.react.dev/learn/synchronizing-with-effects](https://ko.react.dev/learn/synchronizing-with-effects)) 

```jsx
function MyComponent() {
  useEffect(() => {
    // 이곳의 코드는 *모든* 렌더링 후에 실행됩니다
  });
  return <div />;
}
```

→ 클래스형 컴포넌트의 componentDidmount에 기반한 접근법이므로, 가급적 사용을 지양해야함.

# UseCallback

**함수를 메모이제이션**하는 훅입니다. 컴포넌트가 리렌더링될 때마다 함수가 새로 생성되는 것을 방지합니다.

# UseMemo

# UseRef

컴포넌트 인스턴스마다 고유값을 부여함

## useState와의 차이점

| 구분 | `useState` | `useRef` |
| --- | --- | --- |
| 값 보존 | 렌더 간 **보존됨** | 렌더 간 **보존됨** |
| 변경 시 렌더 | **다시 렌더링 발생** | **렌더 안 됨** (그냥 값만 바뀜) |
| 용도 | UI에 **표시/의존**하는 상태(데이터) | 렌더와 무관한 **가변 값** 보관, **DOM 노드** 참조 |
| 형태 | 값 + `setState` | `{ current: T }` 객체 |
| 업데이트 방식 | 비동기 스케줄링(배칭/합쳐짐), **불변성 권장** | 동기적 대입(`ref.current = …`), **가변(mutable)** |
| 어디서 쓰나 | 렌더에 영향 주는 값, 서버/폼 데이터, 토글 등 | 타이머 ID, 이전 값, 외부 인스턴스, 스크롤 위치, 포커스 등 |
| 초기화 타이밍 | 초기값은 **첫 렌더 때만** 사용 | `useRef(init)`의 `init`은 **첫 렌더 때만** 적용, 이후 동일 ref 객체 유지 |

# UseContext

props drilling을 방지하기 위해 사용함 

? 굳이 써야할 이유가 있나

# UseReducer

useState의 심화버전 

# `useState` vs `useReducer`

- **useState**: 단순 필드/토글/숫자 등 **로컬·단순** 상태
- **useReducer**: **액션 중심**으로 상태 변화를 모델링(도메인 로직이 복잡, 전이가 많음)

---

# 베스트 프랙티스 & 주의

- **불변성 유지**: 기존 `state`를 직접 변형하지 말 것
    
    (필요하면 `useImmer`/`useImmerReducer` 같은 도구 고려)
    
- **부수효과는 reducer에서 하지 말기**: `dispatch` 후 `useEffect`에서 처리
- **액션 타입 상수화/유니온**: TS에서 **Discriminated Union**을 쓰면 안전
- **dispatch는 안정적 참조**: 핸들러 props로 내려도 리렌더 유발 안 함
- **에러 상태도 상태로 관리**: `status: 'idle'|'loading'|'success'|'error'` 같이 명시

# 사용자 정의 훅

[특수 페이지들 ](Hooks/%ED%8A%B9%EC%88%98%20%ED%8E%98%EC%9D%B4%EC%A7%80%EB%93%A4%20294cee38e89a80cfbcfedddfca25ded8.md)