---
title: iframe
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# iframe

`<iframe>`은 독립된 브라우저 컨텍스트(즉, 별도의 문서/윈도우)를 만들기 때문에, **부모 문서와 직접적으로는 완전히 섞이지 않습니다.**

그럼에도 불구하고 **특정 조건**에서 서로 통신할 수 있는 방법이 있어요.

---

## 1. 기본 원칙

- iframe은 **자체적인 DOM, Window, JavaScript 실행 컨텍스트**를 가짐.
- 따라서 부모 페이지의 JS 변수나 DOM에 **바로 접근할 수는 없음**.
- 하지만 보안 정책(Same-Origin Policy)에 따라 다름:
    - *같은 출처(same-origin)**라면: 부모 ↔ iframe 간에 자유롭게 접근 가능.
    - *다른 출처(cross-origin)**라면: 직접 DOM 접근 불가 → 안전한 통신 API(`postMessage`)만 사용 가능.