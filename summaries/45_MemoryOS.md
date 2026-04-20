# Memory OS of AI Agent

> **논문 정보**: Jiazheng Kang, Mingming Ji, Zhe Zhao, Ting Bai (BUPT, Tencent AI Lab)
> **arXiv**: 2506.06326 (2025.05)
> **코드**: https://github.com/BAI-LAB/MemoryOS

---

## Problem

LLM은 고정 길이 컨텍스트 윈도우에 의존하기 때문에 장기 대화에서 연속성을 유지하기가 구조적으로 어렵다.
시간적 간격이 큰 세션 간 상호작용에서 사실 불일치가 누적되며 개인화 품질이 급격히 저하된다.
다중 세션 지식 유지, 지속적 사용자 적응, 안정적 페르소나 표현이 필요한 시나리오에서 이 한계가 특히 심각하게 드러난다.
현재까지의 메모리 연구는 지식 조직(A-Mem, TiM), 검색 메커니즘(MemoryBank, EmotionalRAG), 아키텍처(MemGPT, SCM)의 세 방향으로 분화되어 있다.
각 접근은 저장 구조, 검색 로직, 업데이트 전략 가운데 단일 차원에만 집중한다.
저장·업데이트·검색·생성을 통합적으로 관리하는 "운영체제" 수준의 프레임워크는 존재하지 않는다.
플랫 FIFO 큐 기반 MemGPT는 대화가 길어질수록 주제 혼합(topic mixing) 문제가 발생한다.
A-Mem의 그래프 기반 조직은 의미 확장에는 강하지만 다단계 링크 생성의 레이턴시와 오류 누적이 커진다.

---

## Motivation

운영체제의 세그먼트-페이지 메모리 관리(Multics 등)는 논리적 구조와 물리적 효율을 균형 있게 결합한 전형적 사례이다.
저자들은 이 원칙을 AI 에이전트의 대화 메모리에 그대로 전이하여 "토픽=세그먼트, 대화=페이지" 구조를 구성한다.
힛-카운트(heat-based) 우선순위로 자주 참조된 토픽을 유지하고 덜 접근된 정보를 폐기·아카이브하는 OS식 eviction 정책을 적용한다.
심리학적 기억 회상(Yuan et al., 2024)에서 영감을 얻어, 대분류(세그먼트) → 세부 페이지라는 2단계 검색을 도입한다.
장기 대화의 일관성·개인화·페르소나 지속성이라는 세 요구는 단일 기법으로는 해결되지 않으며 계층적 분업이 필수적이다.
따라서 short/mid/long 3계층 저장과 저장/업데이트/검색/생성 4모듈을 단일 시스템으로 엮는 것이 핵심 동기이다.
특히 사용자 특성 90차원(기본 욕구·성격, AI 정렬, 콘텐츠 플랫폼 관심 태그)은 장기 누적을 통해서만 의미 있게 형성된다.
운영체제에서 메인 메모리-디스크 계층이 수행하는 역할을 STM-MTM-LPM 계층으로 재해석하는 것이 본 연구의 출발점이다.

---

## Method

