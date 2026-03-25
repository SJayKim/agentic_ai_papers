# From Local to Global: A Graph RAG Approach to Query-Focused Summarization

> **논문 정보**: Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley 외 (Microsoft Research)
> **arXiv**: 2404.16130 (2024.04)
> **코드**: https://github.com/microsoft/graphrag

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 벡터 RAG는 문서 컬렉션에서 특정 정보를 검색하는 데 효과적이지만, "이 데이터셋의 주요 주제는 무엇인가?" 같은 전체 코퍼스에 대한 글로벌 질문(sensemaking query)에는 근본적으로 실패한다. 이는 검색 태스크가 아닌 질의 중심 요약(QFS) 태스크이기 때문. |
| **Motivation** | 센스메이킹(사람·장소·사건 간 연결을 추론하여 궤적을 예측)은 과학적 발견, 정보 분석 등에서 핵심적이다. LLM은 센스메이킹에 뛰어나지만, 대규모 코퍼스에서는 컨텍스트 윈도우 제한으로 전체를 처리할 수 없다. 기존 QFS 방법은 RAG 규모로 확장되지 않는다. |
| **Limitation** | 저자 언급: 인덱싱 비용이 높음(LLM으로 엔티티 추출, 커뮤니티 요약 생성). 독자 관점: 로컬 질문(특정 엔티티에 대한 구체적 질문)에서는 벡터 RAG가 여전히 효율적. 커뮤니티 탐지 알고리즘(Leiden)의 파라미터에 따라 요약 품질이 크게 달라짐. 증분 업데이트 메커니즘 미제공. |

---

## Method

1. **인덱싱 파이프라인 (오프라인)**
   - **Text Chunks → Entities & Relationships**: LLM이 각 텍스트 청크에서 엔티티(인물, 장소, 조직)와 관계를 추출. 도메인 맞춤 few-shot 프롬프트로 추출 품질 조정 가능. 클레임(사실 진술)도 추가 추출
   - **Entities → Knowledge Graph**: 중복 엔티티/관계를 집계하여 그래프의 노드·엣지로 통합. 관계 중복 횟수가 엣지 가중치
   - **KG → Graph Communities**: Leiden 커뮤니티 탐지를 계층적으로 적용하여 밀접한 엔티티 그룹을 재귀적으로 분할
   - **Communities → Community Summaries**: LLM이 각 커뮤니티의 노드·엣지·클레임 설명을 입력받아 보고서형 요약 생성. 상위 커뮤니티는 하위 요약을 재귀적으로 통합

2. **쿼리 처리 (Map-Reduce)**
   - **Map**: 각 커뮤니티 요약이 독립적·병렬적으로 쿼리에 대한 부분 응답 생성
   - **Reduce**: 모든 부분 응답을 종합하여 최종 글로벌 답변 생성

3. **적응형 벤치마킹**: LLM이 코퍼스 특화 사용 사례 기반으로 글로벌 센스메이킹 질문을 자동 생성, 별도 LLM이 두 시스템의 답변을 비교 평가

---

## Key Contribution

1. **글로벌 센스메이킹을 위한 그래프 기반 RAG**: 엔티티 지식 그래프 + 커뮤니티 탐지 + 계층적 요약으로 전체 코퍼스의 주제와 패턴을 파악하는 최초의 체계적 접근
2. **커뮤니티 요약의 사전 생성**: 쿼리 시점에 전체 그래프를 탐색하지 않고, 사전 생성된 커뮤니티 요약을 map-reduce로 활용하여 확장성 확보
3. **오픈소스 생태계 구축**: Microsoft GraphRAG + LangChain, LlamaIndex, Neo4J 등 주요 프레임워크에 통합

---

## Experiment & Results

- **데이터셋**: 2개 실세계 텍스트 코퍼스 (백만 토큰 규모)
- **비교**: GraphRAG vs Vector RAG (나이브 청크 검색)
- **평가**: LLM-as-a-judge로 포괄성(comprehensiveness)과 다양성(diversity) 비교

**GPT-4 기반 평가**:
- GraphRAG가 포괄성과 다양성 모두에서 Vector RAG를 일관되게 초과
- 글로벌 질문("주요 트렌드는?", "핵심 주제는?")에서 GraphRAG의 답변이 더 많은 측면을 커버하고 다양한 관점을 포함
- 커뮤니티 수준 조정: 상위 커뮤니티(추상적)는 넓은 커버리지, 하위 커뮤니티(세부적)는 깊은 분석 제공

**인덱싱 비용**: 엔티티 추출과 커뮤니티 요약에 상당한 LLM 호출 필요 — 하지만 쿼리 시에는 요약만 활용하므로 응답 속도는 빠름
