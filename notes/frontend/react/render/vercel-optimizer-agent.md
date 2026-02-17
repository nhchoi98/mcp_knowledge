---
title: Vercel의 최적과 agent 분석
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Vercel의 최적과 agent 분석

# React 핵심 개념 가이드

> Vercel Engineering의 React Best Practices를 기반으로 재정리한 React/Next.js 성능 최적화 가이드
> 

---

## 📊 개념 연관도 (Concept Map)

```
                        ┌─────────────────────────────────────┐
                        │        React 성능 최적화             │
                        └────────────────┬────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        │                                │                                │
        ▼                                ▼                                ▼
┌───────────────┐              ┌───────────────┐              ┌───────────────┐
│  🚀 초기 로딩   │              │  ⚡ 런타임 성능  │              │  🔄 상태 관리   │
│   최적화       │              │     최적화      │              │    최적화       │
└───────┬───────┘              └───────┬───────┘              └───────┬───────┘
        │                              │                              │
   ┌────┴────┐                   ┌─────┴─────┐                   ┌────┴────┐
   │         │                   │           │                   │         │
   ▼         ▼                   ▼           ▼                   ▼         ▼
번들 최적화  서버사이드        렌더링 최적화  JS 성능          리렌더링    데이터 페칭
           성능                             최적화            최적화      최적화

```

---

## 1️⃣ 비동기 처리와 워터폴 제거 (CRITICAL)

### 핵심 개념

**워터폴(Waterfall)** 은 순차적 await로 인해 발생하는 성능 문제입니다. 각 await마다 전체 네트워크 지연이 추가됩니다.

### 연관 개념들

```
Promise.all ─────────────┐
                         │
Suspense Boundaries ─────┼───▶ 병렬 데이터 페칭
                         │
React Server Components ─┘

```

### 📌 핵심 패턴

### 1.1 독립적인 작업은 Promise.all()로 병렬 실행

```tsx
// ❌ 잘못된 예:  순차 실행 (3회 라운드 트립)
const user = await fetchUser()
const posts = await fetchPosts()
const comments = await fetchComments()

// ✅ 올바른 예: 병렬 실행 (1회 라운드 트립)
const [user, posts, comments] = await Promise.all([
  fetchUser(),
  fetchPosts(),
  fetchComments()
])

```

### 1.2 의존성 있는 작업은 better-all 사용

```tsx
import { all } from 'better-all'

// config와 profile이 병렬로 실행됨
const { user, config, profile } = await all({
  async user() { return fetchUser() },
  async config() { return fetchConfig() },
  async profile() {
    return fetchProfile((await this.$. user).id)  // user 완료 후 실행
  }
})

```

### 1.3 Suspense로 UI 스트리밍

```tsx
// 레이아웃은 즉시 렌더링, 데이터가 필요한 부분만 대기
function Page() {
  return (
    <div>
      <Header />  {/* 즉시 렌더링 */}
      <Suspense fallback={<Skeleton />}>
        <DataComponent />  {/* 데이터 로딩 후 렌더링 */}
      </Suspense>
      <Footer />  {/* 즉시 렌더링 */}
    </div>
  )
}

```

### 🔗 연관 개념

- **React Server Components**: 서버에서 데이터 페칭 최적화
- **Streaming**: Suspense와 함께 점진적 렌더링 가능
- **use() 훅**: Promise를 컴포넌트에서 직접 사용

---

## 2️⃣ 번들 사이즈 최적화 (CRITICAL)

### 핵심 개념

초기 번들 크기를 줄여 **Time to Interactive (TTI)** 와 **Largest Contentful Paint (LCP)** 를 개선합니다.

### 연관 개념들

```
                    번들 최적화
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
    ▼                   ▼                   ▼
직접 임포트         동적 임포트         프리로드
(Barrel 회피)      (Code Splitting)    (User Intent)

```

### 📌 핵심 패턴

### 2.1 Barrel File 직접 임포트

```tsx
// ❌ 잘못된 예: 전체 라이브러리 로드 (1,583개 모듈)
import { Check, X, Menu } from 'lucide-react'

// ✅ 올바른 예: 필요한 것만 로드 (3개 모듈)
import Check from 'lucide-react/dist/esm/icons/check'
import X from 'lucide-react/dist/esm/icons/x'

// ✅ Next.js 13.5+에서 자동 최적화
// next.config.js
module.exports = {
  experimental: {
    optimizePackageImports: ['lucide-react', '@mui/material']
  }
}

```

### 2.2 Heavy 컴포넌트는 Dynamic Import

```tsx
import dynamic from 'next/dynamic'

// Monaco Editor (~300KB)를 사용할 때만 로드
const MonacoEditor = dynamic(
  () => import('./monaco-editor').then(m => m.MonacoEditor),
  { ssr: false }
)

```

