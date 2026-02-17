---
title: 반응성 원리
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 반응성 원리

# 키워드

Track, Trigger, Proxy

# 반응성이란?

1. **변수를 읽을 때 추적(track when a variable is read)**
    - 예: `A0 + A1` 을 평가하면, `A0` 와 `A1` 두 변수를 읽게 됩니다.
    - 이 시점에 Vue는 “어떤 effect(반응형 함수)가 지금 실행 중인지”를 알고 있어서, 해당 변수들이 **현재 실행 중인 effect의 의존성**이라고 기록합니다.

---

1. **effect를 subscriber로 등록 (make that effect a subscriber)**
    - 만약 변수가 읽히는 순간 실행 중인 effect가 있다면, 그 effect는 해당 변수의 **구독자(subscriber)**가 됩니다.
    - 예: `update()`라는 effect를 실행할 때 `A0`, `A1`을 읽는다면 → `update()`는 자동으로 `A0`, `A1`의 구독자가 됩니다.
    - 즉, 이후 `A0` 또는 `A1`이 바뀌면 `update()`가 다시 실행되도록 연결이 맺어지는 거예요.

---

1. **변경 감지 (detect when a variable is mutated)**
    - 예: `A0 = 5` 와 같이 새로운 값이 할당되면, Vue는 `A0`에 구독된 모든 effect들을 찾아서 **재실행(re-run)** 시킵니다.
    - 이렇게 하면 DOM을 다시 그리거나, 계산된 값을 다시 구할 수 있게 됩니다.

---

## 핵심 요약

- **읽기 시점:** “누가 나를 읽었는지”를 기록 (의존성 추적, tracking).
- **쓰기 시점:** “나를 읽었던 애들한테 알려주기” (변경 알림, triggering).

즉, Vue의 반응형은 **track → trigger** 구조로 돌아갑니다.

Vue.js 2는 Vue 인스턴스에 `data` 옵션으로 전달되는 객체의 모든 속성을 순회하며 `Object.defineProperty`를 사용하여 반응형을 구현한다.

### `track`: 반응형으로 실행할 코드를 저장

Vue.js 3에서는 반응형을 위한 데이터 설계를 `Map`, `Set`, `WeakMap`로 구현하였다. (`obj`와 `effect`는 예제용 코드이다.)

Proxy는**객체 조작을 근본적으로 가로채고 제어할 수 있는 기능**

을 제공하기 위해 ES6에 도입되었습니다.

이는 기존

```
Object.defineProperty
```

방식의 한계를 극복하고, 자바스크립트를 더 강력한

**메타 프로그래밍 언어**

로 진화시키려는 목적이 있었던 거예요.

## 자바스크립트 - Reflect

 ***Reflect*** 는 중간에서 가로챌 수 있는 ***JavaScript*** 작업에 대한 메서드를 제공하는 내장 객체입니다. 메서드의 종류는 프록시 처리기와 동일합니다.

# Proxy가 필요한 이유

## 1. 원본 객체에 직접 접근하는 게 문제인 경우

### (1) **보안 / 접근 제어**

- 예: DB 연결, 파일 시스템, 원격 API 등 민감한 자원에 대한 접근
- 클라이언트가 무분별하게 원본 객체를 호출하면 위험할 수 있음 → Proxy가 중간에서 허용 여부를 확인

### (2) **성능 최적화 / 캐싱**

- 원본 객체가 무겁거나(예: 이미지, DB 쿼리) 호출 비용이 큰 경우, 매번 실행하면 비효율적
- Proxy가 호출 결과를 캐싱해 두고, 다음 호출 때는 재사용

### (3) **지연 로딩(Lazy Loading)**

- 어떤 객체는 생성 비용이 너무 커서, 필요할 때까지 만들고 싶지 않음
- Proxy가 대신 “껍데기” 역할을 하고 있다가, 실제 필요해질 때 원본을 생성

Vue 3의 반응형 시스템도 같은 원리예요:

- 원본 객체(`reactive()`)에 접근하는 걸 **Proxy가 가로채서**
    - `get` → "누가 이 데이터를 읽었는지" 기록 (track)
    - `set` → "이 데이터 바뀌었다" 알리고 구독자(effect) 실행 (trigger)
- 즉, Proxy가 없으면 **자동 추적/갱신이 불가능**합니다.

## Reactive Object와 Ref 차이

### Reactive Object

- **기준:** 객체(Object)를 **Proxy**로 감싼 형태
- **특징:**
    - 객체 전체에 대해 속성 읽기/쓰기(get/set)를 **Proxy 트랩**으로 가로챔
    - 중첩 객체도 자동으로 reactive 처리됨 (deep reactive)
    - 구조적으로 “원본 객체(Object) + Proxy”가 한 세트

### Ref

- **기준:** 값(primitive, object 상관없음)을 **객체(Object)의 속성**에 담음
- **특징:**
    - 내부 구조는 `{ value: 원본값 }` 형태
    - Proxy가 아니라 그냥 평범한 JS Object
    - 다만 Vue가 `value` 접근 시 **get/set을 추적**하도록 만들어둠
    - 값이 원시 타입이면 그대로, 객체면 내부적으로 다시 reactive 처리

내부적으로 `ref(객체)`를 넣으면 Vue가 알아서 `reactive`로 바꿔줍니다.

### Computed와 Watch, WatchEffect의 차이와 공통점을 아는지?

