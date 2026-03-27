# Agentic RAG with Knowledge Graphs for Complex Multi-Hop Reasoning

> **논문 정보**: Jean Lelong, Adnane Errrazine, Annabelle Blangero (Ekimetrics, France)
> **arXiv**: 2507.16507 (2025.07)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 RAG는 top-k 벡터 검색으로 제한적인 텍스트 스니펫만 반환하여, 완전한 목록(예: 특정 저자의 모든 논문), 다중 데이터 포인트 통합, 복잡한 관계 경로 탐색(저자→논문→펀딩 프로젝트)이 필요한 쿼리에 부적합하다. |
| **Motivation** | 지식 집약적 도메인(과학 데이터)에서는 단순 스니펫 추출이 아닌, 인간 연구자처럼 증거를 수집·평가하고 후속 검색을 계획하는 반복적 탐구가 필요하다. 지식 그래프의 구조화된 관계와 에이전트의 동적 추론을 결합하면 이를 달성할 수 있다. |
| **Limitation** | 저자 언급: 특정 기관(INRAE) 데이터에 특화된 구현으로 일반화 가능성이 제한됨. 독자 관점: 에이전트가 Cypher 쿼리를 직접 생성해야 하므로 LLM의 Cypher 문법 이해에 의존하며 오류 가능성 존재. 정량적 벤치마크 비교 없이 정성적 시연에 그쳐 객관적 성능 평가 불가. 대규모 그래프 탐색 시 지연 시간 및 비용 문제 미검토. |

---

## Method

1. **지식 베이스 구축 (Knowledge Base Construction)**
   - 데이터 범위: INRAE의 2019년 1월 ~ 2024년 8월 오픈액세스 출판물
   - **벡터 DB**: 출판물 텍스트(제목 + 초록 + 결론)를 텍스트 청크로 변환
     - Dense vector: Jina v3 임베딩 모델 (시맨틱 유사도)
     - Sparse vector: BM25 알고리즘 (키워드 기반 매칭)
     - 하이브리드 결과는 Cohere 리랭커로 통합·재정렬
   - **Knowledge Graph (Neo4j)**: 417,030 노드 + 100만+ 관계로 구성
     - Author 233,728 (56.0%), Keyword 96,588 (23.2%), Publication 38,791 (9.3%), Software 21,617 (5.2%), Concept 13,591 (3.3%), Journal 5,563 (1.3%), Project 3,999 (1.0%) 등 11개 노드 타입
   - **PDF 파싱**: GROBID 도구로 출판물 원문 처리 및 구조화

2. **에이전트 기반 멀티툴 오케스트레이션**
   - 백본 LLM: deepseek-r1-0528 (open-weight reasoning model)
   - 오케스트레이션 프레임워크: Mirascope, 벡터 스토리지: Qdrant
   - 에이전트 책임: 쿼리 이해 → 분해 → 실행 계획 수립 → 도구 동적 선택·호출 반복 → 수집 정보 종합 → 응답 생성

3. **전문화 도구 집합 (Specialized Tool Suite)**
   - **SearchGraph**: Neo4j KG에 Cypher 쿼리 전송 → 특정 엔티티 검색, 관계 경로 탐색, 완전한 목록 검색
   - **SearchPublications**: 벡터 DB에서 하이브리드 검색(semantic + keyword) → KG 탐색의 초기 진입점 식별
   - **SearchConceptsKeywords**: KG 내 개념·키워드 검색 → 쿼리와 KG 구조화 어휘 간 간극 해소
   - **IdentifyExperts**: 복합 전문성 점수(논문 관련도, 상위 10% 논문 수, 인용 수, 활동 기간, 최근 발표 시점 등 가중 지표) 기반 전문가 순위화

4. **다중 홉 추론 프로세스**
   - Step 1: SearchPublications로 관련 출판물 초기 집합 식별
   - Step 2: SearchGraph로 저자 및 연관 프로젝트 추출 (Author → Publication → Project 경로)
   - Step 3: SearchGraph로 프로젝트 연결 Concept 노드를 DESCRIBES 관계로 탐색
   - Step 4: Author → Publication → Project → Concept 체인으로 구조화된 종합 응답 생성

---

## Key Contribution

1. **에이전틱 KG 쿼리의 실세계 적용**: 417K+ 노드 및 100만+ 관계 규모의 실세계 KG를 대상으로, 에이전트가 동적으로 탐색하며 반복적 다중 홉 추론을 수행하는 INRAExplorer 시스템 구현
2. **Map-reduce 요약과의 차별화**: GraphRAG 스타일의 사전 요약 대신, 에이전트가 실시간으로 증거를 수집·평가·계획하는 "인간 연구자" 패러다임 채택
3. **모듈형 전문 도구 설계**: IdentifyExperts처럼 복잡한 도메인 로직을 캡슐화한 고수준 도구와 저수준 도구(SearchGraph)의 혼합으로 유연성과 신뢰성 동시 달성
4. **오픈소스 기반 아키텍처**: Mirascope, Qdrant, Neo4j, GROBID, deepseek-r1-0528 등 오픈소스 컴포넌트만으로 구성하여 다른 도메인으로의 이식성 제공

---

## Experiment & Results

- **시스템**: INRAExplorer — INRAE 과학 데이터 (2019.01~2024.08 오픈액세스 출판물)
- **KG 규모**: 417,030 노드, 1,000,000+ 관계, 11개 노드 타입
- **출판물**: Publication 노드 38,791개, Author 노드 233,728개

정성적 시연으로 시스템 능력을 보여줌 (정량 벤치마크 없음):

- **완전한 목록 검색**: "특정 저자의 모든 논문 목록" → SearchGraph가 Cypher 쿼리로 완전한 목록 반환. 기존 top-k RAG 대비 누락 없는 exhaustive retrieval 달성
- **다중 홉 관계 탐색**: "climate change adaptation 연구 관련 프로젝트 및 소프트웨어" → Author→Publication→Project→Concept 4단계 경로 탐색으로 구조화 응답 생성
- **교차 도메인 전문가 식별**: "zoonoses 분야 INRAE 전문가 식별" → 6개 가중 지표 기반 복합 점수로 전문가 순위화

기존 classical RAG 대비 완전성(exhaustiveness)과 구조화된 응답에서 질적 우위를 보임. 단, 공개 벤치마크 대비 정량적 비교 실험은 미수행.
