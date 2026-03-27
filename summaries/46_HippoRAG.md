# HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models

> **논문 정보**: Bernal Jiménez Gutiérrez, Yiheng Shu, Yu Gu, Michihiro Yasunaga, Yu Su (Ohio State University, Stanford University)
> **arXiv**: 2405.14831 (2024.05, NeurIPS 2024)
> **코드**: https://github.com/OSU-NLP-Group/HippoRAG

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 현재 RAG 시스템은 각 패시지를 독립적으로 인코딩하여, 패시지 경계를 넘어 지식을 통합(knowledge integration)해야 하는 태스크에서 실패한다. 멀티홉 QA에서 서로 다른 패시지의 정보를 연결하려면 비용이 높은 반복적 검색(IRCoT 등)이 필요하며, 반복 검색으로도 해결 불가능한 "path-finding" 유형의 질문이 존재한다. |
| **Motivation** | 포유류 뇌의 해마 기억 인덱싱 이론(hippocampal indexing theory)에 따르면, 신피질이 실제 기억을 저장하고 해마가 기억 간 연관 인덱스를 유지하여 빠른 연상 검색을 가능하게 한다. 이 메커니즘을 LLM의 장기 기억으로 모방하면 단일 검색 단계에서 멀티홉 추론이 가능하다. |
| **Limitation** | 저자 언급: KG 추출이 LLM에 의존하므로 REBEL 등 전용 OpenIE 모델 대비 비용 높음. 엔티티 매칭 정확도가 동의어 처리에 민감. 독자 관점: PPR 탐색 성능이 KG의 밀도·연결성에 민감하여 희소한 코퍼스에서 성능 저하 우려. 대규모 코퍼스(수백만 패시지)에서의 KG 구축 시간·비용이 미분석. 동적 업데이트 시나리오의 일관성 유지 방법이 미제시. |

---

## Method

1. **이론적 배경: 해마 기억 인덱싱 이론**
   - 인간 장기 기억은 **패턴 분리(pattern separation)**와 **패턴 완성(pattern completion)** 두 기능으로 설명
   - 신피질(neocortex): 고수준 표현으로 변환하고 실제 기억 저장
   - 방해마 영역(PHR): 신피질과 해마 사이 라우팅 담당
   - 해마(hippocampus): CA3의 조밀 연결 뉴런 네트워크로 기억 인덱스를 유지하며 연상 검색 수행
   - HippoRAG는 이 세 컴포넌트를 각각 LLM, 검색 인코더, KG+PPR로 대응

2. **오프라인 인덱싱 (메모리 인코딩)**
   - **OpenIE 트리플 추출**: GPT-3.5-turbo를 1-shot 프롬프팅으로 사용하여 각 패시지에서 명사구 노드 N과 관계 엣지 E를 추출, 스키마리스 KG 구축
   - 2단계 프롬프트: 먼저 named entity 추출 → 해당 엔티티를 포함하는 OpenIE 프롬프트로 최종 트리플 추출
   - **동의어 엣지 추가**: 검색 인코더 M(Contriever/ColBERTv2)으로 KG 내 명사구 간 코사인 유사도 계산, 임계값 τ=0.8 이상이면 동의어 엣지 E' 추가

3. **노드 특이성(Node Specificity)**
   - 노드 i의 특이성: sᵢ = |Pᵢ|⁻¹ (노드가 추출된 패시지 수의 역수)
   - 소수 패시지에만 등장하는 특정 노드일수록 가중치 높음 → PPR 전파 시 세밀한 관련성 조절

4. **온라인 검색 (메모리 인출)**
   - **쿼리 엔티티 추출**: LLM이 1-shot 프롬프트로 쿼리에서 named entity 집합 Cq 추출
   - **쿼리 노드 매핑**: 검색 인코더로 Cq를 인코딩, KG 내 모든 노드와 코사인 유사도 비교 → 가장 유사한 KG 노드 선택
   - **PPR 실행**: 쿼리 노드에 동등한 초기 확률 부여, KG 전체에서 Personalized PageRank 실행 (감쇠 계수 0.5)
   - PPR은 단일 단계에서 멀티홉 경로를 따라 확률 질량을 전파하여, 여러 쿼리 엔티티를 연결하는 중간 노드를 부상시킴
   - **패시지 스코어링**: PPR 확률 분포와 P 행렬을 곱하여 상위 패시지 반환

---

## Key Contribution

1. **해마 인덱싱 이론의 RAG 적용**: 신피질(LLM) + PHR(검색 인코더) + 해마(KG+PPR) 3-컴포넌트 구조로 인간 장기 기억을 모방. 단일 검색 단계에서 멀티홉 추론 실현
2. **비용·속도 우위**: IRCoT 대비 10~30배 저렴하고 6~13배 빠르면서 동등 이상의 성능
3. **Path-Finding 멀티홉 QA**: ColBERTv2, IRCoT가 모두 실패하는 path-finding 유형에서 HippoRAG만 정답 패시지 검색 성공
4. **지속적 지식 통합 용이성**: 새 지식 추가 시 KG에 엣지만 삽입, RAPTOR·GraphRAG처럼 전체 요약 재수행 불필요

---

## Experiment & Results

- **벤치마크**: MuSiQue (1,000 dev), 2WikiMultiHopQA (1,000 dev), HotpotQA (1,000 dev)
- **코퍼스 규모**: MuSiQue 11,656 패시지, KG 고유 노드 91,729개, 트리플 107,448개
- **Baseline**: BM25, Contriever, GTR, ColBERTv2, Propositionizer, RAPTOR, IRCoT

**단일 검색 (R@2 / R@5)**:
- MuSiQue: HippoRAG(ColBERTv2) 40.9/51.9 vs ColBERTv2 37.9/49.2
- 2WikiMultiHopQA: HippoRAG 70.7/89.1 vs ColBERTv2 59.2/68.2 (+11%/+20%)
- HotpotQA: HippoRAG 60.5/77.7 vs ColBERTv2 64.7/79.3 (경쟁적)

**멀티홉 All-Recall (AR@5)**:
- MuSiQue: HippoRAG 22.4% vs ColBERTv2 16.1% (+6%p)
- 2WikiMultiHopQA: HippoRAG 75.7% vs ColBERTv2 37.1% (+38%p)

**IRCoT 결합 (R@5)**:
- MuSiQue: IRCoT+HippoRAG 57.6% vs IRCoT+ColBERTv2 53.7%
- 2WikiMultiHopQA: IRCoT+HippoRAG 93.9% vs IRCoT+ColBERTv2 74.4% (+18%p)

**QA 성능 (EM/F1)**:
- 2WikiMultiHopQA: HippoRAG 46.6/59.5 vs ColBERTv2 33.4/43.3 (+17% F1)
- IRCoT+HippoRAG 전체 평균 EM 38.4 / F1 51.7

**어블레이션 (MuSiQue R@2)**:
- w/o Node Specificity: 37.6 (-3.3%p) / w/o Synonymy Edges: 40.2 (미미한 하락)
- PPR 대신 쿼리 노드만 사용: 37.1 (PPR의 핵심 기여 확인)
- REBEL로 OpenIE 교체: 31.7 (대폭 하락, LLM 기반 OpenIE의 중요성 입증)
