---
title: Web platform interface
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Web platform interface

# Web Platform Interface

**Web Platform Interface**는 웹 브라우저가 제공하는 표준화된 API들의 집합을 의미합니다. 쉽게 말해, **JavaScript로 브라우저의 기능을 사용할 수 있게 해주는 인터페이스**들입니다.

## 구체적인 예시

웹 개발할 때 사용하는 거의 모든 브라우저 API가 Web Platform Interface에 해당합니다:

### DOM 관련

```jsx
// Document Object Model
document.getElementById('myElement');
element.addEventListener('click', handler);
```

## 네트워크 통신

```jsx
// Fetch API
fetch('https://api.example.com/data');

// WebSocket
new WebSocket('wss://example.com');

// Broadcast Channel (위에서 본 것!)
new BroadcastChannel('channel_name');
```

## 브라우저 기능

```jsx
// Geolocation API
navigator.geolocation.getCurrentPosition();

// Notification API
new Notification('알림 제목');

// LocalStorage
localStorage.setItem('key', 'value');
```

**표준화**: W3C, WHATWG 같은 표준화 기구에서 정의하고 관리합니다.

**크로스 브라우저**: 표준을 따르는 모든 브라우저에서 동일하게 동작해야 합니다 (실제로는 구현 차이가 있을 수 있음).

**JavaScript로 접근**: `window`, `document`, `navigator` 같은 전역 객체를 통해 사용합니다.

## 왜 "Interface"라고 부를까?

프로그래밍에서 **인터페이스**는 "어떻게 사용할 수 있는지"를 정의한 명세입니다. Web Platform Interface는:

- 브라우저 내부 구현(C++, Rust 등)과 JavaScript 사이의 다리 역할
- 개발자가 일관된 방식으로 브라우저 기능을 사용할 수 있게 함
- 명확한 메서드, 속성, 이벤트를 정의