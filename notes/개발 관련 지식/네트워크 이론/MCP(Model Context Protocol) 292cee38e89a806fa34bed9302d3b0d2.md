---
title: MCP(Model Context Protocol)
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# MCP(Model Context Protocol)

- **정의:** LLM(예: ChatGPT, Claude)을 **외부 데이터·툴**(DB, 파일, SaaS API 등)과 **표준 방식**으로 연결하는 오픈 프로토콜. “AI용 USB-C” 비유가 자주 쓰임. [Model Context Protocol+1](https://modelcontextprotocol.io/?utm_source=chatgpt.com)
- **전송/형식:** **JSON-RPC 2.0** 기반 메시지로 **호스트(LLM 앱) ↔ 클라이언트(커넥터) ↔ 서버(툴/데이터 제공자)**가 대화. **LSP**(Language Server Protocol)에서 영감. [Model Context Protocol](https://modelcontextprotocol.io/specification/2025-03-26)
- **구성요소(서버가 제공):**
    1. **Resources**: 파일/레코드 같은 읽기 전용 **컨텍스트 데이터**
    2. **Prompts**: 미리 정의된 **프롬프트 템플릿/워크플로**
    3. **Tools**: 모델이 **실행**할 수 있는 함수(예: `search_orders`, `create_ticket`)
        
        (클라이언트가 제공 가능한 기능: **Sampling** = 서버가 LLM 상호작용을 요청하는 패턴) [Model Context Protocol](https://modelcontextprotocol.io/specification/2025-03-26)
        
- **보안/신뢰 원칙:** **명시적 사용자 동의**, 데이터 최소 공유, **툴 실행 전 승인**, 진행상황/취소/로깅 등 권장. [Model Context Protocol](https://modelcontextprotocol.io/specification/2025-03-26)

> 누가 만들었고 누가 쓰나?
> 
> 
> 2024년 말 **Anthropic**이 공개한 오픈 표준이고, 현재 **OpenAI Agents SDK** 등에서도 **MCP 서버/클라이언트**를 지원하는 흐름이야.
> 

참고: [https://wikidocs.net/286230](https://wikidocs.net/286230)