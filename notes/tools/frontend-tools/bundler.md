---
title: Bundler
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Bundler

# 개념

번들러(Bundler)”는 **프론트엔드 개발에서 여러 개의 자원(JS, CSS, 이미지 등)을 하나(또는 소수)의 파일로 묶어주는 도구**를 말합니다.

## 왜 번들러가 필요할까?

### (1) 모듈 시스템과 브라우저 한계

- 과거 자바스크립트는 브라우저에서 모듈 개념이 없어서 `<script>` 태그를 여러 개 달아야 했음.
- ES6에서 `import/export`가 생겼지만, 여전히 브라우저는 **네트워크 요청이 많으면 느려짐**.

### (2) 성능 최적화

- JS 파일, CSS 파일, 이미지가 수십~수백 개라면, 브라우저가 HTTP 요청을 너무 많이 함 → 느려짐.
- 번들러는 이를 **최소한의 파일로 합쳐서 제공** → 네트워크 효율 ↑

### (3) 개발 편의

- ES6, TypeScript, JSX 같은 최신 문법은 브라우저가 직접 못 읽음.
- 번들러는 **트랜스파일러(Babel, SWC 등)**와 결합해 브라우저가 이해할 코드로 변환.

## 번들러의 역할

1. **모듈 그래프 생성**
    - 진입점(entry)에서 시작해서 `import/export`를 따라가며 의존성 그래프를 분석.
    - 예: `index.js → utils.js → lodash`
2. **자원 통합**
    - JS, CSS, 이미지 등 다양한 파일을 모듈로 인식 → 하나의 결과물로 묶음.
    - 예: CSS-in-JS, 이미지 → base64 embedding
3. **최적화**
    - **Minify/Compress**: 코드 압축, 불필요한 공백 제거.
    - **Tree Shaking**: 사용하지 않는 코드(dead code) 제거.
    - **Code Splitting**: 필요한 시점에 필요한 코드만 불러오기(동적 import).
    - **Caching**: 해시 기반 파일명 생성으로 브라우저 캐싱 최적화.
4. **개발 경험 개선**
    - **Hot Module Replacement(HMR)**: 코드 수정 시 브라우저가 즉시 갱신.
    - **로컬 개발 서버** 제공.

## 번들러와 빌드 도구 차이

- **번들러(Bundler)** = 모듈을 묶고 최적화하는 핵심 역할.
- **빌드 도구(Build Tool)** = 번들러를 포함하면서, 개발 서버, HMR, 테스트, 플러그인 시스템까지 제공.
    - 예: **Vite, Next.js, CRA(Create React App)**

- **Yarn = 의존성 관리자**
    - 어떤 라이브러리를 어떤 버전으로 가져올지, 어떻게 저장할지 결정.
    - lockfile로 버전 트리를 고정.
- **번들러 = 빌드/번들링 엔진**
    - Yarn이 설치해둔 의존성 + 애플리케이션 코드를 import/export 그래프 따라 분석.
    - 최적화 후 브라우저가 실행할 수 있는 번들 산출.

👉 **Yarn은 “재료를 준비”하고, 번들러는 “재료를 요리해서 최종 요리를 만드는” 관계**라고 비유할 수 있어요.

# HMR(Hot Module Replacement)

프론트엔드 개발에서 **코드 수정 시 브라우저 전체를 새로고침하지 않고, 바뀐 모듈만 실시간으로 교체해 주는 기능**을 말합니다.

## 기존 방식: 전체 리로드

- 개발자가 `App.js`를 수정 → 브라우저 전체 페이지를 리로드해야 반영됨.
- 단점:
    - 상태(state)가 초기화됨 (예: 입력 폼, Redux store 다 날아감).
    - 전체 리로드라서 속도 느리고 개발 효율 낮음.

---

## 2. HMR 방식: 모듈만 교체

- HMR은 수정된 **특정 모듈만 다시 로드하고 교체**해줍니다.
- 예: 버튼 컴포넌트 파일만 바뀌면, 번들러/개발 서버가 해당 모듈만 새로 로드해서 교체.
- 브라우저는 전체 리로드가 아니라 **부분 업데이트**만 수행 → 빠르고 상태 유지 가능.

# Tree shaking

번들링할 때 **“쓰이지 않는 코드(dead code)를 모듈 그래프에서 걷어내는 과정”**이에요. 결과적으로 번들 크기가 줄고 로드가 빨라집니다.

### **1. ESM(ES Modules) 기반의 정적 분석**

- Tree Shaking은 `import/export` 구문이 **정적 구조(compile-time에 분석 가능)** 라는 점을 활용합니다.
- 예시:
    
    ```jsx
    // utils.js
    export function add(a, b) { return a + b; }
    export function sub(a, b) { return a - b; }
    
    // index.js
    import { add } from './utils.js';
    console.log(add(2, 3));
    
    ```
    
    👉 여기서 `sub` 함수는 불러오지 않았으므로 **번들 결과에서 제거**됩니다.
    

---

### 2. **Dead Code Elimination (DCE) + Minifier 연계**

- 번들러(Webpack/Rollup/Vite)가 ESM 기반으로 **사용되지 않는 export를 표시**하고,
- 이후 Terser/Uglify 같은 **압축기(minifier)**가 실제 JS 코드에서 제거합니다.
- 즉, 번들러가 “이건 안 쓰임”이라고 태깅 → Minifier가 최종적으로 삭제.

단, 조건부 Export 에서는 제거 불가능 

## . **조건부 export / 런타임 의존 코드**

- 어떤 export가 쓰일지 컴파일 단계에서 알 수 없으면 제거 불가능.
    
    ```jsx
    if (process.env.NODE_ENV === "production") {
      export const feature = () => {};
    }
    
    ```