1. **3계층 저장 아키텍처**: Short-Term Memory(STM), Mid-Term Memory(MTM), Long-term Personal Memory(LPM)의 3단계로 정보를 조직한다.
2. **STM – 대화 페이지 단위**: 각 페이지는 `page_i = {Q_i, R_i, T_i}`(질문·응답·타임스탬프) 구조이며, 최대 길이 7의 고정 큐로 유지된다.
3. **Dialogue Chain 메타정보**: LLM이 두 단계로 메타를 생성한다. (1) 신규 페이지의 이전 페이지 대비 문맥 연관성 평가 후 체인 연결 또는 리셋 결정, (2) 체인 전체 페이지를 요약하여 `meta_chain_i` 생성.
4. **MTM – 세그먼트-페이지 구조**: 동일 주제 대화 페이지를 세그먼트로 묶는다. 세그먼트 소속 판정은 `F_score = cos(e_s, e_p) + F_Jaccard(K_s, K_p)`로 하며(임계값 θ=0.6), 세그먼트 최대 길이는 200.
5. **LPM – User Persona**: Static Profile(성별·이름·출생 연도 등 고정 속성) + User KB(과거 상호작용에서 증분 추출한 사실 정보, FIFO 100 엔트리) + 90차원 User Traits(기본 욕구/성격, AI 정렬, 콘텐츠 플랫폼 관심 태그) 구성.
6. **LPM – Agent Persona**: Agent Profile(역할·성격 등 고정 설정) + Agent Traits(상호작용을 통해 동적으로 형성되는 추천 이력·신규 설정, FIFO 100 엔트리).
7. **STM→MTM 업데이트**: STM 큐가 최대 용량(7)에 도달하면 FIFO로 가장 오래된 페이지를 MTM에 이전한다. 이전된 페이지는 `F_score`로 기존 세그먼트와의 유사도를 측정하여 병합되거나 신규 세그먼트로 생성된다.
8. **Heat 점수**: `Heat = α·N_visit + β·L_interaction + γ·R_recency`이며, `R_recency = exp(-Δt/μ)`(μ=1e+7초), α=β=γ=1로 설정.
9. **MTM→LPM 승격**: Heat가 임계값 τ=5를 초과한 세그먼트를 LPM으로 전환한다. 세그먼트·페이지로부터 User Traits 90차원, User KB, Agent Traits를 LLM이 자율 갱신한다. 전환 후 `L_interaction`은 0으로 리셋되어 heat가 감쇠하고 지속적 페르소나 진화가 보장된다.
10. **세그먼트 삭제**: Heat 점수가 낮은 세그먼트는 eviction되어 MTM 용량을 확보한다.
11. **검색 – STM**: 모든 STM 페이지를 최근 문맥으로 반환한다.
12. **검색 – MTM 2단계**: (1) `F_score`로 top-m=5 세그먼트 선별, (2) 각 세그먼트 내 의미 유사도 기준 top-k 페이지 선별(GVD: k=5, LoCoMo: k=10). 검색 직후 `N_visit`와 `R_recency`가 갱신된다.
13. **검색 – LPM**: User KB와 Agent Traits 각각 쿼리 벡터와 의미 유사도 상위 10개 엔트리 반환. User/Agent Profile과 User Traits 전체는 항상 포함된다.
14. **응답 생성**: STM(최근 맥락) + MTM(주제별 페이지) + LPM(페르소나) 검색 결과를 통합하여 최종 프롬프트를 구성하고 LLM이 응답을 생성한다.

---

## Key Contribution

1. **최초의 체계적 메모리 OS**: 저장·업데이트·검색·생성 4개 핵심 모듈을 하나의 운영체제로 통합한 최초 프레임워크.
2. **3계층 계층적 저장 아키텍처**: STM(real-time)/MTM(recurring topic)/LPM(personal)의 명시적 분업으로 맥락 일관성과 페르소나 지속성을 동시에 달성.
3. **OS 영감 세그먼트-페이지 업데이트**: Dialogue-chain 기반 FIFO(STM→MTM)와 Heat 기반 eviction(MTM→LPM)을 결합한 하이브리드 동적 업데이트.
4. **90차원 User Traits 기반 페르소나 진화**: 기본 욕구/성격, AI 정렬, 콘텐츠 플랫폼 관심 태그의 3범주 90차원을 LLM이 자율적으로 갱신하는 개인화 메커니즘.
5. **심리학적 회상 모방 2단계 MTM 검색**: 세그먼트 선택 후 페이지 선택이라는 human-like coarse-to-fine 검색으로 의미 일관성과 효율성 동시 확보.
6. **압도적 효율-성능 Pareto**: LoCoMo에서 F1 평균 +49.11%, BLEU-1 평균 +46.18% 향상을 달성하면서도 A-Mem 대비 LLM 호출 62% 절감, MemGPT 대비 토큰 77% 절감.

---

## Experiment

**벤치마크**: GVD(15명 가상 사용자, 10일간 하루 최소 2개 토픽의 멀티턴 대화), LoCoMo(평균 300턴·약 9K 토큰, Single-hop/Multi-hop/Temporal/Open-domain 4유형).
**기반 모델**: GPT-4o-mini, Qwen2.5-7B, Qwen2.5-3B. 하드웨어는 8x H20 GPU.
**Baseline**: TiM, MemoryBank, MemGPT, A-Mem (A-Mem*는 동일 환경 재현값).
**하이퍼파라미터**: STM 큐 7, MTM 세그먼트 200, User KB/Agent Traits FIFO 100, τ=5, θ=0.6, μ=1e+7, α=β=γ=1, top-m=5, top-k=10(LoCoMo)/5(GVD).

