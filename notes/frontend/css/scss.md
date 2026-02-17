---
title: SCSS
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# SCSS

# 🎨 Sass/SCSS란?

- **Sass (Syntactically Awesome Stylesheets)**
    
    → CSS를 더 프로그래밍적으로 작성할 수 있게 해주는 **CSS 전처리기**.
    
- **SCSS (Sassy CSS)**
    
    → Sass의 최신 문법. **CSS와 거의 똑같은 문법**을 사용하기 때문에 기존 CSS 사용자도 쉽게 적응 가능.
    
    - `Sass` : 들여쓰기 기반 문법
    - `SCSS`: 중괄호(`{}`)와 세미콜론(`;`) 기반 (일반 CSS와 유사)

👉 사실상 **현업에서는 대부분 SCSS 문법**을 씁니다.

## 1. **변수 (Variables)**

- 색상, 크기, 간격 등을 변수로 관리 → 유지보수성 ↑

`$primary-color: #2563eb;
$padding: 12px;`

`.btn {
background: $primary-color;
padding: $padding;
}`

## 2. **중첩 (Nesting)**

- 계층 구조를 코드로 표현할 수 있음.

## 3. **믹스인 (Mixins)**

- CSS 함수처럼 재사용 가능한 코드 블록 정의.

## 4. **상속 (Extend / Inheritance)**

- 공통 스타일을 상속받아 코드 중복 제거.

## 5. **연산 (Operations)**

- 수학 연산 가능.

# SCSS에서 @mixin, @extend 공통/차이점

| 구분 | CSS | Sass/SCSS |
| --- | --- | --- |
| 변수 | 없음 | `$변수명` 지원 |
| 중첩 | 없음 | 중첩 문법 지원 |
| 함수 | 제한적 | `lighten()`, `darken()` 등 다양한 내장 함수 |
| 재사용 | 클래스 복붙 | Mixin, Extend 가능 |
| 구조화 | 하나의 큰 CSS | Partials + @use 로 모듈화 가능 |

| 구분 | **@mixin** | **@extend** |
| --- | --- | --- |
| 동작 방식 | 코드 복사 (inline) | 선택자 병합 (상속) |
| 유연성 | 파라미터 전달 가능 → 다양하게 활용 | 파라미터 불가, 정적인 상속만 |
| 결과 CSS | 같은 스타일이 여러 번 중복될 수 있음 | CSS 코드 줄 수 있음 (중복 줄임) |
| 단점 | 코드가 중복돼서 CSS 파일이 커질 수 있음 | 선택자 체인이 꼬이면 예상치 못한 스타일 충돌 발생실무 팁 |
- **재사용하면서 상황별 옵션이 필요한 경우 → `@mixin`**
    
    (ex. `@mixin button($color) { ... }`)
    
- **완전히 같은 스타일을 여러 셀렉터에 적용할 경우 → `@extend`**
    
    (ex. `.btn` 기본 속성 상속받기)
    

---

👉 정리하면:

- `@mixin`은 **복사 + 파라미터 가능 → 함수 같은 개념**
- `@extend`는 **상속 + 셀렉터 병합 → 클래스 계승 같은 개념**