---
title: FastAPI
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# FastAPI

# 핵심 키워드

Pydantic Model, 레이어드 아키텍처, 의존성 주입(DI), Micro service archicheture (MSA), Callable 타입, Annotated, Field

## FastAPI 아키텍처 / 패턴

FastAPI 자체는 특정 아키텍처(예: MVC, Hexagonal 등)를 강제하지 않아. 대신 FastAPI가 준 것들은 딱 두 가지야:

1. **APIRouter 기반 라우팅** → “Controller” 같은 역할
2. **Dependency Injection(Depends)** → “이 함수는 이런 리소스를 필요로 해”라고 선언적으로 주입

여기에 우리가 일반적으로 입히는 패턴은 아래 셋이 많아.

---

### 1) 레이어드 아키텍처 (Controller / Service / Repository)

가장 흔하고 현실적인 구조. 위에서 본 (C) 구조가 바로 이거.

- **Router (Controller 역할)**
    - HTTP 세부사항 처리 (경로, status code, body 파싱, response_model)
- **Service (Domain / Use Case)**
    - 비즈니스 규칙
    - 트랜잭션 경계 설정(성공 시 commit, 실패 시 rollback)
    - 여러 repository 호출을 조합
- **Repository (Data Access Layer)**
    - ORM/SQL 구체 구현
    - DB 변경이 여기서만 일어난다

장점:

- 책임 분리가 분명함
- 테스트 용이
- 대부분의 백엔드 팀이 이해하기 쉬움
- FastAPI + SQLAlchemy/SQLModel 튜토리얼도 이 구조로 확장하기 편함

사실상 FastAPI의 “사실상 표준”에 가장 가깝다.

### 2) Domain-driven / 모듈 단위로 세로 쪼개기

이건 한 층씩(horizontal) 나누는 게 아니라, “도메인 단위(feature 단위)로 묶자”는 접근.

- **Repository (DAO)**
    - DB랑만 대화한다.
    - 반환값은 UserEntity 같은 ORM 객체.
- **Service**
    - 비즈니스 규칙 처리 (중복 이메일 검사, 권한 로직 등)
    - Repository에서 받은 UserEntity를 **DTO(Pydantic 모델)**로 변환해서 밖으로 준다.
    - 즉, 서비스 레이어가 “외부로 나갈 수 있는 안전한 형태”로 정제하는 마지막 방어선.
- **Controller / Router**
    - Service에서 받은 DTO를 그냥 리턴한다.
    - FastAPI는 그걸 `response_model=UserRead` 같은 걸로 다시 한 번 스키마화해서 응답에 사용.

# 레이어드 아키텍처

레이어드 아키텍처란 소프트웨어 시스템을 관심사 별로 여러개의 계층으로 분리(계층화)한 아키텍처를 뜻한다.

각 계층은 어플리케이션 내에서 특정 역할과 책임이 있다.
그 들은 자신의 역할에만 집중한다. 여기서 중요한 것은 구성 요소간 관심사가 분리 되었다는 점이다.

이들은 추상화된 인터페이스로만 소통한다.
이 때, 소통은 자신에게 인접한 하위 계층에 요청을 보내는 방식으로 진행된다.

# 큰 구조

- 요청이 들어오면 `router`가 받는다 → `service`에 비즈니스 의사결정을 맡긴다 → `service`는 `repository`를 이용해 실제 데이터를 읽거나/쓰기 한다 → `repository`는 지금은 in-memory seed 리스트(`db/database.py`)를 조작한다.
- 에러/검증은 주로 `service`에서 도메인 예외로 던지고, `router`가 그걸 HTTP 상태코드로 바꿔서 응답한다.

# 트랜잭션 처리

