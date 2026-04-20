# Chain of Agents: Large Language Models Collaborating on Long-Context Tasks

> **논문 정보**: Yusen Zhang, Ruoxi Sun, Yanfei Chen, Tomas Pfister, Rui Zhang, Sercan Ö. Arik (Penn State University, Google Cloud AI Research)
> **arXiv**: 2406.02818 (2024.06) | **학회**: NeurIPS 2024 Preprint
> **코드**: 미공개

---

## Problem

LLM이 긴 컨텍스트를 처리해야 하는 태스크에서 두 가지 주류 전략이 모두 근본적 한계를 가진다.
Input Reduction 계열(Truncation, RAG)은 전체 입력을 모델 윈도우에 맞게 줄여 넣지만, 검색기의 낮은 정확도 때문에 정답 근거를 담은 청크를 놓치면 downstream LLM이 불완전한 문맥을 받게 된다.
Window Extension 계열(Position Interpolation, 200k Claude-3 등)은 컨텍스트 윈도우를 확장해 전체 입력을 소비하지만, 윈도우가 길어질수록 "lost-in-the-middle" 현상으로 모델이 필요한 정보에 집중하지 못한다.
실제로 Claude-3 Opus의 200k Vanilla 모델조차 NarrativeQA에서 F1 6.56, BookSum에서 ROUGE 14.00에 머무른다.
QA, 요약, 코드 완성 등 실제 long-context 응용은 책 한 권(108,478단어의 BookSum)이나 논문 전체(GovReport 9,239단어)를 다루어야 하므로 두 전략의 한계가 치명적이다.
수용 영역(Receptive Field)의 완전성과 정보 집중(Focus) 능력을 동시에 확보하는 새로운 패러다임이 필요하다.
또한 Full-Context는 입력 길이 n에 대해 O(n²)의 인코딩 시간 복잡도를 가져 비용 측면에서도 부담이 크다.
기존 멀티 에이전트 연구는 사회 시뮬레이션·디베이트·짧은 텍스트 추론에만 집중되어 long-context 문제 해결에는 거의 적용되지 않았다.

---

## Motivation

인간이 긴 문서를 읽을 때 구간별로 읽고 핵심을 축적하며 마지막에 종합하는 방식에서 영감을 받았다.
이 읽기 패턴을 LLM 멀티 에이전트 협업으로 구현하면, 각 에이전트는 짧은 컨텍스트만 보므로 집중 문제를 해결하면서도 전체 입력을 순차적으로 모두 커버할 수 있다.
RAG의 "read-then-process"와 달리, 에이전트가 청크를 읽으면서 동시에 처리하는 "interleaved read-process"는 제너릭 요약이나 passage counting처럼 쿼리 기반 검색이 어려운 태스크에도 적용 가능하다.
기존 멀티 에이전트 LLM 연구(Generative Agents, Social Simulacra, MedAgents, Debate 등)는 주로 사회 시뮬레이션과 짧은 텍스트 디베이트에 한정되어 있어 long-context 전용 프레임워크는 부재하다.
순차 체인 구조는 Worker → Worker 메시지 전달을 통해 multi-hop 추론을 가능하게 하며, 트리/병렬 구조에서 불가능한 크로스-청크 추론 체인을 생성할 수 있다.
훈련 불필요(training-free), 태스크 불변(task-agnostic), 길이 불변(length-agnostic)이면서 해석 가능한 프레임워크를 목표로 한다.
또한 인코딩 시간을 O(n²)에서 O(nk)로 줄여(k는 윈도우 크기, k≪n) Full-Context 대비 비용 효율성을 확보한다.
long-context LLM이라도 여전히 한계를 가지며, 입력이 그 한계를 넘어서는 경우가 항상 존재한다는 가정 위에서 설계되었다.

---

## Method

Chain-of-Agents(CoA)는 Stage 1(Worker Agents)과 Stage 2(Manager Agent)의 두 단계로 구성된 훈련 불필요 프레임워크이다.

1. **입력 분할**: 전체 소스 텍스트 x를 에이전트 윈도우 크기 k보다 짧은 l개의 청크 {c₁, c₂, ..., c_l}로 분할한다.

2. **Worker Agent 순차 처리 (Stage 1)**: l명의 Worker Wᵢ가 순차적으로 청크를 처리하며, 각 Worker는 태스크 지시문 I_W, 이전 Worker의 Communication Unit CU_{i-1}, 자신의 청크 cᵢ, 쿼리 q를 입력받아 새로운 CUᵢ를 출력한다.

