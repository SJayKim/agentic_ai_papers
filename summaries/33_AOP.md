# Agent-Oriented Planning in Multi-Agent Systems

> **논문 정보**: Ao Li, Yuexiang Xie, Songze Li, Fugee Tsung, Bolin Ding, Yaliang Li (HKUST, Alibaba Group, Southeast University)
> **arXiv**: 2410.02189v2 (2024.10, rev. 2025.03)
> **코드**: https://github.com/lalaliat/Agent-Oriented-Planning

---

## Problem

LLM 기반 멀티 에이전트 시스템에서 메타 에이전트(컨트롤러/플래너)는 사용자 쿼리를 서브태스크로 분해하고 각 서브태스크를 적합한 전문 에이전트에 할당해야 한다.

그러나 기존 연구는 단순 태스크 분해(HuggingGPT류)나 chain-of-thought 추론 확장에 초점을 맞추어, 에이전트의 실제 능력 경계와 서브태스크 특성을 정렬하는 데 실패한다.

메타 에이전트가 참조할 수 있는 정보는 각 에이전트의 짧은 description(d1, …, dn)뿐이어서, 간결하고 일반화된 설명만으로는 세밀한 능력 경계(예: 단일 엔티티만 처리 가능한지)를 표현하기 어렵다.

결과적으로 프롬프트 기반 분해는 (1) 단일 에이전트가 해결할 수 없는 복합 서브태스크 생성(solvability 위반), (2) 원본 쿼리의 핵심 정보 누락(completeness 위반), (3) 중복·불필요 서브태스크 생성(non-redundancy 위반)의 세 가지 문제를 빈번하게 일으킨다.

초기 실험에서 쿼리의 15% 이상이 분해 단계에서 completeness/non-redundancy 위반을 보였고, 단순 메타 에이전트 기반 할당은 GPT-4o 단독보다도 낮은 정확도(30.0% vs 33.3%)를 기록한다.

전체 에이전트를 순회하며 최적 응답을 고르는 Traversal 전략은 m×n번의 호출이 필요해 토큰·시간 비용이 폭발적으로 증가(23,175초, 프롬프트 3.07M tokens)하여 비실용적이다.

이러한 구조적 한계로 인해 멀티 에이전트 시스템의 이론적 잠재력이 실제 end-to-end 성능으로 이어지지 못한다.

---

## Motivation

대표 예시: "주석과 구리 100kg 혼합물의 녹는점을 800℃로 낮추려면 주석이 몇 kg 필요한가?"라는 쿼리를 "주석과 구리의 녹는점을 구하라" + "비율 계산"으로 분해하면, 첫 서브태스크가 search agent에 할당될 때 두 엔티티를 동시에 처리해 실패한다.

이는 "주석의 녹는점 결정" + "구리의 녹는점 결정"으로 더 세분화해야 함을 시사하며, 분해 granularity가 에이전트 능력에 맞춰 동적으로 조정되어야 함을 보여준다.

또 다른 예시로 "300인승 항공기로 뉴욕 인구 1%를 수송하려면 몇 대 필요?"에서 "뉴욕 인구 결정", "1% 계산", "항공기 대수 계산" 간 의존 관계와 숫자 정보(300, 1%)의 서브태스크별 보존이 중요하다.

사전 정의된 SOP(ChatDev, MetaGPT 등)는 소프트웨어 개발 등 특정 도메인에서는 효과적이지만, 다양한 실세계 쿼리를 다루는 범용 시스템에는 적용이 어렵다.

OpenAI o1 계열이 제시한 inference-time computing 패러다임에 착안하여, fast decomposition 결과를 최종 결과가 아닌 중간 산출물로 보고 추가 평가·수정을 거치는 접근이 필요하다.

모든 서브태스크에 대해 실제 에이전트 호출로 solvability를 검증하면 비용이 m×n배 증가하므로, 호출 없이 품질을 예측하는 learned reward model이 있으면 효율성과 효과성을 동시에 확보할 수 있다.

따라서 저자들은 solvability, completeness, non-redundancy라는 세 가지 설계 원칙을 명시적으로 정의하고, 이를 프레임워크 수준에서 강제하는 체계를 제안한다.

---

## Method

