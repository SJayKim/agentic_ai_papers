# From Local to Global: A Graph RAG Approach to Query-Focused Summarization

> **논문 정보**: Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley 외 (Microsoft Research)
> **arXiv**: 2404.16130 (2024.04)
> **코드**: https://github.com/microsoft/graphrag

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 벡터 RAG는 문서 컬렉션에서 특정 정보를 검색하는 데 효과적이지만, "이 데이터셋의 주요 주제는 무엇인가?" 같은 전체 코퍼스에 대한 글로벌 질문(sensemaking query)에는 근본적으로 실패한다. 이는 검색 태스크가 아닌 질의 중심 요약(QFS) 태스크이기 때문. 반면 기존 QFS 방법은 RAG 규모의 텍스트를 처리할 만큼 확장되지 않는다. |
| **Motivation** | 센스메이킹(사람·장소·사건 간 연결을 추론하여 궤적을 예측)은 과학적 발견, 정보 분석 등에서 핵심적이다. LLM은 센스메이킹에 뛰어나지만, 대규모 코퍼스에서는 컨텍스트 윈도우 제한으로 전체를 처리할 수 없다. 그래프 기반 커뮤니티 구조를 사전 인덱싱하면, 쿼리 시점에 전체 코퍼스를 탐색하지 않고도 글로벌 이해가 가능하다. |
| **Limitation** | (1) 인덱싱 비용이 높음: LLM으로 엔티티 추출·커뮤니티 요약 생성 시 대규모 LLM 호출 필요 (Podcast 1M 토큰 기준 281분 소요). (2) 로컬 질문(특정 엔티티에 대한 구체적 질문)에서는 벡터 RAG가 더 효율적이며 Directness 기준에서는 벡터 RAG가 우위. (3) 커뮤니티 탐지 알고리즘(Leiden)의 파라미터에 따라 요약 품질이 달라질 수 있음. (4) 증분 업데이트 메커니즘 미제공으로 코퍼스 변경 시 전체 재인덱싱 필요. |

---

## Method

1. **Source Documents → Text Chunks**
   - 코퍼스의 문서를 600-token 청크로 분할 (청크 간 100-token 오버랩)
   - 청크 크기는 핵심 설계 파라미터: 청크가 길수록 LLM 호출 횟수 감소(비용 절감)하지만, 청크 초반부 정보의 recall 저하 발생

2. **Text Chunks → Entities & Relationships**
   - LLM이 각 청크에서 엔티티(인물·장소·조직 등 named entity)와 관계를 추출하고 각각에 대한 짧은 설명 생성
   - 도메인 맞춤 few-shot 프롬프트(in-context learning)로 추출 품질 조정 가능
   - 클레임(claims)도 추가 추출: 엔티티에 대한 검증 가능한 사실 진술

3. **Entities & Relationships → Knowledge Graph**
   - 여러 청크에서 중복 추출된 동일 엔티티/관계를 집계하여 그래프의 노드·엣지로 통합
   - 동일 관계의 중복 횟수가 해당 엣지의 가중치(weight)로 사용됨

4. **Knowledge Graph → Graph Communities**
   - Leiden 커뮤니티 탐지 알고리즘을 계층적(hierarchical)으로 적용: 각 커뮤니티 내에서 재귀적으로 하위 커뮤니티 탐지
   - 각 계층은 그래프 노드를 mutually exclusive, collectively exhaustive 방식으로 분할
   - Podcast 데이터셋 기준: C0(34개) → C1(367개) → C2(969개) → C3(1,310개) 커뮤니티

5. **Graph Communities → Community Summaries**
   - **Leaf-level**: 커뮤니티 내 엣지를 source+target 노드 degree 합 기준으로 내림차순 정렬 후 LLM 컨텍스트 윈도우가 채워질 때까지 노드·엣지·클레임 설명을 추가하여 요약 생성
   - **Higher-level**: 하위 커뮤니티 요약을 재귀적으로 통합하여 상향식(bottom-up) 요약 구조 형성

6. **Community Summaries → Global Answer (Map-Reduce)**
   - **Prepare**: 커뮤니티 요약을 무작위로 셔플 후 사전 지정된 토큰 크기로 분할
   - **Map**: 각 청크에서 LLM이 독립·병렬적으로 부분 답변 생성 + 0~100 점수로 helpfulness 자기 평가; 점수 0인 답변은 필터링
   - **Reduce**: 부분 답변을 helpfulness 점수 내림차순으로 정렬하여 최종 글로벌 답변 생성

---

## Key Contribution

1. **글로벌 센스메이킹을 위한 그래프 기반 RAG**: 엔티티 KG + 계층적 Leiden 커뮤니티 탐지 + 재귀적 요약으로 전체 코퍼스의 주제와 패턴을 파악하는 최초의 체계적 접근
2. **커뮤니티 요약의 사전 생성**: 쿼리 시점에 전체 그래프를 탐색하지 않고, 사전 생성된 커뮤니티 요약을 map-reduce로 활용하여 확장성 확보. C0(root-level)는 TS 대비 97%+ 토큰 절감
3. **Claim-based 정량 검증**: LLM 평가를 클레임 추출·클러스터링으로 교차 검증하는 2단계 평가 설계. LLM 레이블과 클레임 기반 레이블의 일치율 78%(comprehensiveness)
4. **오픈소스 생태계 구축**: Microsoft GraphRAG + LangChain, LlamaIndex, Neo4J 등 주요 프레임워크에 통합

---

## Experiment & Results

- **데이터셋**: Podcast transcripts (~1M 토큰, 1,669개 청크), News articles (~1.7M 토큰, 3,197개 청크)
- **비교 조건**: GraphRAG 4개 계층(C0~C3), Text Summarization(TS), Vector RAG(SS)
- **평가**: LLM-as-a-judge (125개 질문 × 5회 반복) + Claimify 클레임 기반 정량 검증

**GraphRAG vs Vector RAG (Win Rate)**:
- Comprehensiveness: GraphRAG 전 조건이 SS 대비 72~83% win rate (Podcast, p<.001)
- Diversity: GraphRAG 전 조건이 SS 대비 75~82% win rate (Podcast, p<.001)
- Directness: Vector RAG(SS)가 모든 비교에서 가장 직접적인 답변 생성 — 예상된 tradeoff

**Claim-based 정량 검증**:
- 총 47,075개 unique claim 추출 (답변당 평균 31개)
- 평균 클레임 수: SS(25.23) vs C0(34.18) — GraphRAG가 약 36% 더 많은 클레임 포함 (p<.05)
- 다양성(클러스터 수): C0=23.16 vs SS=18.55 (유의미한 차이, p<.05)

**토큰 효율성**:
- C0(root-level): TS 대비 97%+ 적은 컨텍스트 토큰 (26,657 vs 1,014,611)
- C3(low-level): TS 대비 26~33% 토큰 절감하면서 유사한 성능 유지