3. **수식적 정의**: CUᵢ = LLM_Wᵢ(I_W, CU_{i-1}, cᵢ, q)의 재귀적 체인 형태로, CU₀는 빈 문자열로 초기화된다.

4. **Communication Unit의 태스크별 역할**: QA에서는 정답 근거 증거(evidence), 요약에서는 누적 요약(cumulative summary), 코드 완성에서는 함수/클래스 이름과 설명을 담아 태스크에 맞는 정보를 전달한다.

5. **Full Receptive Field 확보**: 마지막 Worker W_l의 CU에는 l개 청크 전체에 대한 통합 정보가 축적되므로 입력 길이에 무관하게 완전한 수용 영역을 달성한다.

6. **Multi-hop 협업 패턴**: Case study에서 W₁은 쿼리 답을 몰라도 관련 증거를 수집, W₂는 이전 CU와 자신의 청크를 결합해 추론 체인을 확장, W₃는 관련 정보가 없으면 CU를 그대로 전달하며 답을 첫 토큰에 배치한다.

7. **Manager Agent (Stage 2)**: Manager 지시문 I_M, 마지막 Worker의 CU_l, 쿼리 q를 입력받아 Response = LLM_M(I_M, CU_l, q)로 최종 답변을 생성한다.

8. **역할 분리 (Duty Decomposition)**: Worker는 long-context에서 관련 정보 추출, Manager는 최종 답변 종합으로 역할이 분리되며, 실험적으로 마지막 Worker가 직접 답을 내면 성능이 하락한다.

9. **시간 복잡도**: 인코딩은 Full-Context O(n²) 대비 CoA O(nk)로 감소(k≪n), 디코딩은 양쪽 모두 O(nr)로 동일하여 비용 측면에서 우위를 가진다.

10. **읽기 순서 설계**: 기본은 왼쪽→오른쪽(left-to-right) 자연 순서이며, 대안으로 Right-to-Left, Permutation 순서를 실험했다.

11. **Multi-path 확장**: 여러 읽기 경로를 생성 후 majority voting(w/ vote) 또는 LLM judge(w/ judge)로 최종 답을 선택, Bi-direction(2-way), Self-consistency(5-way), Permutation(5-way)의 세 가지 앙상블 전략을 제공한다.

12. **태스크 불변성**: QA/요약/코드 완성 모두에 동일한 CoA 구조를 적용하며 지시문 I_W, I_M만 태스크별로 교체한다.

13. **모델 유연성**: Worker와 Manager에 서로 다른 LLM 사용 가능하나 실험에서는 기본적으로 동일 모델로 통일했다.

---

## Key Contribution

1. **Long-context 전용 멀티 에이전트 협업 프레임워크 최초 제안**: training-free, task-agnostic, length-agnostic, highly-interpretable을 동시에 만족하는 첫 접근.
2. **8k 윈도우 CoA가 200k 윈도우 LLM을 능가**: Claude-3 Opus 기준 NarrativeQA에서 CoA(8k) 23.96 vs Vanilla(200k) 6.56으로 약 3.7배 성능.
3. **Full receptive field + short-context focus 동시 달성**: 입력 청크는 짧지만 Worker 체인을 통해 전체 입력을 커버하여 RAG의 수용 영역 문제와 Window Extension의 집중 문제를 동시에 해결.
4. **"Lost-in-the-middle" 문제 완화를 실험적으로 입증**: Vanilla 6.13(±2.17) vs CoA 4.89(±1.91)로 성능 편차 감소.
5. **순차 통신의 우월성 입증**: 8개 데이터셋 전부에서 Hierarchical/Merge(병렬) 기반 멀티 에이전트를 상회하여 sequential chain이 tree/parallel보다 long-context에 적합함을 보임.
6. **인코딩 시간 복잡도 O(n²) → O(nk) 감소**로 Full-Context 대비 비용 효율성 확보.
7. **9개 데이터셋 × 6개 LLM 대규모 실증**: PaLM 2 (text-bison, text-unicorn), Gemini Ultra, Claude-3 Haiku/Sonnet/Opus 전반에 걸쳐 모든 태스크 유형에서 일관된 개선.

---

## Experiment

**평가 설정**: 9개 데이터셋(QA 5: HotpotQA, MuSiQue, NarrativeQA, Qasper, QuALITY / 요약 3: QMSum, GovReport, BookSum / 코드 1: RepoBench-P), 6개 LLM.
평균 입력 길이는 Qasper 4,236단어부터 BookSum 108,478단어까지, 평균 Worker 수는 Qasper 1.12명부터 BookSum 18.63명까지 분포한다.