1. **3가지 설계 원칙 정의**: Solvability(각 서브태스크 qi는 할당된 단일 에이전트 A'i가 완전히 해결 가능), Completeness(서브태스크 집합 {q1..qm}이 원본 Q의 모든 핵심 정보를 포함), Non-Redundancy(중복·불필요 서브태스크 배제) — 프레임워크 전체가 이 3원칙 만족을 목표로 설계됨.

2. **Fast Decomposition & Allocation (4.1)**: 메타 에이전트 P에게 (i) 사용자 쿼리 Q와 전체 에이전트 설명 D 동시 제공, (ii) 할당 시 이유(reason) 작성 요구, (iii) 의존 관계(dep)를 명시한 JSON 구조 `[{task, id, name, reason, dep}]` 출력을 강제. 분해와 할당을 분리하지 않고 통합 수행해야 효과가 크다는 실험적 관찰 반영.

3. **Reward Model 학습 (4.2)**: 임베딩 레이어(all-MiniLM-L6-v2, 384차원) + 3-layer MLP(256/64/1) 구조. 서브태스크 임베딩과 에이전트 description 임베딩을 concat해 768차원 벡터로 MLP 입력. 손실 L(T,θ) = (1/K)·Σ(1/mk)·Σ(1/l)·Σ(s_{k,i,j} − M_θ(q_{k,i}, d_{k,i,j}))^2 로 MSE 최소화. 임베딩은 freeze, MLP만 fine-tune.

4. **Training Data 구성**: 각 쿼리 Q_k에 대해 메타 에이전트가 서브태스크별로 l개 에이전트(l = n/2) 후보 선택 → 실제 호출해 r_{i,j} 수집 → Scorer S가 correctness/relevance/completeness 3측면에서 점수 s_{i,j} 부여 → 삼중 T = {(q, d, s)} 생성. Scorer는 LLM 기반 또는 human annotator.

5. **Solvability 기반 분기 결정**: fast decomposition이 제안한 (qi, A'i)에 대해 Mθ(qi, d'i) 계산. (a) 점수가 threshold 이상 → 실행 승인, (b) threshold 미만 → 전체 에이전트 Aj에 대해 ŝi,j = Mθ(qi,dj) 계산 후 argmax 재할당, (c) max ŝi,j도 매우 낮으면 replan 트리거.

6. **Representative Works 메커니즘 (4.3)**: 각 에이전트 Aj는 자신이 과거에 완전히 해결한 서브태스크 집합 Qj를 유지. 신규 qi와의 유사도 sim(qi, Qj) = max{cos(E(qi), E(qt)) | qt∈Qj}로 계산.

7. **Re-describe vs Plan-in-detail 선택**: max_j sim_{i,j}가 임계값 이상이면 유사 과거 태스크 존재 → 표현 문제로 간주하고 re-describe (예시 문장 템플릿 기반 재작성), 임계값 미만이면 해당 서브태스크가 단일 에이전트로 풀 수 없을 만큼 복잡한 것으로 간주하고 plan-in-detail로 추가 분해. 두 경우 모두 중복 방지를 위해 기존 분해 전체를 프롬프트에 포함.

8. **Detector (4.4)**: 별도 role-play LLM 프롬프트. Completeness 검사로 원본 Q의 모든 key element·requirement 추출 후 서브태스크 집합과 매칭해 누락 탐지, 추가 의존성(unforeseen dep)까지 식별. Non-redundancy 검사로 중복 정보·동일 문제를 푸는 서브태스크쌍 또는 쿼리 해결에 기여하지 않는 서브태스크 탐지. 발견 시 메타 에이전트에 수정 제안 전달.

9. **Feedback Loop (4.5)**: 서브태스크 실행 후 결과를 다시 메타 에이전트에 피드백 → 후속 분해/할당 재조정. 쿼리 완전 해결 시, 기여한 서브태스크들을 대응 에이전트의 representative works Qj에 추가(유사도 threshold로 중복 방지) → 시간이 지남에 따라 에이전트 능력 표현이 점진적으로 풍부해짐.

10. **전체 파이프라인**: Query → Fast Decomposition → Detector(completeness/non-redundancy 수정) → Reward Model 평가 → {Accept | Replan | Plan-in-detail | Re-describe} 분기 → Refined Plan → Execution → Feedback → Representative Works 업데이트.

---

## Key Contribution

1. **3대 설계 원칙의 명시적 정의**: Solvability/Completeness/Non-Redundancy를 agent-oriented planning의 정규 요건으로 formalize하고, 각 원칙을 담당하는 메커니즘(Reward Model, Detector, Detector + sim threshold)을 1:1로 매핑한 최초의 체계.

2. **Reward Model 기반 pre-execution solvability 예측**: 실제 에이전트 호출 없이 (sub-task, agent description) 쌍의 점수를 예측하여 Traversal 방식의 m×n 호출 비용을 회피. MiniLM 임베딩 + 경량 MLP로 학습 비용이 매우 낮음(V100 1대, 50 epoch).

3. **Representative Works + Similarity 분기**: 과거 해결 사례와의 코사인 유사도로 "서브태스크 표현 문제(re-describe)"와 "내재적 복잡도 문제(plan-in-detail)"를 구분. 기존 프레임워크에는 없던 진단적 분기 메커니즘.

4. **Detector를 통한 completeness/non-redundancy 별도 처리**: 메타 에이전트 프롬프트만으로 15% 이상 실패하던 문제를 독립된 LLM 역할로 분리해 효과적으로 완화.

5. **Feedback-driven dynamic planning**: 정적 분해가 아닌, 중간 실행 결과 기반 재계획과 representative works의 온라인 업데이트로 시스템이 사용할수록 개선되는 self-improving 특성 확보.

6. **경량 경험적 증거**: 수치 추론 데이터셋(Husky-QA)에서 GPT-4o 대비 +10.4%, HUSKY 대비 +4.1% 정확도 향상(43.7%)을 유사 비용으로 달성, inference-time compute trade-off가 agent-planning 영역에서도 유효함을 실증.

---

## Experiment

**데이터셋**: Husky-QA (Kim et al., 2024) — 학습 1,440개, 테스트 292개의 수치 추론 쿼리. 보조 평가로 DROP, IIRC decontextualized subset 사용(Appendix D.1).

**에이전트 구성**: 4종 전문 에이전트 — Code Agent(Python 정밀 계산), Math Agent(단계적 수학 추론), Search Agent(Bing Search API), Commonsense Agent(상식 추론). 모두 GPT-4o 백본.

**Reward Model 세팅**: all-MiniLM-L6-v2(384차원) freeze + MLP(256→64→1), batch 32, lr 1e-3, 50 epoch, V100-SXM2-32GB 단일 GPU.

**평가 지표**: GPT-4o 기반 정답 일치 판정으로 Accuracy 계산, Prompt Tokens(M), Completion Tokens(M), 실행 시간(sec).

**Table 1 주요 결과**: AOP **43.7%** vs GPT-4o 33.3% (+10.4%p), CoT 35.6% (+8.1%p), Zero-Shot CoT 32.2% (+11.5%p), Meta-Agent 30.0% (+13.7%p), Meta-Agent Traversal 35.2% (+8.5%p), REACT 37.6% (+6.1%p), HUSKY 39.6% (+4.1%p).

**비용**: AOP는 프롬프트 1.12M / 완료 0.38M tokens, 11,869s로 멀티 에이전트 baseline과 유사 수준. Meta-Agent Traversal(3.07M/0.69M, 23,175s)보다 훨씬 효율적.

**Ablation (Table 2)**: w/o Plan Detector → 43.7% → 36.6% (−7.1%p, 가장 큰 영향), w/o Reward Model → 38.7% (−5.0%p), w/o Representative Works → 41.1% (−2.6%p). 세 구성 모두 필수.

**Scorer 영향 (Table 3)**: Manual Scoring으로 학습 시 46.9% (+3.2%p), Full Parameter Tuning(임베딩까지 학습)으로 47.9% (+4.2%p) 달성 — 고품질 데이터·완전 학습으로 추가 향상 여지 확인.

**일반화**: 한 데이터셋에서 학습한 reward model이 다른 데이터셋에서도 유효하게 동작(Appendix D.2).

**추가 분석**: 태스크별 LLM 특화 expert agent 도입, 유사 에이전트 공존 처리 전략을 Appendix E에서 논의.

---

## Limitation

저자 언급: Reward model 학습을 위해 K개 쿼리 × m개 서브태스크 × l개 에이전트 조합에 대한 실제 에이전트 호출과 scorer 평가가 필요하여 초기 데이터 구축 비용이 상당함. Manual scoring으로 성능은 오르지만 확장성이 떨어짐.

저자 언급: AOP의 inference 비용이 단일 에이전트(GPT-4o 0.02M/0.09M) 대비 크게 증가(1.12M/0.38M)하며, 이는 정확도 향상으로 정당화되지만 간단한 쿼리에는 과잉이 될 수 있음.

독자 관점: Reward model이 특정 에이전트 구성(code/math/search/commonsense 4종)에 과적합될 가능성이 크고, 새 에이전트 추가 또는 description 변경 시 재학습이 필요한지에 대한 구체적 논의가 부재.

독자 관점: 평가가 주로 수치 추론 QA(Husky-QA, DROP, IIRC)에 국한되어 있어 멀티모달, 장기 대화, 코드 개발 같은 질적으로 다른 도메인에서의 일반화는 검증되지 않음.

독자 관점: Representative works의 무한 증가 관리, stale한 과거 사례의 pruning 정책, sim threshold 민감도 분석이 제시되지 않아 운영 장기 안정성이 불명확.

독자 관점: Detector, Reward Model, Representative Works, Feedback Loop 각 모듈이 직렬적으로 호출되어 실행 경로가 길어지면 latency가 선형 누적되며, 실시간 인터랙션 요구 환경에서는 병목이 될 수 있음.

독자 관점: Scorer 자체가 LLM 기반일 때 scorer의 편향이 reward model로 전이되는 2차적 bias 문제에 대한 완화책이 다뤄지지 않음.

독자 관점: Replan 실패 시의 fallback 정책(무한 루프 방지, 최대 재시도 횟수 등)이 본문에서 명확히 기술되지 않아 실제 배포 시 신뢰성 보장이 제한적.