세 가지 모두 Vue의 반응형 시스템(effect) 위에서 동작하지만, 목적이 다릅니다. `computed`는 getter 기반으로 결과를 캐싱해 파생 데이터를 효율적으로 계산하는 데 쓰이고, `watch`는 특정 상태 변화를 감지해서 이전 값과 새 값을 비교해 콜백을 실행할 수 있습니다. `watchEffect`는 의존성을 자동으로 추적하면서 부수효과를 즉시 실행합니다. 내부적으로는 모두 effect를 등록해 동작하지만, computed는 lazy effect + dirty flag로 캐싱을 구현하고, watch는 scheduler를 통해 이전 값/새 값 비교, watchEffect는 즉시 실행 후 scheduler로 반복 실행하는 구조로 정의되어 있습니다.

# Computed

### 동작 방식

- **정의:** `computed(getter)` → 내부적으로는 `effect(getter, { lazy: true })`
- Proxy 객체 속성을 읽으면, getter가 실행되고 값이 캐싱됨.
- 의존하는 반응형 값이 바뀌면 → dirty 플래그만 세팅.
- 다음에 `.value` 읽을 때만 다시 계산.

### 코드 흐름

```tsx
const a = ref(1)
const b = ref(2)
const sum = computed(() => a.value + b.value)

```

- `sum.value` 처음 읽을 때 → `a.value`, `b.value`를 Proxy get → `track(sumEffect)`
- `a`나 `b`가 바뀌면 → `trigger` → sumEffect dirty 표시
- 다시 `sum.value` 읽을 때만 getter 재실행

👉 **특징:** “게으른(lazy) + 캐싱”

# Watch

### 동작 방식

- **정의:** `watch(source, callback)`
- `source`에서 의존하는 반응형 Proxy를 effect로 감싸 실행
- 값이 바뀔 때마다 callback을 바로 실행 (비교 후 실행)

# WatchEffect

### 동작 방식

- **정의:** `watchEffect(effect)`
- 초기에 effect를 실행하면서 읽은 모든 반응형 Proxy 속성을 추적(track)
- 값이 바뀌면 effect를 다시 실행
- `watch`는 “특정 소스”를 추적하지만,
- `watchEffect`는 “실행된 코드 블록 안에서 읽힌 모든 반응형 값”을 자동 추적

| 구분 | Computed | Watch | WatchEffect |
| --- | --- | --- | --- |
| **Proxy get 시점** | getter 실행 → 값 캐싱, dirty 플래그 관리 | source 함수 실행 → 읽은 Proxy track | effect 함수 실행 → 읽은 Proxy 전부 track |
| **Proxy set 시점** | dirty = true (다음 `.value` 접근 때만 재실행) | 값 변경 즉시 callback 실행 | 값 변경 즉시 effect 재실행 |
| **대상** | 보통 **파생값**(derived state) | **특정 소스 + 콜백** | **코드 블록 전체** (자동 의존성 수집) |
| **실행 특성** | Lazy + 캐싱 | Eager (변경 즉시 실행) | Eager (변경 즉시 실행) |

## Lazy하게 반응한다 (반응형 시스템에서 Lazy)

Vue에서 **`computed`** 같은 개념을 설명할 때 쓰이는 표현이에요.

- 의미: 값이 바뀔 때마다 즉시 다시 계산하지 않고,
    
    **“정말 필요할 때(접근할 때)만” 계산한다**는 뜻.
    
- 구현 방식: 내부에서 `dirty`라는 플래그를 두고, 값이 변경되면 플래그만 세팅 → 다음 `get`할 때 다시 계산.

## Watch / WatchEffect와 비교

- **`watch` / `watchEffect`** → 의존성이 바뀌면 값이 달라지든 같든 무조건 실행됩니다.
- **`computed`** → 값이 진짜로 변해야만 새로운 계산 결과를 내보냅니다.

## Lazy Loading (지연 로딩)

웹 개발에서 흔히 쓰이는 성능 최적화 기법이에요.

- 의미: 리소스(이미지, 모듈, 데이터 등)를
    
    **“처음부터 다 불러오지 않고, 실제로 필요해질 때 로드하는 방식”**
    
- 사용 예시:
    - 웹페이지에서 보이지 않는 아래쪽 이미지는 스크롤할 때 로딩
    - SPA에서 특정 라우트에 들어가야만 JS 번들 다운로드
    - 초기 렌더링 속도를 개선하려고 비동기 import 사용

## Virtual DOM diffing

| 구분 | Ref | Computed |
| --- | --- | --- |
| **역할** | 상태 그 자체 | 파생 데이터(derived state) |
| **캐싱** | ❌ 없음 (읽을 때마다 그대로 접근) | ✅ 있음 (값 변할 때만 재계산, 결과 저장) |
| **최적화 포인트** | Virtual DOM diffing 단계에서만 최적화 | 데이터 가공 자체를 캐싱 (불필요한 연산 줄임) |

| 구분 | Ref 내려보내기 | Computed 내려보내기 |
| --- | --- | --- |
| **구조** | `{ value: 원본 값 }` | `{ value: 파생 값 }` |
| **캐싱** | 없음 | 있음 (값 변할 때만 재계산) |
| **자식에서 수정** | 가능 (부모 state 변경됨) | 기본 불가능 (read-only) |
| **의미** | 원본 state를 직접 공유 | 가공된 derived state를 전달 |

- **자주 오가는 화면 + 상태/스크롤 유지 필요** → ✅ KeepAlive
- **초기화가 무거운 위젯(차트/에디터/지도)** → ✅ KeepAlive

## 참고

[https://meetup.nhncloud.com/posts/300](https://meetup.nhncloud.com/posts/300)

[https://vuejs.org/guide/extras/reactivity-in-depth.html](https://vuejs.org/guide/extras/reactivity-in-depth.html)