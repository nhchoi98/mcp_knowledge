---
title: Python
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Python

# 가상환경(venv) 만들기

프로젝트 루트에서:

```
python3 -m venv .venv
```

그리고 가상환경 활성화:

- macOS / Linux (zsh, bash 기준)

```jsx
source .venv/bin/activate
```

## 2. 필요한 패키지 설치

여기서 우리가 사용할 건:

- `fastapi` : 웹 프레임워크
- `uvicorn` : fastapi 앱을 실제로 띄우는 ASGI 서버
- `sqlmodel` : 모델/스키마 정의 (SQLAlchemy + Pydantic 기반)
- (지금은 메모리 DB지만, 나중에 실제 DB 붙일 거 대비해서 sqlmodel도 필요)

아래 한 번에 설치:

```jsx
pip install fastapi uvicorn sqlmodel
```

설치 확인:

```jsx
python -c "import fastapi, sqlmodel; print('fastapi ok, sqlmodel ok')"
```

# 데이터베이스 무결성

데이터베이스 무결성이란, 데이터가 정확하고, 일관성 있고, 신뢰할 수 있는 상태를 전체 수명 주기 동안 유지하는 것을 말합니다. 데이터의 유효성을 보장하고 부적절한 데이터의 삽입, 수정, 삭제를 방지하기 위해 무결성 제약조건을 설정하여 유지하며, 이는 도메인 무결성, 엔티티 무결성, 참조 무결성 등의 종류가 있습니다

## FastAPI에서 `main.py`를 많이 보는 이유

FastAPI 예제에서 자주 이렇게 하잖아:

```
uvicorn main:app --reload
```

여기서 의미는:

- `main` 라는 파이썬 모듈(= main.py 파일)을 import 하고
- 그 안에 있는 `app` 객체(FastAPI 인스턴스)를 찾은 다음
- 그걸 서버로 띄워라

즉 FastAPI에서 `main.py`라는 이름을 많이 쓰는 건,

“서버 시작점 파일로 main.py라는 이름을 쓰자”는 **팀/커뮤니티 관례**일 뿐이야.

FastAPI 자체 요구 사항은 아니고, `app.py:app`, `server:api` 이런 식으로 바꿔도 된다.

`ExtractorSvc = Annotated[ExtractorService, Depends(get_extractor_service)]`

각 구성 요소와 용도를 자세히 설명해 드릴게요.

---

## 🧐 주요 구성 요소 및 의미

### 1. `ExtractorSvc`

- **의미:** 이 구문 전체의 **별칭(Alias)** 또는 **타입 정의**입니다.
- **용도:** FastAPI 경로 함수(Path Operation Function)의 매개변수에 이 `ExtractorSvc`를 타입 힌트로 사용하면, FastAPI는 이 별칭에 정의된 의존성을 주입하게 됩니다. 함수 내에서는 `ExtractorService` 객체로 접근하게 됩니다.

### 2. `ExtractorService`

- **의미:** 주입하려는 **실제 클래스** 또는 **타입**입니다. (예: 데이터 추출 로직을 담당하는 서비스 클래스)
- **용도:** 주입이 완료된 후, 경로 함수 내에서 이 타입의 **인스턴스(Instance)**를 사용하게 됩니다.

### 3. `Depends(get_extractor_service)`

- **의미:** FastAPI의 **의존성 주입 메커니즘**을 지정하는 함수입니다. `get_extractor_service`는 **호출 가능한(Callable)** 객체(함수 또는 클래스)여야 하며, 이 함수가 실제로 `ExtractorService`의 인스턴스를 **반환**합니다.
- **용도:** FastAPI에게 "경로 함수를 호출하기 전에, `get_extractor_service()`를 호출해서 반환된 객체를 준비해 줘"라고 지시합니다. 이 `get_extractor_service` 함수 내에서 서비스 객체를 생성하거나, 데이터베이스 연결 등 필요한 초기화 작업을 수행할 수 있습니다.

### 4. `Annotated[...]` 🆕

- **의미:** 파이썬 **3.9 이상**에서 도입된 `typing` 모듈의 특별한 타입으로, **메타데이터(Metadata)**를 타입 힌트에 **첨부**할 수 있게 해줍니다.
- **용도:** `[Type, Metadata1, Metadata2, ...]` 형태로 사용되며, 여기서는 `ExtractorService`라는 **타입**에 `Depends(get_extractor_service)`라는 **메타데이터(FastAPI에게 전달할 정보)**를 연결하는 역할을 합니다.
- **FastAPI에서의 역할:** FastAPI는 경로 함수 매개변수의 타입 힌트에서 `Annotated`를 발견하면, 첫 번째 요소(`ExtractorService`)를 **타입**으로 인식하고, 두 번째 이후의 요소(`Depends(...)`)를 해당 타입에 적용할 **의존성 주입 로직**으로 사용합니다.

## 🎯 전체적인 용도 (왜 이렇게 사용할까요?)

이 코드는 **FastAPI의 의존성 주입**을 깔끔하게 정의하는 최신 방식이며, 특히 라이브러리/프레임워크 관련 메타데이터(여기서는 `Depends`)를 **타입 정의 자체**에 포함시켜 코드를 더 간결하게 만듭니다.

