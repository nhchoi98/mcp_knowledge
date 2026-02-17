---
title: Next.js
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Next.js

# 키워드

getServerSideProps,  getStaticPaths, getStaticProps, App router, **React Server Components(RSC), Streaming, Client** component, Instrumentation, Suspense

최초 진입점은 _app.tsx

**Next.js**로 만들면 `index.html`은 **직접 작성하지 않으며**, `app/layout.tsx`·`page.tsx`로 구조/페이지를 정의합니다.

→ 왜 필요가 없을까? 

Next.js의 `app/` 디렉토리 구조 자체가 “라우팅·레이아웃·상태경계·캐시전략”을 정의하는 약속(convention)**이기 때문이야. 이 **약속을 지키면 Next가 정적분석해서** URL 매핑, 코드 스플리팅, 스트리밍/하이드레이션, 캐싱/재검증(ISR)까지 자동 최적화해줘.

# 왜 그 구조를 쓰냐 — 근거 6가지

1. **폴더 = URL 세그먼트**
    
    `app/blog/page.tsx` → `/blog`처럼, 폴더/파일로 라우트를 선언해. 중첩 폴더는 중첩 라우트가 되고, 자연스럽게 중첩 레이아웃을 구성해. [Next.js+1](https://nextjs.org/docs/app/getting-started/layouts-and-pages?utm_source=chatgpt.com)
    
2. **특수 파일로 화면 뼈대와 상태 경계를 선언**
    - `layout.tsx`는 해당 세그먼트의 공통 UI(헤더/내비 등)를 감싸고 라우트 간에 **지속**돼.
    - `page.tsx`가 실제 페이지 본문.
    - `loading.tsx`는 세그먼트 단위 **즉시 로딩 UI + 스트리밍**을 켜는 스위치.
    - `error.tsx`는 세그먼트별 에러 경계, `not-found.tsx`는 404 UI.
    - `template.tsx`는 네비게이션 때 **새 인스턴스**로 감싸고 싶을 때. [Next.js+4Next.js+4Next.js+4](https://nextjs.org/docs/app/getting-started/layouts-and-pages?utm_source=chatgpt.com)
3. **Route Group으로 URL에 안 보이는 폴더 정리**
    
    `(dashboard)/users`처럼 괄호 폴더는 URL에 드러나지 않고, 섹션/팀별로 파일을 묶을 수 있어(레이아웃 공유에도 유용). [Next.js+1](https://nextjs.org/docs/app/api-reference/file-conventions/route-groups?utm_source=chatgpt.com)
    
4. **UI 곁에 API를 공존**
    
    `app/api/*/route.ts`로 REST 핸들러(웹 표준 Request/Response)를 라우트와 같은 트리 안에 둬서 **프론트·백 소스의 공위치(colocation)**와 배포를 단순화. [Next.js+1](https://nextjs.org/docs/app/getting-started/route-handlers-and-middleware?utm_source=chatgpt.com)
    
5. **Server/Client 컴포넌트 구분을 구조로 표현**
    
    기본은 **서버 컴포넌트**(데이터 패칭·캐시·스트리밍 유리), 브라우저 상호작용이 필요한 파일만 `use client`. 구조를 지키면 번들이 작아지고 하이드레이션 비용이 줄어. [Next.js](https://nextjs.org/docs/app/getting-started/server-and-client-components?utm_source=chatgpt.com)
    
6. **세그먼트별 캐싱·재검증 정책(SSR/SSG/ISR) 선언**
    
    각 폴더(세그먼트)에서 `export const revalidate`, `dynamic` 등을 지정하거나 `fetch(..., { next: { revalidate, tags } })`로 세밀하게 제어—**라우트 단위로 신선도 정책**이 박힌다. [Next.js+1](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config?utm_source=chatgpt.com)
    

---

## 이 구조가 주는 실전 이득

- **가독성/예측성**: 파일 경로만 봐도 **URL·레이아웃·상태경계**가 보임. 새 팀원이 들어와도 바로 파악 가능. [Next.js](https://nextjs.org/docs/app/getting-started/project-structure?utm_source=chatgpt.com)
- **성능 기본값**: 라우트/세그먼트 기준 **자동 코드 스플리팅** + **스트리밍 로딩 UI** → 초기 표시 빠르고, 상호작용 영역만 하이드레이션. [Next.js](https://nextjs.org/docs/14/app/building-your-application/routing/loading-ui-and-streaming?utm_source=chatgpt.com)
- **운영 편의**: 읽기 많은 페이지는 ISR, 개인화 뷰는 SSR/CSR처럼 **폴더 단위 정책**으로 혼합 전략을 간단히 적용.

- **서버에서 할 수 있으면 서버에서**(읽기·렌더·보안 로직).
- **브라우저 상호작용이 필요한 부분만** `'use client'`로 좁게.
- **데이터 갱신은 `'use server'` 서버 액션**으로 안전하게.

# App Router

The **App Router** is a file-system based router that uses React's latest features such as 

[Server Components](https://react.dev/reference/rsc/server-components), [Suspense](https://react.dev/reference/react/Suspense), and [Server Functions](https://react.dev/reference/rsc/server-functions)

## Page router와의 차이점

- Pages Router: `pages/` 디렉터리 안의 각 파일이 곧 라우트.
- App Router: `app/` 디렉터리 안의 폴더(segment)와 특수 파일(`page.tsx`, `layout.tsx`, `loading.tsx` 등)로 라우트를 선언
- Pages Router: 전통적인 SSR(서버사이드 렌더링), SSG(정적생성), CSR(클라이언트) 패턴 위주. `getServerSideProps`, `getStaticProps` 같은 함수를 페이지에서 export해서 데이터를 넣어줌. [Next.js](https://nextjs.org/docs/pages/building-your-application/data-fetching/get-server-side-props?utm_source=chatgpt.com) [Next.js](https://nextjs.org/docs/pages/building-your-application/data-fetching/get-static-props?utm_source=chatgpt.com)
- App Router: 기본이 React Server Components. 컴포넌트 자체가 서버에서 async/await로 데이터 가져오고 바로 렌더링할 수 있고, 스트리밍/부분 로딩(loading.tsx) 같은 최신 React 기능이 내장돼 있음.

**App Router 쪽 방식**

- App Router에서는 라우트 컴포넌트 자체가 기본적으로 **Server Component**다. 즉 컴포넌트 함수를 `async`로 만들고 안에서 DB나 외부 API를 직접 호출한 뒤 그 결과를 바로 JSX로 리턴할 수 있다. 별도의 `getServerSideProps` 함수가 필요 없다. [Next.js](https://nextjs.org/docs/14/app/building-your-application/routing) [Next.js](https://nextjs.org/docs/app/getting-started/fetching-data?utm_source=chatgpt.com)
- 이런 Server Component들은 서버에서만 실행되므로 비밀 키나 DB 커넥션을 그대로 써도 되고, 그 결과만 브라우저로 보내 성능·보안 이점을 얻는다. [Next.js](https://nextjs.org/docs/app/getting-started/fetching-data?utm_source=chatgpt.com)
- App Router는 React Suspense/Streaming을 기본으로 지원해서, 부분적으로 먼저 렌더 가능한 UI를 먼저 보내고 나머지를 점진적으로 스트리밍할 수 있게 설계돼 있다. 이 스트리밍 중 로딩 상태를 처리하는 전용 `loading.tsx` 파일도 라우트 단위로 둘 수 있다. [Next.js](https://nextjs.org/docs/14/app/building-your-application/routing) [Next.js](https://nextjs.org/docs/app?utm_source=chatgpt.com)

한 줄로 말하면: Pages Router는 "데이터를 props로 미리 주입하는 모델", App Router는 "컴포넌트 자체가 서버에서 async로 데이터를 채우고 바로 렌더하는 모델".

# Server component

**Server Component = 브라우저에서 안 돌고, 서버에서만 실행되는 React 컴포넌트.**

즉 이 컴포넌트의 JS 코드는 클라이언트(사용자 브라우저)로 안 보내지고, 서버에서 렌더링된 결과(HTML/serialized payload)만 브라우저로 전달돼. 그래서 번들 사이즈를 덜어주고 보안/성능이 좋아진다.

반대로, Client Component가 존재한다. 

## 서버 컴포넌트를 써야 하는 경우

아래 중 하나라도 해당되면 서버 컴포넌트가 맞아.

1. **데이터를 읽기만 한다 / 화면에 뿌리기만 한다**
    - 예: 목록 페이지, 상세 페이지, 대시보드 통계 값 등
    - 서버에서 DB나 API 불러오고 JSX로 뿌리는 애들
    - 클릭 핸들러나 상태 관리가 필요 없으면 굳이 클라이언트일 이유가 없음
2. **보안이 중요한 로직/정보를 다룬다**
    - DB 직접 접근
    - 비밀 토큰(.env), private API 키 사용
    - 결제 백엔드 호출 등
        
        클라이언트로 보내면 안 되는 정보를 사용할 때는 무조건 서버에서 처리하고 결과만 내려줘야 해.
        
3. **SEO/초기 렌더링에 좋은 정적인 UI를 만들고 싶다**
    - 블로그 글, 상품 상세, 문서 페이지처럼 대부분 읽기 전용 콘텐츠
4. **페이지 레이아웃 / 중첩 레이아웃 / 공통 프레임**
    - `layout.tsx`
    - header/sidebar처럼 전역 뼈대 역할만 하는 컴포넌트
    - 여기서 굳이 이벤트/로컬 상태 안 쓰면 서버로 두는 게 맞다
5. **무거운 데이터 조합 / 가공 / 필터링을 하고 싶다**
    - 예: 여러 서비스에서 데이터를 합쳐 랭킹 계산하고 테이블로 던지는 경우
    - 이걸 클라에서 하면 API 여러 번 치고 병합해야 하니까 느림. 서버에서 한 번에 처리하면 빠름.

[디렉토리 구조 예시 ](Next%20js/%EB%94%94%EB%A0%89%ED%86%A0%EB%A6%AC%20%EA%B5%AC%EC%A1%B0%20%EC%98%88%EC%8B%9C%2028ccee38e89a80b1990be2bde55f3fe7.md)

[라우팅](Next%20js/%EB%9D%BC%EC%9A%B0%ED%8C%85%2028ccee38e89a801aa4d1d7af33d6a73b.md)