### 2.3 사용자 의도 기반 프리로드

```tsx
function EditorButton({ onClick }) {
  // 호버/포커스 시 미리 로드
  const preload = () => void import('./monaco-editor')

  return (
    <button
      onMouseEnter={preload}
      onFocus={preload}
      onClick={onClick}
    >
      Open Editor
    </button>
  )
}

```

### 🔗 연관 개념

- **Tree Shaking**: 사용하지 않는 코드 제거
- **Code Splitting**: 코드를 청크로 분리
- **Lazy Loading**: 필요할 때 로드

---

## 3️⃣ 서버사이드 성능 (HIGH)

### 핵심 개념

서버 컴포넌트와 캐싱을 활용해 서버 응답 시간을 최적화합니다.

### 연관 개념들

```
                서버사이드 최적화
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
    ▼                 ▼                 ▼
React. cache()     LRU Cache        데이터 직렬화
(요청 내 중복제거)  (요청 간 캐싱)     최소화

```

### 📌 핵심 패턴

### 3.1 React.cache()로 요청 내 중복 제거

```tsx
import { cache } from 'react'

// 같은 요청 내에서 여러 번 호출해도 한 번만 실행
export const getCurrentUser = cache(async () => {
  const session = await auth()
  if (!session?. user?. id) return null
  return await db.user.findUnique({
    where: { id: session.user.id }
  })
})

```

### 3.2 LRU Cache로 요청 간 캐싱

```tsx
import { LRUCache } from 'lru-cache'

const cache = new LRUCache<string, any>({
  max: 1000,
  ttl: 5 * 60 * 1000  // 5분
})

export async function getUser(id: string) {
  const cached = cache.get(id)
  if (cached) return cached

  const user = await db.user.findUnique({ where: { id } })
  cache.set(id, user)
  return user
}

```

### 3.3 RSC 경계에서 직렬화 최소화

```tsx
// ❌ 잘못된 예: 50개 필드 모두 직렬화
async function Page() {
  const user = await fetchUser()  // 50 fields
  return <Profile user={user} />  // 1 field만 사용
}

// ✅ 올바른 예:  필요한 데이터만 전달
async function Page() {
  const user = await fetchUser()
  return <Profile name={user.name} />  // 필요한 것만 직렬화
}

```

### 3.4 after()로 논블로킹 작업

```tsx
import { after } from 'next/server'

export async function POST(request:  Request) {
  await updateDatabase(request)

  // 응답 후 백그라운드에서 실행
  after(async () => {
    await logUserAction({ userAgent: request.headers.get('user-agent') })
  })

  return Response.json({ status: 'success' })  // 즉시 응답
}

```

---

## 4️⃣ 리렌더링 최적화 (MEDIUM)

### 핵심 개념

불필요한 리렌더링을 방지하여 클라이언트 성능을 최적화합니다.

### 연관 개념들

```
              리렌더링 최적화
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
상태 구독 최적화  메모이제이션    Transitions
                (React. memo)   (useTransition)

```

### 📌 핵심 패턴

### 4.1 상태 읽기를 사용 시점으로 지연

```tsx
// ❌ 잘못된 예:  items 변경 시마다 리렌더링
function ListAction({ items }) {
  const handleClick = () => console.log(items. length)
  return <button onClick={handleClick}>Log Count</button>
}

// ✅ 올바른 예: 클릭 시에만 상태 읽기
function ListAction({ itemsRef }) {
  const handleClick = () => console.log(itemsRef.current.length)
  return <button onClick={handleClick}>Log Count</button>
}

```

### 4.2 Lazy State Initialization

```tsx
// ❌ 잘못된 예: 매 렌더링마다 계산
const [state, setState] = useState(expensiveComputation())

// ✅ 올바른 예: 초기화 시 한 번만 계산
const [state, setState] = useState(() => expensiveComputation())

```

### 4.3 Functional setState

```tsx
// ❌ 잘못된 예: count 의존성 필요
const increment = useCallback(() => {
  setCount(count + 1)
}, [count])

// ✅ 올바른 예:  의존성 불필요
const increment = useCallback(() => {
  setCount(prev => prev + 1)
}, [])

```

### 4.4 useTransition으로 비긴급 업데이트

```tsx
const [isPending, startTransition] = useTransition()

const handleSearch = (query) => {
  // 긴급:  입력 필드 즉시 업데이트
  setInputValue(query)

  // 비긴급:  검색 결과는 나중에
  startTransition(() => {
    setSearchResults(filterResults(query))
  })
}

```

---

## 5️⃣ 렌더링 성능 (MEDIUM)

### 핵심 개념

