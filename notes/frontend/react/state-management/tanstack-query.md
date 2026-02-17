---
title: tanstack query
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# tanstack query

# useMutation

- React-Query를 이용해 서버에 변경(insert, update, delete) 작업 요청 시 사용

### 무엇을 하는 훅인가

- 서버에 **부수효과가 있는 작업(CUD 등)**을 트리거하고, 그 진행/결과 상태를 컴포넌트에서 다룰 수 있게 해줘요. 반환값에는 `mutate`, `mutateAsync`, `status`, `isPending/isSuccess/isError/isIdle`, `data`, `error`, `reset` 등이 포함됩니다. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)

### 옵션(첫 번째 인자)

- **`mutationFn(variables, context)`**: 실제 비동기 작업 함수. `variables`는 `mutate(variables)`로 넘긴 값, `context`에는 `QueryClient`, `mutationKey`, `meta`가 담겨요. **필수(기본 뮤테이션 함수가 없다면)**. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
- **`gcTime`**: 뮤테이션 캐시의 가비지 컬렉션까지 유지 시간(ms). `Infinity`면 GC 안 함(브라우저 최대 타이머 제한 관련 주석 있음). [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
- **`mutationKey`**: 해당 키로 **기본 옵션 상속**(setMutationDefaults) 받기 좋음. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
- **`networkMode`**: `'online' | 'always' | 'offlineFirst'`. 네트워크 정책. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
- **콜백 4종**
    - `onMutate(variables)`: **실행 전** 호출. 낙관적 업데이트에 사용, **반환값은 실패 시 `onError/onSettled`로 전달되어 롤백에 쓰임**. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
    - `onSuccess(data, variables, onMutateResult, context)`: 성공 시. 비동기 허용. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
    - `onError(err, variables, onMutateResult, context)`: 실패 시. 비동기 허용. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
    - `onSettled(data, error, variables, onMutateResult, context)`: 성공/실패 **모두** 후처리. 비동기 허용. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
- **`retry`, `retryDelay`**: 재시도 횟수/지연(지수/선형 백오프 예시). 기본 `retry: 0`. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
- **`scope`**: `{ id }`를 주면 **같은 scope id를 가진 뮤테이션은 직렬(serial)로 실행**(경합 방지). 기본은 유니크 id(병렬). [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
- **`throwOnError`**: 에러를 렌더 단계에서 throw하여 에러 바운더리로 전파할지 제어. 함수로 조건부도 가능. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
- **`meta`**: 캐시에 붙는 임의의 메타데이터(훅/캐시 콜백에서 접근). [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
- **두 번째 인자 `queryClient?`**: 기본 컨텍스트 대신 커스텀 클라이언트 사용. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)

### 반환값(핵심만)

- **`mutate(variables, { onSuccess, onError, onSettled })`**: 즉시 실행(콜백은 **이번 호출에만** 적용). **동시에 여러 번 호출하면 마지막 호출 기준으로 onSuccess가 실행**됨. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
- **`mutateAsync(variables, ...)`**: `Promise`를 반환하여 `await` 가능. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
- **상태/데이터**:
    
    `status`(`idle|pending|error|success`), 파생 불리언(`isPending` 등), `data`, `error`, `reset()`, `failureCount/failureReason`, `submittedAt`, `variables`. [TanStack](https://tanstack.com/query/v5/docs/react/reference/useMutation)
    

### 관련 유틸

- **`useMutationState`**: 뮤테이션 캐시에 있는 **모든(또는 필터된) 뮤테이션 상태**를 조회(예: `status: 'pending'` 인 것들 변수 모으기). `mutationKey`로 특정 그룹만 훑을 수도 있어요.