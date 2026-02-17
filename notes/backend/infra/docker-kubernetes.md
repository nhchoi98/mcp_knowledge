---
title: Docker, Kubernates
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Docker, Kubernates

**Dockerfile**은 “컨테이너 이미지 만드는 레시피(빌드 스크립트)”고,

**Kubernetes**는 “그 이미지를 여러 대(노드)에 뿌리고, 살아있게 관리하는 오케스트레이션 시스템”이에요.

즉, Dockerfile → 이미지 빌드 → 레지스트리에 푸시 → Kubernetes가 그 이미지를 풀(pull)해서 컨테이너로 실행·확장·복구합니다.

# Kubernates

## 🎯 Deploy 서버란?

Kubernetes 클러스터와 직접 통신하면서 배포 명령을 내리는 **중간 관리 서버**입니다.

### 구조 이해하기

[개발자 로컬 PC]
↓ SSH 접속
[Deploy 서버] ← kubectl 명령 실행
↓ kubectl 명령 전달
[Kubernetes 클러스터]
├─ Master Node
└─ Worker Nodes

## 왜 별도 서버가 필요한가?

### 1. **보안상의 이유** 🔒

- Kubernetes 클러스터를 외부에 직접 노출하지 않음
- Deploy 서버만 클러스터에 접근 권한 보유
- 개발자는 Deploy 서버를 통해서만 접근

### 2. **네트워크 접근 제어**

- 사내 클러스터는 보통 내부망(VPC)에만 존재
- Deploy 서버는 내부망과 외부망 사이의 중계 역할
- 개발자는 VPN 없이 Deploy 서버만 접속

### 3. **관리의 편의성**

- CI/CD 파이프라인 실행
- 배포 스크립트 보관
- kubectl, helm 등 도구 통합 관리