**GVD (GPT-4o-mini)**: Accuracy MemoryOS 93.3% vs A-Mem 90.4% (+3.2%), Correctness 91.2% vs 86.5% (+5.4%), Coherence 92.3% vs 91.4% (+1.0%).
**GVD (Qwen2.5-7B)**: Accuracy 91.8% vs A-Mem 87.2% (+5.3%), Correctness 82.3% vs 79.5% (+3.5%), Coherence 90.5% vs 87.8% (+3.1%).

**LoCoMo (GPT-4o-mini)**: Single-hop F1 35.27 (vs A-Mem* 22.61, +32.35%), Multi-hop F1 41.15 (+23.83%), Temporal F1 20.02 (vs A-Mem* 8.04, +118.80%), Open-domain F1 48.62 (+18.47%). 평균 F1 Rank 1.0 / BLEU-1 Rank 1.0.
**LoCoMo (Qwen2.5-3B)**: Single-hop F1 +125.61%, Multi-hop +31.45%, Temporal +46.69%, Open-domain +112.56% 대비 A-Mem*.
**BLEU-1**: Single-hop +42.33%, Temporal +111.52%, Open-domain +25.19% (GPT-4o-mini).

**효율성 (LoCoMo)**: MemoryOS 토큰 3,874 / 평균 LLM 호출 4.9회 / F1 36.23. A-Mem* 2,712 / 13.0 / 26.55 → 호출 62% 절감, F1 36% 향상. MemGPT 16,977 / 4.3 / 29.13 → 토큰 77% 절감, F1 24% 향상. MemoryBank 432 / 3.0 / 6.84, TiM 1,274 / 2.6 / 18.01.

**Ablation (GPT-4o-mini)**: MTM 제거 시 성능 저하가 가장 크고, LPM 제거가 두 번째, Dialogue Chain 제거 영향이 가장 작다. 전체 MemoryOS 제거 시 성능이 급락하여 유기적 통합이 핵심임을 확인.
**Hyperparameter k 분석**: k={5,10,20,30,40}에서 k 증가로 성능 개선되지만 일정 임계 초과 후 노이즈로 성능 저하. k=10이 성능-연산 비용의 최적 균형.
**Case Study**: "몇 주 전 습지공원 방문·달리기·다람쥐 목격" 디테일을 MTM의 세그먼트-페이지 + dialogue chain 상호작용으로 정확히 회상. "살 빼고 싶다"는 사용자 목표를 LPM이 기억해 버거 추천 시 "다이어트 중임을 잊지 말라"며 능동적 리마인드 제공.

---

## Limitation

저자 언급: 평가가 LoCoMo와 GVD 두 벤치마크에 한정되어 있어 도메인 커버리지가 좁다.
GVD는 10일·2토픽/일 구조, LoCoMo는 평균 300턴 수준이므로 수개월~수년 단위 초장기 상호작용에 대한 검증은 여전히 공백으로 남는다.
독자 관점 한계 1: STM 큐 길이=7, τ=5, MTM 세그먼트 최대=200, KB/Traits=100, μ=1e+7 등 핵심 하이퍼파라미터가 휴리스틱하게 결정되어 도메인 이전성(transferability)이 보장되지 않는다.
독자 관점 한계 2: 모든 업데이트(dialogue chain 생성, 세그먼트 요약, User Traits 90차원 자율 갱신)가 LLM 호출에 의존하므로 LLM 품질 저하 시 메모리 전체가 오염될 위험이 있다.
독자 관점 한계 3: α=β=γ=1로 균등 설정된 Heat 가중치는 태스크 특성(예: recency-critical vs frequency-critical)에 적응적이지 않다.
독자 관점 한계 4: 계층 간 전환(STM→MTM→LPM)의 누적 레이턴시가 실시간 대화 시나리오에 미치는 영향이 정량 보고되지 않았다.
독자 관점 한계 5: Agent Traits의 FIFO eviction이 장기적으로 중요한 특성을 잃을 수 있으며, 중요도 기반 폐기 정책이 부재하다.
독자 관점 한계 6: 대규모 멀티유저 실서비스 적용 결과와 저장 공간 확장 시나리오(수천 세그먼트 누적 상황)에서의 검색 효율은 검증되지 않았다.