**QA 성능 (text-bison 8k 기준)**:
- HotpotQA: CoA 53.62 vs RAG 51.91 vs Vanilla 45.57 (F1, +8.05 over Vanilla).
- MuSiQue: CoA 37.09 vs RAG 33.83 vs Vanilla 26.87 (F1, +10.22 over Vanilla).
- NarrativeQA: CoA 25.26 vs RAG 14.20 vs Vanilla 11.96 (F1, +13.30 over Vanilla).
- Qasper: CoA 37.17 vs RAG 27.20 vs Vanilla 26.56 (F1, +10.61 over Vanilla).

**gemini-ultra**: QuALITY에서 CoA(8k) 80.60 vs Vanilla(32k) 58.60 vs RAG(8k) 62.40 — EM +22.00로 32k 윈도우를 가진 Gemini를 8k CoA가 크게 상회.

**Long Context LLM 비교 (Claude-3 Opus)**:
- NarrativeQA: CoA(8k) 23.96 vs Vanilla(200k) 6.56 — +17.40.
- BookSum: CoA(8k) 17.47 vs Vanilla(200k) 14.00 — +3.47.
- 개선 폭이 Haiku → Sonnet → Opus로 모델이 강해질수록 커짐(NarrativeQA: +11.63/+11.36/+17.40).

**멀티 에이전트 구조 비교 (text-bison 8k)**: CoA가 8개 데이터셋 전체에서 Hierarchical과 Merge를 상회.
MuSiQue에서 CoA 37.09 vs Hierarchical 29.40 vs Merge 26.66.
NarrativeQA에서 CoA 25.26 vs Hierarchical 17.04 vs Merge 11.27.

**Ablation (w/o Manager)**: MuSiQue 37.09 → 26.79로 -10.30, HotpotQA 53.62 → 48.58로 -5.04.

**Reading Order Ablation**: Left-to-right가 대부분 태스크에서 최고, Right-to-Left는 MuSiQue 29.77로 가장 저조, Permutation은 HotpotQA 56.05로 일부 태스크에서 L2R을 상회.

**Multi-path 결과**: Permutation 5-way + judge가 HotpotQA 59.17, MuSiQue 42.37로 단일 경로 대비 추가 향상.
Oracle 상한은 HotpotQA 75.73, MuSiQue 60.16, NarrativeQA 39.89로 현실 selector와의 gap이 커서 개선 여지가 크다.

**BookSum 길이별 성능**: Claude-3 Opus 기준 입력이 400k 토큰을 초과할 때 CoA의 Vanilla(200k) 대비 개선률이 약 100%에 도달, 긴 입력일수록 CoA 우위가 커진다.

**RAG 실패 분석**: NarrativeQA에서 gold answer 청크가 RAG 상위에 없을수록(index가 클수록) CoA의 개선폭이 커져 RAG 실패 영역에서 CoA가 특히 유효함을 입증.

---

## Limitation

현재 Worker 간 Communication Unit은 자연어 출력을 그대로 사용하므로, LLM 간 통신에 최적화된 표현이 아닐 수 있다.
저자들도 finetuning 또는 in-context learning으로 통신 효율을 높이는 방향을 향후 과제로 제시했다.
CoA는 순차 체인이라는 단일 통신 패턴만 탐구하였으며, 디베이트·토론·round-table 등 더 복잡한 에이전트 간 상호작용 형태는 미탐구 상태이다.
순차 처리 특성상 Worker 수에 비례해 레이턴시가 선형 증가하며, Worker 간 의존성으로 병렬화가 본질적으로 어렵다.
Multi-path 앙상블은 성능을 높이지만 비용이 5-way에서 5배로 증가하며, oracle 상한(HotpotQA 75.73)과 실제 vote/judge selector(59.17) 간 격차가 16점 이상 커 경로 선택 메커니즘이 최적이 아니다.
모델 라우팅(model routing) 등으로 일부 Worker를 경량 모델로 대체해 비용을 낮추는 방향이 제시되지만 구현되지 않았다.
실험 데이터셋이 영어 중심이며, 다국어 환경이나 멀티모달 긴 컨텍스트(이미지·비디오 포함)에 대한 검증이 부재하다.
Worker 간 오류 전파(error propagation) 문제에 대한 분석이 부족하여, 중간 Worker의 CU에 오류가 섞였을 때 이후 Worker가 이를 수정할 수 있는지에 대한 체계적 평가가 없다.
