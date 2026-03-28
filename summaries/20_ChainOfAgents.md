# Chain of Agents: Large Language Models Collaborating on Long-Context Tasks

> **논문 정보**: Yusen Zhang, Ruoxi Sun, Yanfei Chen, Tomas Pfister, Rui Zhang, Sercan Ö. Arik (Penn State University, Google Cloud AI Research)
> **arXiv**: 2406.02818 (2024.06) | **학회**: -
> **코드**: 미공개

---

## Problem

LLM이 긴 컨텍스트를 처리해야 하는 태스크(QA, 요약, 코드 완성 등)에서 두 가지 주류 전략이 존재하지만 각각 근본적 한계를 가진다. Input Reduction(RAG, Truncation) 방식은 입력을 줄여 LLM에 전달하지만, 검색 정확도가 낮으면 정답을 포함하는 청크를 놓칠 수 있어 수용 범위가 불완전하다. Window Extension 방식은 컨텍스트 윈도우를 확장하여 전체 입력을 소비하지만, 윈도우가 길어질수록 "lost-in-the-middle" 현상이 발생하여 필요한 정보에 집중하지 못한다. Claude-3의 200k 토큰 윈도우조차 NarrativeQA에서 F1 7.17, BookSum에서 ROUGE 14.00에 그쳐 긴 입력에서의 성능 저하가 뚜렷하다. 결국 긴 컨텍스트를 완전히 읽으면서도 각 부분에 집중할 수 있는 새로운 패러다임이 필요하다.

---

## Motivation

인간이 긴 문서를 처리할 때 전체를 한 번에 읽기보다 구간별로 읽고 핵심을 축적하며 최종 정리하는 방식에서 영감을 받았다. 이를 멀티 에이전트 협업으로 구현하면, 각 에이전트는 짧은 컨텍스트만 담당하므로 집중 문제를 해결하면서 전체 입력을 순차적으로 커버할 수 있다. 기존 멀티 에이전트 연구는 사회 시뮬레이션이나 짧은 텍스트 디베이트에 집중했으며, 긴 컨텍스트 태스크에 대한 멀티 에이전트 접근은 거의 탐구되지 않았다. 순차적 에이전트 체인을 통해 interleaved read-process 패턴을 구현하면, "read-then-process"인 RAG와 달리 정보를 점진적으로 축적·추론할 수 있다. 또한 인코딩 시간 복잡도가 Full-Context의 O(n²)에서 O(nk)로 감소하여 비용 효율성도 확보된다. 학습이 필요 없고, 태스크에 구애받지 않으며, 해석 가능성이 높은 프레임워크를 목표로 한다.

---

## Method

Chain-of-Agents(CoA)는 Stage 1: Worker Agents와 Stage 2: Manager Agent의 2단계로 구성된다.

1. **입력 분할**: 전체 소스 텍스트를 에이전트 윈도우 크기 k보다 짧은 l개의 청크로 분할한다.

2. **Worker Agent 순차 처리 (Stage 1)**: l명의 Worker Agent가 순차적으로 각 청크를 처리한다. 각 Worker는 태스크별 지시문, 이전 Worker가 전달한 Communication Unit(CU), 자신의 청크, 쿼리를 입력받아 새로운 CU를 출력한다.

3. **Communication Unit(CU)의 태스크별 역할**: QA에서는 정답 근거 증거, 요약에서는 누적 요약, 코드 완성에서는 함수/클래스 이름과 설명을 담는다.

4. **순차 체인의 핵심**: Worker 간 정보가 순차 전달되므로 마지막 Worker의 CU에는 전체 입력에 대한 정보가 축적된다. 이를 통해 입력 길이에 관계없이 full receptive field를 확보한다.

5. **멀티 홉 추론 지원**: W₁이 부분 증거를 생성 → W₂가 이전 증거와 새 청크를 결합하여 추론 체인 확장 → W₃가 관련 정보 없으면 이전 CU를 그대로 전달하는 식으로 협업.