DOM 조작과 렌더링 프로세스를 최적화합니다.

### 📌 핵심 패턴

### 5.1 정적 JSX 호이스팅

```tsx
// ❌ 잘못된 예: 매 렌더링마다 생성
function Card({ children }) {
  return (
    <div>
      <div className="card-decoration">★</div>
      {children}
    </div>
  )
}

// ✅ 올바른 예: 한 번만 생성
const CardDecoration = <div className="card-decoration">★</div>

function Card({ children }) {
  return (
    <div>
      {CardDecoration}
      {children}
    </div>
  )
}

```

### 5.2 CSS content-visibility로 긴 리스트 최적화

```css
.list-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 100px;  /* 예상 높이 */
}

```

### 5.3 명시적 조건부 렌더링

```tsx
// ❌ 잘못된 예:  count가 0이면 "0" 렌더링
{count && <Badge count={count} />}

// ✅ 올바른 예: 명시적 조건
{count > 0 ?  <Badge count={count} /> :  null}

```

---

## 6️⃣ 클라이언트 데이터 페칭 (MEDIUM-HIGH)

### 핵심 개념

SWR을 활용한 자동 중복 제거와 캐싱으로 네트워크 요청을 최적화합니다.

### 📌 핵심 패턴

### 6.1 SWR로 자동 중복 제거

```tsx
import useSWR from 'swr'

function useUsers() {
  // 여러 컴포넌트에서 호출해도 한 번만 페칭
  return useSWR('/api/users', fetcher)
}

// ComponentA, ComponentB, ComponentC 모두에서 useUsers() 호출해도
// 실제 API 요청은 1회만 발생

```

### 6.2 Passive Event Listener

```tsx
// ✅ 스크롤 성능 최적화
document. addEventListener('wheel', handleWheel, { passive: true })
document.addEventListener('touchstart', handleTouch, { passive: true })

```

---

## 7️⃣ JavaScript 성능 (LOW-MEDIUM)

### 핵심 개념

순수 JavaScript 연산을 최적화하여 전반적인 성능을 향상시킵니다.

### 📌 핵심 패턴

### 7.1 Set/Map으로 O(1) 조회

```tsx
// ❌ 잘못된 예: O(n) 조회
const isSelected = selectedIds.includes(id)

// ✅ 올바른 예:  O(1) 조회
const selectedSet = new Set(selectedIds)
const isSelected = selectedSet.has(id)

```

### 7.2 배열 순회 최소화

```tsx
// ❌ 잘못된 예: 3회 순회
const result = items
  .filter(x => x.active)
  .map(x => x.value)
  .filter(x => x > 0)

// ✅ 올바른 예: 1회 순회
const result = items. reduce((acc, x) => {
  if (x.active && x.value > 0) acc.push(x.value)
  return acc
}, [])

```

### 7.3 정규식 호이스팅

```tsx
// ❌ 잘못된 예: 매번 생성
items.forEach(item => {
  const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/
  if (emailRegex. test(item.email)) { /* ...  */ }
})

// ✅ 올바른 예: 한 번만 생성
const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/
items.forEach(item => {
  if (emailRegex.test(item.email)) { /* ... */ }
})

```

---

## 🎯 우선순위 가이드

| 우선순위 | 카테고리 | 영향도 | 주요 기법 |
|: ---:|:---|:---:|:---|
| 1 | 워터폴 제거 | **CRITICAL** | Promise.all, Suspense, better-all |
| 2 | 번들 최적화 | **CRITICAL** | Dynamic Import, 직접 Import |
| 3 | 서버사이드 | **HIGH** | React.cache, LRU, after() |
| 4 | 데이터 페칭 | **MEDIUM-HIGH** | SWR, Event Dedup |
| 5 | 리렌더링 | **MEDIUM** | memo, useTransition, functional setState |
| 6 | 렌더링 | **MEDIUM** | content-visibility, JSX 호이스팅 |
| 7 | JavaScript | **LOW-MEDIUM** | Set/Map, 배열 최적화 |
| 8 | 고급 패턴 | **LOW** | useLatest, Ref 핸들러 |

---

## 📚 참고 자료

- [React 공식 문서 - cache](https://react.dev/reference/react/cache)
- [Next.js 공식 문서 - after()](https://nextjs.org/docs/app/api-reference/functions/after)
- [Vercel 블로그 - Package Import 최적화](https://vercel.com/blog/how-we-optimized-package-imports-in-next-js)
- [better-all 라이브러리](https://github.com/shuding/better-all)
- [LRU Cache](https://github.com/isaacs/node-lru-cache)

---

*Based on [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices)*

# Reference

https://ywc.life/posts/vercel-react-best-practice/

[https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices)