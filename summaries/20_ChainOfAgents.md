# Chain of Agents: Large Language Models Collaborating on Long-Context Tasks

> **논문 정보**: Yusen Zhang, Ruoxi Sun, Yanfei Chen, Tomas Pfister, Rui Zhang, Sercan Ö. Arık (Penn State University, Google Cloud AI Research)
> **arXiv**: 2406.02818 (2024.06)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 긴 컨텍스트 처리의 두 주요 전략인 입력 축소(RAG)와 윈도우 확장 모두 한계가 있다. RAG는 필요한 정보가 검색되지 않을 수 있고, 윈도우 확장은 긴 컨텍스트에서 관련 정보에 집중하지 못하는 "lost-in-the-middle" 문제를 겪는다. |
| **Motivation** | 인간은 긴 문서를 한 번에 읽지 않고, 부분별로 읽으며 이전 부분의 정보를 다음 부분 처리에 활용한다. 이 인간적 접근을 다중 에이전트 협업으로 구현하면, 각 에이전트가 짧은 컨텍스트만 처리하면서도 전체 입력을 커버할 수 있다. 또한 시간 복잡도를 n²에서 nk로 줄일 수 있다(n: 입력 토큰, k: 윈도우 크기). |
| **Limitation** | (1) Worker 에이전트의 순차 처리로 인해 latency가 청크 수에 비례하여 증가. (2) 초기 worker의 오류가 후속 worker에 전파될 수 있는 error cascading 위험. (3) Communication Unit의 품질이 전체 성능을 좌우하나 이에 대한 명시적 품질 제어가 없다. (4) 학습 없는(training-free) 방식이지만 청크 크기·worker 수 등 하이퍼파라미터 튜닝 필요. |

---

## Method

CoA는 긴 입력을 청크로 분할한 뒤, **Worker 에이전트 체인**이 순차적으로 정보를 축적하고, **Manager 에이전트**가 최종 답변을 생성하는 2단계 프레임워크다.

1. **Stage 1: Worker Agent Chain (세그먼트 이해 + 체인 커뮤니케이션)**
   - 입력 x를 l개 청크 {c₁, c₂, ..., cₗ}로 분할 (각 청크 < 윈도우 크기 k)
   - Worker Wᵢ가 입력받는 것: 이전 worker의 Communication Unit CUᵢ₋₁ + 현재 청크 cᵢ + 쿼리 q + 태스크 지시 Iw
   - 출력: 다음 worker에 전달할 CUᵢ = LLM_Wᵢ(Iw, CUᵢ₋₁, cᵢ, q)
   - CU 내용은 태스크에 따라 다름: QA는 증거, 요약은 부분 요약, 코드 완성은 함수/클래스 설명

2. **Stage 2: Manager Agent (정보 통합 + 응답 생성)**
   - 마지막 worker의 CUₗ를 받아 최종 답변 생성
   - Response = LLM_M(IM, CUₗ, q)
   - Worker와 다른 LLM을 사용할 수 있어 유연성 확보

3. **핵심 특성**
   - **Training-free**: 추가 학습 없이 기존 LLM 활용
   - **Task-agnostic**: QA, 요약, 코드 완성 등 다양한 태스크에 적용
   - **전체 수용 영역**: 마지막 worker가 간접적으로 전체 입력 정보에 접근
   - **해석 가능성**: 각 worker의 CU를 통해 추론 과정 추적 가능
   - 입력 축소(수용 영역 손실)도 윈도우 확장(집중력 저하)도 아닌 제3의 접근

---

## Key Contribution

1. **읽기-처리 인터리빙**: 입력을 한 번에 처리하는 대신, 읽기와 처리를 교대하여 전체 수용 영역을 유지하면서 집중력 문제를 해결하는 새로운 패러다임.
2. **다중 에이전트 장문맥 프레임워크**: Training-free, task-agnostic하게 다양한 LLM에 적용 가능한 장문맥 처리 프레임워크.
3. **9개 데이터셋에서 일관된 개선**: QA, 요약, 코드 완성 3가지 태스크 유형에서 RAG, Full-Context, 다른 다중 에이전트 방식을 일관되게 초과.

---

## Experiment & Results

**데이터셋 9개**: QA 5개(HotpotQA, MuSiQue, NarrativeQA, Qasper, QuALITY), 요약 3개(QMSum, GovReport, BookSum), 코드 1개(RepoBench-P)

**LLM**: PaLM 2 (text-bison, text-unicorn), Gemini 1.0 Ultra, Claude 3 (Haiku, Sonnet, Opus)

**비교 대상**: Truncation, RAG, Full-Context(Vanilla), 계층 구조 다중 에이전트, 결과 병합 다중 에이전트

**주요 결과**: 9개 데이터셋 전체에서 CoA가 모든 베이스라인 대비 최대 **10%** 향상
- MuSiQue (멀티홉 QA): CoA가 RAG/Full-Context 대비 가장 큰 격차 — 순차 커뮤니케이션이 멀티홉 추론에 특히 효과적
- BookSum (108K 토큰 소설 요약): 가장 긴 입력에서도 CoA가 안정적 성능
- 계층 구조/결과 병합 다중 에이전트보다 CoA의 순차 체인이 일관되게 우수 — worker 간 정보 흐름의 중요성

**비용 효율**: Full-Context 대비 시간 복잡도 n² → nk로 개선
