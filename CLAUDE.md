# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요
CrewAI Flow를 활용한 콘텐츠 생성 파이프라인 에이전트입니다. 블로그 포스트, 트윗, LinkedIn 포스트를 자동으로 생성하고 품질을 검증하는 워크플로우를 제공합니다.

## 환경 설정

### 의존성 설치
```bash
uv sync
```

### 필수 환경 변수
`.env` 파일에 다음 환경 변수가 필요합니다:
- `OPENAI_API_KEY`: OpenAI API 키 (GPT-4o-mini 모델 사용 시 필요)
- `GEMINI_API_KEY`: Google Gemini API 키 (Gemini 2.0 Flash Exp 모델 사용 시 필요)
- `FIRECRAWL_API_KEY`: Firecrawl API 키 (웹 검색 및 스크래핑)

### 실행
```bash
uv run python main.py
```

## 아키텍처

### CrewAI Flow 패턴
이 프로젝트는 CrewAI의 Flow 시스템을 기반으로 합니다:

- **State Management**: `ContentPipelineState` (Pydantic BaseModel)이 전체 파이프라인의 상태를 관리
- **Flow Decorators**:
  - `@start()`: 파이프라인의 진입점
  - `@listen()`: 이전 단계 완료 후 실행
  - `@router()`: 조건부 라우팅 (다음 단계 결정)
  - `and_()`, `or_()`: 복수 단계 조합

### 주요 워크플로우 단계

1. **init_content_pipeline**: 콘텐츠 타입 검증 및 최대 길이 설정
2. **conduct_research**: Agent를 사용한 주제 리서치 (web_search_tool 활용)
3. **conduct_research_router**: 콘텐츠 타입에 따라 다음 단계 라우팅
4. **Content Creation**:
   - `handle_make_blog`: 블로그 포스트 생성/개선 (LLM structured output 사용)
   - `handle_make_tweet`: 트윗 생성/개선
   - `handle_make_linkedin_post`: LinkedIn 포스트 생성/개선
5. **Quality Check**:
   - `check_seo`: 블로그 SEO 점수 확인
   - `check_virality`: 트윗/LinkedIn 바이럴성 확인
6. **score_router**: 품질 점수에 따라 재생성 또는 완료
7. **finalize_content**: 최종 콘텐츠 출력

### 핵심 컴포넌트

#### State Models (main.py)
- `BlogPost`: title, subtitle, sections
- `Score`: value, reason
- `Tweet`: content, hashtags
- `LinkedInPost`: hook, content, call_to_action
- `ContentPipelineState`: 전체 파이프라인 상태
  - `llm_provider`: LLM 제공자 선택 ("openai" 또는 "gemini")

#### Tools (tools.py)
- `web_search_tool`: Firecrawl을 사용한 웹 검색 및 마크다운 스크래핑
  - 검색 결과를 클린업하여 제목, URL, 마크다운 콘텐츠 반환
  - URL과 마크다운 링크 제거 처리

#### LLM Structured Output
- `LLM.call(prompt, response_model=BlogPost)` 패턴을 사용하여 Pydantic 모델로 직접 응답 받기
- LLM 제공자 선택 가능:
  - OpenAI: `gpt-4o-mini`
  - Google Gemini: `gemini-2.0-flash-exp` (기본값)
- `llm_provider` 파라미터로 실행 시 선택 ("openai" 또는 "gemini")
- **중요**: `llm.call()`의 반환 타입은 문자열(JSON)일 수 있으므로 `isinstance()` 체크 후 파싱 필요

#### SEO Crew (seo_crew.py)
- `SeoCrew`: CrewAI의 `@CrewBase` 데코레이터를 사용한 SEO 분석 Crew
- `seo_expert`: SEO 전문가 Agent
- `seo_audit`: 블로그 포스트 SEO 분석 Task
  - 0-10 점수 평가 및 이유 제공
  - `output_pydantic=Score`로 구조화된 출력
- **주의**: Task의 `agent` 파라미터에 `self.agent_name()` 형태로 호출 필요

### 개발 시 주의사항

1. **Flow Listener 순서**: `@listen()` 데코레이터는 메서드 정의 순서와 무관하게 Flow 그래프에 따라 실행됩니다.

2. **Router 반환값**: `@router()` 메서드는 문자열을 반환하며, 이 문자열은 다음 `@listen()` 단계의 이름과 매칭됩니다.

3. **State 수정**: `self.state`를 직접 수정하여 파이프라인 전체에서 상태를 공유합니다.

4. **Agent vs LLM**:
   - Research 단계: Agent 사용 (도구 활용 가능)
   - Content Creation: LLM 직접 호출 (structured output)

5. **Content Type**: "blog", "tweet", "linkedin" 세 가지만 지원

## 파일 구조
- `main.py`: 메인 Flow 정의 및 실행
- `seo_crew.py`: SEO 분석을 위한 CrewAI Crew 정의
- `tools.py`: CrewAI 도구 정의 (web_search_tool)
- `flow_sample.py`: Flow 패턴 학습용 샘플 코드
- `.env`: API 키 환경 변수

## 구현 완료 기능

✅ **콘텐츠 생성**
- 블로그 포스트 생성 (LLM structured output)
- 트윗 생성 (LLM structured output)
- LinkedIn 포스트 생성 (LLM structured output)

✅ **품질 검증**
- 블로그 SEO 점수 확인 (SeoCrew 사용)
- Score 기반 자동 재생성 로직 (score < 8일 경우)

✅ **기타**
- 웹 검색을 통한 리서치 (Firecrawl)
- OpenAI/Gemini 선택 가능

## 미구현 기능

❌ **품질 검증**
- 트윗 바이럴성 체크 (placeholder만 존재)
- LinkedIn 포스트 바이럴성 체크 (placeholder만 존재)