1. **코드 간결화:** 경로 함수 내에서 주입 코드가 깔끔해집니다.
    - **전통적인 방식:** `svc: ExtractorService = Depends(get_extractor_service)`
    - **`Annotated` 방식:** `svc: ExtractorSvc` (이미 타입 정의에 `Depends` 로직이 포함되어 있음)
2. **재사용성 및 명확성:** 복잡한 의존성 로직을 한 번 정의하고(`ExtractorSvc`), 여러 경로 함수에서 재사용할 수 있습니다.
3. **테스트 용이성:** `get_extractor_service` 함수를 Mocking(가짜 객체로 대체)하여 서비스 로직을 쉽게 테스트할 수 있습니다.

결론적으로, 이 구문은 **"경로 함수에 `ExtractorSvc` 타입의 객체가 필요하면, `get_extractor_service` 함수를 호출하여 그 반환값을 주입해줘"**라고 FastAPI에게 지시하는 **의존성 주입 정의**입니다.

---

## 🛠️ 의존성 주입(DI)의 쉬운 정의

의존성 주입을 이해하기 위해 가장 흔히 사용되는 비유는 **레스토랑 주방** 비유입니다.

### 🍳 비유: 레스토랑 주방

| 구성 요소 | DI를 사용하지 않을 경우 (Self-reliant) | DI를 사용할 경우 (Injection) |
| --- | --- | --- |
| **요리사 (객체)** | 칼이 필요하면 **요리사가 직접 칼을 사러** 마트에 갑니다. | 칼이 필요하면 **주방 매니저(외부 시스템)**가 **미리 준비된 칼**을 요리사에게 건네줍니다. |
| **칼 (의존성)** | 요리사가 책임지고 **생성**하고 **관리**합니다. | 외부 시스템이 책임지고 **생성**하고 **관리**합니다. |
| **주방 매니저 (DI 컨테이너)** | 해당 역할이 없습니다. | 의존성(칼)을 준비하고 필요한 객체(요리사)에게 **주입**합니다. |

### 📝 핵심 요약

- **의존성(Dependency):** 어떤 객체(A)가 다른 객체(B)를 작동시키는 데 필요로 하는 **부품**이나 **서비스**를 말합니다. (예: `User` 객체가 `DatabaseConnector` 객체를 필요로 할 때, `DatabaseConnector`가 의존성입니다.)
- **주입(Injection):** 의존성(B)을 필요로 하는 객체(A) **내부**에서 직접 만들지 않고, **외부**에서 객체(A)의 생성자나 메서드를 통해 전달해주는 행위를 의미합니다.

---

## ✅ DI를 사용하는 이유

DI는 다음과 같은 중요한 장점을 제공합니다.

1. **결합도(Coupling) 감소:** 객체 A와 B가 서로 직접 생성하는 방식으로 엮여 있으면 변경하기 어렵지만, DI를 통해 외부에서 연결하면 독립적으로 개발하고 수정하기 쉬워집니다. **유연성**이 높아집니다.
2. **테스트 용이성:** 실제 데이터베이스 커넥터 대신 가짜(Mock) 커넥터를 쉽게 **주입**하여, 실제 데이터베이스에 접근하지 않고도 객체(서비스)의 로직만 테스트할 수 있습니다.
3. **재사용성 증가:** 같은 부품(의존성)을 여러 객체에서 공유하거나, 필요에 따라 다른 버전의 부품으로 쉽게 **교체**할 수 있습니다. (예: 개발 환경에서는 메모리 DB를, 운영 환경에서는 실제 DB를 주입)

## 🔁 FastAPI의 의존성 주입과 동작 방식

FastAPI에서 `Depends(get_extractor_service)`를 사용했을 때 일어나는 일입니다.

1. **경로 함수 호출 시점:** 사용자가 FastAPI 애플리케이션에 요청을 보내고, 특정 경로 함수(Path Operation Function)가 호출되어야 할 때.
2. **`get_extractor_service` 호출:** FastAPI는 경로 함수의 매개변수 타입(여기서는 `ExtractorSvc`)에 연결된 의존성 주입 함수, 즉 **`get_extractor_service()`*를 호출합니다.
3. **새 인스턴스 생성:** 특별한 설정을 하지 않았다면, 이 `get_extractor_service` 함수는 요청이 들어올 때마다 실행되어 **새로운 `ExtractorService` 인스턴스**를 생성하고 반환합니다.
4. **주입:** FastAPI는 이 새로운 인스턴스를 경로 함수의 매개변수에 주입하여 함수를 실행합니다.

### 💡 정리: 기본 동작은 **"요청당 새 인스턴스"**

FastAPI의 `Depends`의 **기본 범위(Scope)**는 **요청 범위(Request Scope)**입니다.

- **요청이 들어올 때마다** → `Depends` 함수가 **실행**됩니다.
- **실행될 때마다** → 보통 **새로운 인스턴스**를 반환합니다.

이는 각 요청이 독립적인 서비스 인스턴스를 가지게 하여, 한 요청의 상태가 다른 요청에 영향을 미치지 않도록 (**Thread Safety**) 보장하는 안전한 방식입니다.

---