[https://jd6186.github.io/FastAPI_Transaction/](https://jd6186.github.io/FastAPI_Transaction/)

[Python](FastAPI/Python%2029bcee38e89a80bb88cfe37987763a71.md)

# Swagger Docs보안

## 실무에서 보통 어떻게 하냐?

- 로컬/개발 환경(dev): `docs_url="/swagger"` 같이 열어둠
- 운영(prod): 아예 `docs_url=None`, `redoc_url=None` 으로 막아두거나, JWT 등 인증된 사용자만 볼 수 있는 커스텀 라우트(`/swagger`)로 감싼다
- OpenAPI JSON(`/openapi.json`)은 프론트/QA팀이 쓰니까 보통은 계속 유지한다
    
    

# Exception 처리

1. **입력 자체가 잘못된 경우**
    - path param 타입 안 맞음
    - query/body 스키마 안 맞음
    - 필수 필드 누락
    - 이메일 형식 아님
        
        → FastAPI + Pydantic이 자동으로 422 응답.
        
        → try/except 안 해도 돼.
        
2. **입력은 문법적으로 맞는데, 도메인에서 문제가 되는 경우**
    - 해당 user_id가 DB에 없음 → 404
    - 권한 없음 → 403
    - 이미 존재하는 이메일이라서 가입 불가 → 400
        
        이런 건 Pydantic이 절대 모름.
        
        → 우리가 처리해야 해.
        
        → 라우터에서 처리하거나, 전역 예외 핸들러 만들어서 처리.
        

# 로깅

## OpenTelemetry Semantic Conventions

필드명으로 도구 간 호환성 확보하고, 컨텍스트를 로거가 자동 주입 받으면 좋겠어.

## 

# FastAPI 의존성

## 의존성

## 의존성 주입

필요한 특정 정보를 함수에 전달하는 것. 이를 수행하는 전통적인 방법은 헬퍼 함수이며 ,이를 호출해 특정 데이터를 가져온다. 

# Select할 때, Join tip

- **간단한 관계 / 연관 객체 수가 적은 1:1, 소규모 1:N**
    - `joinedload` 자주 씀
    - 예: 유저 + 프로필, 글 + 작성자
- **연관 객체가 많아질 수 있는 1:N, N:M**
    - 기본은 `selectinload` 추천
    - 예: 글 + 댓글, 유저 + 주문 목록, 주문 + 주문 아이템들
- **특정 관계는 이 화면에서 절대 안 쓰는 경우**
    - `noload`, `raiseload`로 아예 차단하거나 에러로 막기
- **N+1 문제가 보이면**
    - 프로파일링 / 로그에서 쿼리 수 확인 → 문제 나는 관계에 `selectinload` or `joinedload` 붙여보기
- **정렬**: `select(...).order_by(Model.col.desc())`
- **ORM 엔티티/단일 컬럼 select**:
    
    → **`session.scalars(stmt)`** 사용이 2.0 스타일에서 가장 추천
    
- **스칼라 값 하나(집계 등)**:
    
    → `session.scalar(stmt)`
    
- **복잡한 튜플/여러 컬럼/Raw 느낌**:
    
    → `session.execute(stmt)`
    
    - **joinedload**:
        
        👉 *한 번의 큰 JOIN 쿼리로 다 가져오기*
        
    - **selectinload**:
        
        👉 *먼저 부모만 가져오고, 그 부모들 ID 모아서 2차 SELECT로 자식들 한 번 더 가져오기*
        

### ✅ joinedload 추천 상황

- 관계가 **many-to-one / one-to-one** 이고,
    - 예: `TermEntity.src_lang`, `TermVariantEntity.domain` 처럼 “딱 하나만 매핑”되는 관계
- 부모 개수가 적고, 조인해도 row 폭발이 걱정 안 될 때
- 자식 기준으로 필터링/정렬을 같이 써야 할 때

### ✅ selectinload 추천 상황

- **one-to-many / many-to-many 컬렉션 관계** (리스트, 컬렉션)
    - 예: `TermEntity.variants`, `GlossaryEntity.concepts`
- 리스트/페이지네이션 있는 화면:
    - “Term 50개 가져오고, 각 Term의 variants도 보고 싶다” 같은 경우
- JOIN하면 row 수가 **기하급수적으로 늘어날 수 있는 상황** (카디널리티 높음)

[Pydantic ](FastAPI/Pydantic%2029bcee38e89a80539d1fe0555b9fc0ed.md)

[Alembic](FastAPI/Alembic%202bccee38e89a8067be2aeb587ce9616c.md)

[Application lock](FastAPI/Application%20lock%202c6cee38e89a80b1a50be1a2da4e5c88.md)