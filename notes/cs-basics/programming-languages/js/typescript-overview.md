---
title: Typescript
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Typescript

## TypeScript를 도입하는 이유는 무엇인가요?

TypeScript를 도입하는 가장 큰 이유는 **정적 타입 검사**

를 통해 런타임 에러를 줄이고, IDE 지원을 통해 **개발 생산성과 유지보수성** 을 높일 수 있기 때문입니다. 특히 대규모 프로젝트나 여러 명이 협업하는 환경에서는 코드의 안정성과 일관성을 보장할 수 있어서 효과적입니다.

# 타입 검사(type checking)

**타입 검사**란, 어떤 심벌에 대한 각종 대입/참조/연산이 가능한지 확인하는 과정입니다. 어떻게 보면 자동 증명이라고 할 수 있는데요. 단순히 증명에서 그치는 것이 아니라, 구체적으로 어떤 맥락 하에 심벌이 가질 수 있는 타입은 무엇인지도 찾아냅니다(예: 타입 가드를 수행한 if문 블록, IDE 자동 완성).

학술적으로 이는 [**제약 충족 문제**(Constrained Satisfaction Problem, CSP)](https://en.wikipedia.org/wiki/Constraint_satisfaction_problem)의 일종입니다. 그러나 이 문제는 NP-완전(NP-complete)하기 때문에, 현실적으로 컴파일러가 풀기엔 너무 어려운 문제입니다. 따라서 tsc는 그리디(greedy)한 알고리즘을 구현한 것으로 추정됩니다(실제로 지수 복잡도 케이스를 테스트해보면, 백트래킹을 하지 않는다는 것을 알 수 있습니다).

### 타입 검사는 증명이다

tsc는 개발자가 입력한 소스 코드를 **기반 지식**(knowledge base)으로 사용합니다. 즉, 엉터리 타입을 주거나 엉터리 대입을 하더라도 그것을 참인 명제로 간주합니다. 대신 그 소스 코드를 정적 분석하면서 모순이 발생할 경우, tsc에 내재하는 사실은 참이므로 소스 코드에 오류가 있다고 결론을 내죠.

예를 들어, 다음과 같은 간단한 상수 선언문이 있다고 생각해 봅시다.

# Typescript

## Typescript에 존재하는 기본 타입은?

- 원시타입 (Primitive type) + **void**
- 객체타입(Object Type)
- tuple, enum도 추가적으로
- 특수타입 (any, unknown, never)

## Union type

자바스크립트에서 꽤 흔하게 하나의 속성에 다수의 타입을 정의합니다.

- `|` (vertical bar, 파이프) 기호를 사용해서 여러 타입을 **합집합(union)**처럼 묶습니다.
- 즉, *“이 변수는 A 타입이거나 B 타입일 수 있다”*라고 선언하는 것.

## Intersection Type

두개의 객체를 가져와서 두 객체의 기능을 모두 갖춘 새로운 객체를 만듭니다.

## Typescript 에서 null과 undefined 의 처리

strictNullCheck:false 컴파일러 설정을 통해서 처리 어떻게 할지 결정.

null과 undefined는 해당 설정이 ture일 때 다르게 처리됨 

## Typescript 기본 타입

### `any`, `unknown`, `never` 타입의 차이는 무엇인가요?

```
any
```

는 타입 체크를 포기하고 모든 값을 허용하는 타입이라,

안전성은 떨어지지만 빠른 개발엔 유용합니다.

```
unknown
```

은 값이 뭔지 아직 모르지만, 타입 가드를 통해 안전하게 좁혀서 사용할 수 있습니다.

```
never
```

는 발생할 수 없는 값의 타입으로, 주로 에러 처리 함수나 타입 좁히기에서 모든 경우를 처리했는지 검사할 때 활용합니다

## 🟡 `any`

- **가장 유연한 타입** → 어떤 값이든 들어올 수 있음
- 타입 체크를 **아예 포기**하겠다는 의미
- 컴파일러가 에러를 잡아주지 않음 (JS처럼 동작)

## 🟢 `unknown`

- `any`와 달리, **값을 알 수 없다는 걸 명시적으로 표현**
- 하지만 사용하려면 **타입을 좁히거나(타입 가드)** 캐스팅해야 함

## 🔴 `never`

- **절대 발생할 수 없는 타입**
- 보통 함수가 **끝까지 실행될 수 없는 경우**에 사용

## Type guard란?

런타임에서 값의 타입을 좁혀서(`narrowing`) TypeScript 컴파일러가 **보다 정확한 타입 추론을 하게 하는 기법**이에요. 즉, **Type Guard는 “이 조건 안에서는 이 타입이 확실하다”라고 컴파일러에게 알려주는 장치**예요.
컴파일러가 코드 실행 흐름을 분석해서, 특정 분기 내에서 변수의 타입을 더 정확하게 추론할 수 있게 만들어 줍니다.

즉, `any`, `unknown`, `union` 같은 넓은 타입에서 → **조건문** 등을 통해 특정 타입으로 제한하는 것.

## 🔹 기본 개념

- TypeScript는 **유니언 타입(union type)** 등을 사용할 때, 변수의 실제 타입이 무엇인지 확실하지 않을 수 있습니다.
- **Type Guard**는 특정 조건문(`if`, `switch`, `typeof`, `instanceof`, 사용자 정의 함수 등)을 사용해서 타입을 좁혀주는 문법/기술입니다.
- 이렇게 좁혀진 타입은 조건문 블록 안에서만 유효합니다.

## Type alias란?

**Type alias는 타입에 새로운 이름을 붙여주는 문법**입니다.

말 그대로 **별칭(alias)**을 만드는 거라, 객체 구조뿐만 아니라 **유니온, 인터섹션, 튜플, 리터럴 타입**

등 다양한 타입을 표현할 수 있습니다.

## Type inference (타입 추론)이란?

Type inference는 TypeScript가 명시적인 타입 선언이 없어도,

변수에 할당된 값이나 함수 반환값, 혹은 문맥을 기반으로 타입을 자동으로 결정하는 기능입니다.

예를 들어 let x = 10

이라고 하면 TS는 자동으로 x: number 로 추론합니다.

이렇게 해서 불필요한 타입 선언을 줄이면서도 타입 안정성을 유지할 수 있습니다

명시적으로 타입을 지정하지 않아도, **TypeScript 컴파일러가 변수/함수의 타입을 자동으로 결정하는 기능**입니다. (함수 반환형도, 문맥적 추론도함)

## Interface란?

TypeScript에서 interface 는 객체의 구조를 정의하는 타입 시스템입니다.

속성과 메서드를 명세해서, 객체나 클래스가 그 규격을 따르도록 강제할 수 있습니다.

특히 extends 로 확장하거나, implements 로 클래스와 결합할 수 있고,

같은 이름으로 여러 번 선언하면 자동으로 병합되는 특징이 있습니다.

그래서 주로 객체 구조 정의나 라이브러리의 API 스펙을 표현할 때 많이 사용합니다

## Interface와 Type alias의 차이는 무엇인가요?

interface와 type alias 는 객체 구조를 정의할 때 모두 사용할 수 있습니다.

다만, interface 는 **상속과 선언 병합이 가능** 해서 확장성이 좋고, type은 **union, tuple 같은 복잡한 타입 표현** 에 더 유리합니다. (Interface는 속성 구조 정의만 가능하므로, type Status = “Success” | “error” | “loading” 이런거 표현이 불가함) 

그래서 저는 객체 구조나 라이브러리 API 정의에는 interface 를, 유니온 타입이나 조합이 필요한 경우에는 type을 주로 사용합니다.

## 🟡 공통점

- `interface`와 `type alias` 둘 다 **객체의 형태(Shape)**를 정의할 수 있음
- 함수 타입, 객체 타입, 클래스 구현체 등에서 활용 가능

## 🟢 차이점

### 1. **확장(extends) 방식**

- **interface**는 `extends`로 상속 가능
- **type**은 `&`(intersection)으로 확장

### 2. **선언 병합(Declaration Merging)**

- `interface`는 같은 이름으로 여러 번 선언하면 **자동 병합**됨
- `type`은 동일 이름으로 재선언 불가능 (에러 발생)

## 구조적 타이핑(Structural typing)이 무엇인지 아나요?

TypeScript는 구조적 타이핑을 사용하기 때문에, 타입 이름이 같을 필요 없이 **속성과 형태가 같으면 호환됩니다.**

예를 들어, Person 타입을 기대하는 함수에 {name, age} 속성을 가진 객체라면Person으로 간주됩니다.이 덕분에 JavaScript와 호환성이 좋고 유연하지만, 때로는 원치 않는 타입 호환이 일어나서 주의가 필요합니다.

타입의 **이름이 아니라 구조(Shape, 속성과 메서드 형태)**에 따라 타입 호환 여부를 판단하는 방식입니다.

- TypeScript는 **구조적 타이핑 언어**
- Java나 C#처럼 이름으로만 타입을 구분하는 **명목적 타이핑(Nominal Typing)**과 대비됨

## Optional이란?

**객체 속성이나 함수의 매개변수가 있을 수도 있고 없을 수도 있음을 나타내는 것**을 의미합니다. ?를 이용해 표현합니다. 

## Generic이란?

제네릭(Generic)**은

**타입을 함수나 클래스, 인터페이스에 매개변수처럼 전달할 수 있는 기능**입니다.

즉, 값이 아니라 **타입에 대한 파라미터** 를 받는다고 보면 돼요.

이를 통해 **재사용성**과 **타입 안정성**을 동시에 확보할 수 있습니다.

## keyof, typeof, in 같은 키워드를 활용한 타입 프로그래밍 예시를 들어보세요.

keyof는 객체 타입에서 키를 뽑아 유니온 타입으로 만들 때 쓰이고, typeof 는 값에서 타입을 추출할 때 사용합니다. in 은 매핑된 타입을 만들 때 활용해서, keyof 로 뽑은 키들에 대해 반복적으로 타입을 정의할 수 있습니다. 예를 들어 typeof config 로 객체 타입을 뽑고, keyof 로 키 유니온을 만든 뒤,

in 을 이용해 readonly버전의 타입을 자동으로 생성할 수 있습니다.”

## Partial<T>, Pick<T, K>, Omit<T, K> 같은 유틸리티 타입을 설명해보세요.

- `Partial<T>` → 모든 속성을 **옵션 처리**
- `Pick<T, K>` → 일부 속성만 **선택**
- `Omit<T, K>` → 일부 속성만 **제외**

### Partial<T>

 `T`의 모든 속성을 **선택적(optional)**으로 바꿉니다.

## `Pick<T, K>`

👉 `T`에서 `K` 속성만 뽑아온 새로운 타입을 만듭니다.

`Omit<T, K>`

`T`에서 `K` 속성을 **제외**한 새로운 타입을 만듭니다.

## Gradual Typing

- **필요할 때만 타입을 지정할 수 있는 방식**.
- 기본적으로 동적 타입처럼 자유롭게 쓰다가, 중요한 부분에는 타입을 명시해서 **안전성을 보강**할 수 있음.

# Infer Keyword

**`infer`는 조건부 타입 안에서 새로운 타입 변수를 선언하고 추론하게 해주는 키워드**예요.

주로 **배열 원소 타입 추출, Promise 결과 타입 추출, 라이브러리 스키마 타입 변환** 등에 활용돼요.

```jsx
type ElementType<T> = T extends (infer ArrayElement)[] ? ArrayElement : T
```

---

### 조건부 타입(conditional type)

조건부 타입이란 제네릭 정의문에서 특정 타입이 다른 타입의 서브타입인지 확인한 뒤 분기하는 구문입니다. `infer`와 밀접한 연관이 있습니다.

```tsx
type IsNever<T> = [T]extends [never] ? true : false
```

# 확장 버전 (더 범용)

배열뿐 아니라 **이터러블 전반**에서 원소 타입을 뽑고 싶다면:

```tsx
type ElementOfIterable<T> =
  T extends Iterable<infer R> ? R : never;

type A = ElementOfIterable<Set<number>>;     // number
type B = ElementOfIterable<Map<string, boolean>>; // [string, boolean]
type C = ElementOfIterable<string[]>;        // string

```

[https://d2.naver.com/helloworld/3713986](https://d2.naver.com/helloworld/3713986)

# Extend 키워드의 역할

### (1) 클래스/인터페이스 문맥

👉 우리가 익숙한 "상속"의 의미

### (2) 제네릭 조건부 타입 문맥

👉 "타입 제약" 또는 "조건 검사"의 의미

```

```

# `keyof`

- 객체 타입의 **모든 키(key)를 유니온 타입으로 추출**.

# `satisfies`

- TS 4.9에 도입된 키워드.
- 값이 특정 타입 **제약을 만족하는지 검사하면서**,
- 동시에 값의 구체적 타입 정보는 잃지 않음.

# IN

- `K in keyof T`
    
    👉 `T` 타입의 모든 키(`keyof T`)를 하나씩 꺼내와서 **순회(iterate)**
    
- `T[K]`
    
    👉 그 키에 해당하는 값의 타입