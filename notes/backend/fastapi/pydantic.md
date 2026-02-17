---
title: Pydantic
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Pydantic

# 핵심 키워드

Basemodel, model_copy, model_dump 

# 어떤것인가?

Pydantic은 "데이터 검증 + 변환"을 해주는 Python 라이브러리야.

즉, 아무 형태로 들어온 데이터를 우리가 정의한 스키마(모델)에 맞게:

- 타입 체크하고
- 잘못된 값이면 에러 던지고
- 가능한 건 자동으로 변환까지 해줘.

FastAPI는 이걸 기반으로 요청 JSON → Python 객체 변환, 응답 JSON 스키마 문서화까지 전부 돌려.

- **유효성 검사** (필수 필드, 타입, 형식) 자동화
- **데이터 파싱/타입 변환** 자동화
- **응답 직렬화/필드 필터링** 자동화
- **API 문서(OpenAPI/Swagger) 자동 생성에 바로 연결**
- **router ↔ service 경계에서 신뢰 가능한 데이터만 흘러가게 하는 방화벽**

# 기본 사용 형태

Pydantic에서는 보통 `BaseModel`을 상속해서 "데이터 모델"을 정의해.

```
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class User(BaseModel):
    id: UUID
    email: str
    is_active: bool = True        # 기본값 가능
    created_at: datetime
```

이건 "User라는 데이터는 이런 구조여야 한다"를 선언한 거야.

# BaseModel이란

`BaseModel`은 Pydantic 모델의 부모 클래스야. 하는 일은:

- 필드 타입 힌트 읽어서 validation rule로 바꿔줌
- 기본값 처리
- `.model_dump()`, `.model_dump_json()` 같은 유틸 제공
- `.model_validate()` (raw 데이터 → 모델 인스턴스 검증) 제공

즉, 우리가 "데이터 스키마" 만들 땐 거의 무조건 `class Something(BaseModel):` 패턴 쓴다고 보면 돼.

# 어떻게 동작하는가?

(1) 인스턴스를 만들면, 알아서 검증이 돼

```jsx
from uuid import uuid4
from datetime import datetime

u = User(
    id=uuid4(),
    email="test@example.com",
    is_active="true",
    created_at="2025-10-29T10:00:00",
)

print(u)
```

## dict / JSON으로 주고받기

Pydantic 모델은 응답으로 JSON 뽑기 쉬워.

```
u_dict = u.model_dump()        # 파이썬 dict
u_json = u.model_dump_json()   # JSON 문자열

print(u_dict)
print(u_json)
```

# 유효성 검사

## 필드 옵션 (유효성 제약 추가)

Pydantic은 단순히 타입만 있는 게 아니라 제약도 걸 수 있어.

```
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr            # 이메일 형식 검증
    password: str = Field(min_length=8, max_length=64)
    nickname: str | None = Field(default=None, max_length=20)
```

의미:

- `EmailStr`: 그냥 `str` 아니고 이메일 포맷인지 검사해줌
- 비밀번호 최소/최대 길이 검증
- nickname은 optional이고 길이 제한 있음

이거 덕분에 “이건 필수야?” “몇 글자까지 가능해?” 같은 백엔드 규칙이 코드에서 명시적으로 문서화되고, 동시에 자동으로 검증까지 가능해.

## 부분 업데이트(PATCH)에서 유용한 패턴: exclude_unset

우리가 PATCH용 모델을 만들고 나서 DB에 반영할 때 자주 쓰는 패턴이 이거야:

```
class UserUpdate(BaseModel):
    email: str | None = None
    is_active: bool | None = None

payload = UserUpdate(email="new@example.com")

update_data = payload.model_dump(exclude_unset=True)
# {'email': 'new@example.com'}
# is_active는 안 들어옴 (안 보냈으니까)

# 이제 update_data만 DB UPDATE에 반영하면 안전
```

이 방식이 "builder처럼 전체를 만들고 내가 바꾼 것만 반영"이라는 너 질문이랑 사실상 동일한 해결책이야.

핵심은:

- PATCH용 모델 따로 둔다 (`UserUpdate`)
- 컨트롤할 때 `exclude_unset=True`로 클라이언트가 실제로 전송한 필드만 뽑는다

# 직렬화 시에는, 아래 타입이 권장됨

- dict, list