---
title: 브라우저 기본
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 브라우저 개요

## 웹 브라우저 아키텍처
- UI, 네트워크, 렌더러(프로세스 분리), 스토리지 등 주요 컴포넌트로 구성
- 프로세스 격리: 사이트 격리(Site Isolation)로 보안/안정성 확보

## 주요 Web Platform Interfaces
- DOM API, Fetch/XHR, Storage API(local/session), BroadcastChannel 등
- iframe: 외부/다른 출처 문서를 현재 문서에 포함시키는 컨테이너

## 탭 간 통신: Broadcast Channel API
```jsx
const channel = new BroadcastChannel('my_channel');
channel.onmessage = (event) => console.log(event.data);
channel.postMessage('hello');
channel.close();
```
- 같은 origin의 탭/창/iframe/워커 간 pub-sub
- 클라이언트↔서버가 필요한 WebSocket과 목적이 다름 (로컬, 서버 불필요)

## 참고 링크
- [Web platform interface](web-platform-interface.md)