6. **Manager Agent (Stage 2)**: 마지막 Worker의 CU와 쿼리, Manager 지시문을 받아 최종 응답을 생성한다. Worker와 Manager의 역할을 분리하여 각각 정보 추출과 종합 답변 생성에 집중.

7. **시간 복잡도**: 인코딩 시간 Full-Context O(n²) 대비 CoA O(nk)로 감소 (k ≪ n).

8. **Multi-path 확장**: 여러 읽기 경로(bi-direction, self-consistency, permutation)를 생성한 뒤 majority voting 또는 LLM judge로 최종 답을 선택하여 추가 향상 가능.

---

## Key Contribution

1. **멀티 에이전트 협업을 통한 긴 컨텍스트 처리의 새로운 패러다임**: training-free, task-agnostic, length-agnostic 프레임워크.
2. **8k 윈도우 CoA가 200k 윈도우 LLM을 능가**: Claude-3 Opus 기준 NarrativeQA에서 CoA(8k) 23.96 vs Vanilla(200k) 6.56으로 약 3.7배.
3. **"Lost-in-the-middle" 문제 완화**: 정보 위치에 따른 성능 편차가 Full-Context(6.13±2.17) 대비 CoA(4.89±1.91)로 감소.
4. **순차 통신의 우월성 입증**: 병렬 구조(Merge, Hierarchical) 대비 9개 데이터셋 전체에서 우수.
5. **인코딩 시간 복잡도 O(n²) → O(nk) 감소**로 비용 효율성 확보.

---

## Experiment & Results

9개 데이터셋(QA 5, 요약 3, 코드 1), 6개 LLM(PaLM 2, Gemini Ultra, Claude-3 Haiku/Sonnet/Opus).

**QA 성능 (text-bison 기준)**:
- HotpotQA: CoA 53.62 vs RAG 51.91 vs Vanilla 45.57 (F1)
- MuSiQue: CoA 37.09 vs RAG 33.83 vs Vanilla 26.87 (F1, +10.22)
- NarrativeQA: CoA 25.26 vs RAG 14.20 vs Vanilla 11.96 (F1, +13.30)
- QuALITY (gemini-ultra): CoA 80.60 vs Vanilla(32k) 58.60 vs RAG 62.40 (EM, +22.00)

**Long Context LLM 비교 (Claude-3 Opus)**:
- NarrativeQA: CoA(8k) **23.96** vs Vanilla(200k) 6.56 — **+17.40**
- BookSum: CoA(8k) **17.47** vs Vanilla(200k) 14.00 — **+3.47**

**멀티 에이전트 구조 비교**: CoA가 8개 데이터셋 전체에서 Hierarchical과 Merge를 상회. MuSiQue에서 CoA 37.09 vs Hierarchical 29.40 vs Merge 26.66.

**Ablation**: Manager 제거 시 MuSiQue에서 37.09 → 26.79로 10.30 하락.

**Multi-path**: Permutation 5-way + judge가 HotpotQA 59.17, MuSiQue 42.37로 단일 경로 대비 추가 향상. Oracle 상한은 HotpotQA 75.73.

---

## Limitation

현재 Worker 간 Communication Unit은 자연어 출력을 그대로 사용하므로, LLM 간 통신에 최적화된 표현이 아닐 수 있다. CoA는 순차 체인이라는 단일 통신 패턴만 탐구하였으며, 디베이트·토론 등 더 복잡한 에이전트 간 상호작용 형태는 미탐구 상태이다. 순차 처리 특성상 Worker 수에 비례하여 레이턴시가 선형 증가하며, 병렬화가 본질적으로 어렵다. Multi-path 앙상블은 성능을 높이지만 비용이 5배로 증가하며, oracle과 실제 선택 전략 간 격차가 커서 경로 선택 메커니즘의 추가 연구가 필요하다. 실험에서 사용한 데이터셋이 영어 중심이며, 다국어 환경이나 멀티모달 긴 컨텍스트에 대한 검증이 부재하다.
