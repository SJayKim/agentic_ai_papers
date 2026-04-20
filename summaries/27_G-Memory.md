# G-Memory: Tracing Hierarchical Memory for Multi-Agent Systems

> **논문 정보**: Guibin Zhang, Muxin Fu, Guancheng Wan, Miao Yu, Kun Wang, Shuicheng Yan (NUS, Tongji University, UCLA, A*STAR, NTU)
> **arXiv**: 2506.07398 (2025.06)
> **코드**: https://github.com/bingreeky/GMemory

---

## Problem

LLM 기반 다중 에이전트 시스템(MAS)은 단일 에이전트 대비 탁월한 인지·실행 능력을 보이지만, 자기진화(self-evolution) 능력은 저개발된 메모리 아키텍처로 인해 심각하게 제약된다.

기존 MAS 메모리 메커니즘은 에이전트 간 협업 궤적의 미묘한 상호작용을 완전히 무시한 채 지나치게 단순화되어 있다.

MetaGPT, ChatDev, MacNet 같은 대표적 프레임워크조차 최종 결과물(solution artifact)만을 cross-trial 메모리로 저장하여 에이전트 간 협업 경험에서 의미 있는 학습을 불가능하게 한다.

또한 cross-trial 메모리와 에이전트별 역할 맞춤화가 부재하여, 단일 에이전트용 메모리가 누리는 표현력(expressive memory)을 전혀 확보하지 못한다.

단일 에이전트용 RAG 기반 유사도 검색 메모리를 MAS에 직접 이식하면, MAS의 다중턴 오케스트레이션 특성상 단일 에이전트 대비 최대 10배 긴 토큰 궤적으로 인해 LLM 컨텍스트가 압도된다.

실제로 MemoryBank는 AutoGen+PDDL에서 −3.12%, ChatDev-M은 DyLAN+FEVER에서 −1.87%, MacNet-M은 AutoGen+ALFWorld에서 −1.06%처럼 오히려 성능을 저하시키는 현상이 광범위하게 관측된다.

결과적으로 MAS는 환경과의 상호작용을 통한 지속적 진화 능력(continual evolution)을 확보하지 못한 채 수동 SOP나 사전 정의된 통신 토폴로지에 의존하는 상태에 머물러 있다.

---

## Motivation

조직 기억 이론(Organizational Memory Theory, Walsh & Ungson 1991)에 따르면 효율적 지식 검색은 넓은 범위의 스키마에서 출발하여 점진적으로 세밀한 기억으로 접근하는 계층적 구조를 따른다.

이 통찰은 MAS 메모리가 단일 평면적 저장소가 아니라, 추상적 교훈과 구체적 협업 궤적을 모두 담는 다계층 구조로 설계되어야 함을 시사한다.

MAS의 자기진화를 활성화하려면, 단순히 과거 쿼리와 해답을 저장하는 것을 넘어 "왜 성공/실패했는가"에 대한 일반화 가능한 교훈(insight)과 "어떻게 협업했는가"에 대한 미세한 상호작용 궤적(utterance-level trajectory)을 동시에 보존해야 한다.

또한 MAS는 역할(Role)이 상이한 에이전트들의 집합이므로, 동일한 기억 덩어리를 모든 에이전트에 주입하면 역할과 무관한 정보가 오히려 방해 요인이 된다.

기존 GPTSwarm, ADAS, AFlow 같은 자동화 MAS는 토폴로지/프롬프트를 최적화하지만 일회성(one-shot) 진화에 그치며, 경험 축적을 통한 점진적 자기조정(agility to self-adjust) 능력이 결여되어 있다.

따라서 (i) 인사이트·쿼리·상호작용의 3계층 메모리, (ii) 추상↔구체를 잇는 양방향 탐색, (iii) 에이전트 역할별 메모리 필터링, (iv) 환경 피드백 기반 업데이트라는 네 가지 요건을 통합하는 플러그앤플레이 메모리가 MAS에 요구된다.

---

## Method

1. **3계층 그래프 메모리 아키텍처**: 조직 기억 이론의 계층성을 반영하여 Insight Graph(최상위, 일반화 교훈) / Query Graph(중간, 과거 쿼리 네트워크) / Interaction Graph(utterance 단위, 최하위 협업 궤적)의 3개 그래프로 MAS 기억을 구조화한다.

2. **Interaction Graph 정의**: 쿼리 Q의 협업 궤적 G_inter^(Q) = (U^(Q), E_u^(Q)) 에서 노드 u_i ≜ (A_i, m_i) 는 발화 에이전트 A_i 와 텍스트 m_i 로 구성되며, 엣지 (u_j, u_k) ∈ E_u^(Q) 는 u_j 가 u_k 에 전달·영감을 준 시간적·인과적 관계를 인코딩한다.

3. **Query Graph 정의**: G_query = (Q, E_q) 에서 노드 q_i = (Q_i, Ψ_i, G_inter^(Q_i)) 는 원본 쿼리·상태(Failed/Resolved)·연결된 Interaction Graph의 삼중 구조이며, 엣지 E_q ⊆ Q×Q 는 쿼리 간 의미 관계를 토폴로지로 인코딩하여 단순 임베딩 유사도 이상의 검색을 가능케 한다.

4. **Insight Graph 정의**: G_insight = (I, E_i) 의 노드 ι_k = ⟨κ_k, Ω_k⟩ 는 인사이트 내용 κ_k 와 이를 뒷받침하는 쿼리 집합 Ω_k ⊆ Q 로 구성되며, 하이퍼엣지 (ι_m, ι_n, q_j) 는 쿼리 q_j 맥락에서 인사이트 ι_m 이 ι_n 을 문맥화하는 관계를 표현한다.

5. **Coarse-grained 유사도 검색**: 새 쿼리 Q 도착 시 MiniLM(ALL-MINILM-L6-V2) 임베딩으로 cosine 유사도 top-k 쿼리 집합 Q_S 를 Query Graph에서 선정하며, k ∈ {1, 2} 가 실험적 최적치이다.

6. **1-hop 이웃 확장**: 초기 유사도가 피상적일 수 있으므로 Q_S 를 1-hop 이웃으로 확장한 증강 집합 Q̃_S = Q_S ∪ {Q_k | ∃Q_j ∈ Q_S, Q_k ∈ N+(Q_j) ∪ N−(Q_j)} 을 구성한다.

7. **Upward Traversal (Query → Insight)**: 쿼리-인사이트 프로젝터 Π_{Q→I}(Q̃_S) ≜ {ι_k ∈ I | Ω_k ∩ Q̃_S ≠ ∅} 로 지원 쿼리 집합이 Q̃_S 와 교집합을 갖는 인사이트 노드들을 I_S 로 수집하여 고수준 전략 가이던스를 추출한다.

8. **Downward Traversal (Query → Interaction)**: LLM 기반 관련도 평가자 R_LLM(Q, q_k) 로 Q̃_S 내 상위 M개 쿼리를 선정하고, LLM 그래프 스파시파이어 S_LLM(G_inter^(Q_j), Q) 로 각 Interaction Graph에서 핵심 대화 서브그래프만 추출한다.

9. **역할별 메모리 배정**: 연산자 Φ(I_S, {Ĝ_inter^(Q_i)}; Role_i, Q) 가 각 에이전트 C_i = (Base_i, Role_i, Mem_i, Plugin_i) 의 역할 Role_i 와 태스크 Q에 따라 인사이트·스파시파이된 상호작용의 유용성을 평가·필터링하여 개인화된 Mem_i 로 초기화한다.

10. **Interaction Level 업데이트**: 태스크 실행 완료 후 각 에이전트의 발화를 추적하여 새 Interaction Graph G_inter^(Q) 를 구성·저장한다.

11. **Query Level 업데이트**: 새 쿼리 노드 q_new = (Q, Ψ, G_inter^(Q)) 를 추가하고, 엣지 집합 N_conn = Q_R ∪ (∪_{ι_k ∈ I_S} Ω_k) 을 이용해 top-M 관련 쿼리 Q_R 및 이번 태스크에서 활용된 인사이트들의 지원 쿼리들과 연결한다.

12. **Insight Level 업데이트**: 요약 함수 J(G_inter^(Q), Ψ) 로 새 인사이트 ι_new 를 생성하고, 이번에 활용된 인사이트 I_S 와 하이퍼엣지 E_{i,new} = {(ι_k, ι_new, q_new) | ι_k ∈ I_S} 로 연결한다.

13. **지원 쿼리 집합 확장**: 기존 인사이트의 Ω_k 를 Ω_k ∪ {q_new} 로 확장하여 성공/실패 사례를 누적 반영함으로써 인사이트의 신뢰도가 경험과 함께 진화하도록 한다.

14. **환경 피드백 통합**: 실행 후 상태 Ψ ∈ {Failed, Resolved}, 토큰 사용량, 도구 호출 수 등을 함께 기록하여 실패 사례로부터도 교훈을 추출한다.

15. **플러그앤플레이 통합**: G-Memory는 원본 MAS 프레임워크(AutoGen, DyLAN, MacNet)에 아무런 수정 없이 삽입 가능하며, 기본적으로 쿼리 시작 시 1회 호출되지만 라운드별/에이전트별 세밀한 호출 전략으로 확장 가능하다.

---

## Key Contribution

1. **MAS 메모리 병목 식별**: 기존 다중 에이전트 시스템의 자기진화 부재가 지나치게 단순한 메모리 아키텍처에 기인함을 체계적 리뷰로 입증하고, 단일 에이전트 메모리의 직접 이식이 오히려 성능을 저하시킬 수 있음을 다수의 baseline에서 실증했다.

2. **조직 기억 이론 기반 3계층 그래프 설계**: Insight/Query/Interaction의 3-tier 그래프 구조를 MAS에 최초로 적용하여, 협업 궤적의 추상화·압축·검색을 동시에 해결하는 원리적(principled) 메모리 아키텍처를 제시했다.

3. **양방향 메모리 탐색 메커니즘**: Upward(구체→추상 insight)와 Downward(추상→구체 trajectory)를 동시에 수행하여 고수준 전략 가이던스와 세밀한 대화 맥락을 상보적으로 제공하는 새로운 검색 패러다임을 정립했다.

4. **역할 인식 메모리 배정**: 연산자 Φ를 통해 에이전트별 Role과 태스크 특성에 맞춘 개인화된 메모리를 생성함으로써, MAS 고유의 분업 구조에 최적화된 메모리 제공이 가능함을 보였다.

5. **플러그앤플레이 통합성**: AutoGen, DyLAN, MacNet 등 주류 MAS 프레임워크에 코드 수정 없이 삽입되어 평균 +7~10% 성능 향상을 달성, 배포 편의성과 범용성을 입증했다.

6. **광범위한 실험적 검증**: 5개 벤치마크(ALFWorld, SciWorld, PDDL, HotpotQA, FEVER) × 3개 MAS 프레임워크 × 3개 LLM 백본(GPT-4o-mini, Qwen-2.5-7b/14b)이라는 총 45개 설정에서 우수성을 확인했다.

7. **토큰 효율성 실증**: PDDL+AutoGen에서 MetaGPT-M이 2.2×10⁶ 토큰으로 +4.07%를 얻는 반면 G-Memory는 1.4×10⁶ 토큰으로 +10.32%를 달성, 성능-비용 파레토 최적점을 확보했다.

---

## Experiment

**벤치마크 구성**: 지식 추론 도메인 HotpotQA·FEVER, 체화된 행동(Embodied) 도메인 ALFWorld·SciWorld, 게임 도메인 PDDL의 총 5개 벤치마크로 다양한 태스크 유형을 포괄한다.

**MAS 프레임워크**: AutoGen(COLM 2024), DyLAN(COLM 2024), MacNet(ICLR 2025)의 3개 대표 프레임워크와 통합하여 범용성을 검증했다.

**LLM 백본**: 프로프라이어터리 GPT-4o-mini와 오픈소스 Qwen-2.5-7b, Qwen-2.5-14b의 3종으로 규모·폐쇄성 스펙트럼을 다뤘다.

**Baseline 비교**: 단일 에이전트 메모리(No-memory, Voyager, MemoryBank, Generative Agents)와 MAS 메모리(MetaGPT-M, ChatDev-M, MacNet-M) 총 7종과 비교했다.

**GPT-4o-mini 주요 결과 (Table 1)**:
- AutoGen+G-Memory 평균 57.18% (No-memory 48.27% 대비 +8.91%), 2위 Voyager(+5.25%)와 Generative(+4.71%)를 크게 상회.
- DyLAN+G-Memory 평균 50.88% (No-memory 43.12% 대비 +7.76%), Voyager 47.85%, Generative 47.51% 대비 우위.
- MacNet+G-Memory 평균 51.95% (No-memory 42.01% 대비 +9.94%), 모든 baseline을 능가.

**세부 수치**: ALFWorld+AutoGen 88.81% (+11.20%), SciWorld+AutoGen 67.40% (+12.91%), PDDL+MacNet 24.33% (+12.15%), FEVER+AutoGen 66.24% (+9.11%), HotpotQA+MacNet 35.69% (+7.12%).

**Qwen-2.5-14b 최대 향상**: MacNet+ALFWorld에서 58.21% → 79.10%로 20.89% 포인트 상승, 논문 전체 최대 개선폭.

**지식 QA 최대**: HotpotQA+AutoGen 기준 No-memory 28.57% 대비 10.12% 향상(체화된 행동 20.89%, 지식 QA 10.12%가 논문 초록 인용치).

**Baseline 실패 사례**: MemoryBank는 AutoGen+ALFWorld에서 −2.65%, AutoGen+PDDL에서 −3.12%, ChatDev-M은 DyLAN+ALFWorld에서 −10.45%, DyLAN+HotpotQA에서 −9.24% 등 광범위한 성능 저하를 보여 MAS 맞춤 메모리의 필요성을 역으로 입증했다.

**토큰 비용 분석 (Figure 3)**: PDDL+AutoGen에서 G-Memory는 +10.32% 향상에 추가 1.4×10⁶ 토큰만 소모, MetaGPT-M(+4.07%, +2.2×10⁶ 토큰) 대비 절반 비용으로 2.5배 향상.

**Hop 확장 민감도 (Figure 4a)**: 1-hop이 ALFWorld 85.82%, PDDL 55.24%(AutoGen 기준)로 최적이며, 2-hop은 PDDL에서 49.79%까지 하락, 3-hop은 추가 노이즈 유입으로 열화.

**k 민감도 (Figure 4b)**: k ∈ {1, 2} 최적, k=5 시 ALFWorld+AutoGen −7.71%, FEVER+DyLAN −2.5%의 성능 저하 발생으로 과다 검색의 해악 확인.

**Ablation (Figure 4c, Qwen-2.5-14b)**: Interaction만 사용 시 AutoGen 평균 −4.47%, DyLAN −3.82%; Insight만 사용 시 AutoGen −3.95%, DyLAN −3.39%. PDDL에서 Inter-only 54.46%, Insight-only 50.00%, Full 55.24%; FEVER에서 63.27/68.77/71.43%로 양쪽 모두 필수임을 증명.

**Case Study**: ALFWorld+AutoGen에서 "put a clean cloth in countertop" 쿼리에 대해 유사 과거 쿼리 "put a clean egg in microwave"를 검색하고, 청소 전에 배치하려다 ground agent가 개입한 궤적 스니펫과 함께 "Clean first!" 인사이트를 제공하여 성공을 유도한 사례를 제시.

---

## Limitation

저자 언급: 현재 G-Memory는 5개 벤치마크·3개 도메인에서 검증되었으나, 의료 QA 등 더 다양한 도메인으로의 확장 검증이 필요하며 이는 향후 과제로 남긴다.

저자 언급: 현 구현은 쿼리 시작 시점에서 1회만 호출되는 정적 전략이며, 라운드별·에이전트별 동적 호출 전략은 추후 설정 가능하다고만 언급되어 실효성 검증이 부재하다.

독자 관점: 초기 검색 단계가 MiniLM(ALL-MINILM-L6-V2) 임베딩의 표현력에 전적으로 의존하며, 도메인 특화 쿼리나 코드·수식 포함 태스크에서 임베딩 품질 저하 시 전체 파이프라인이 붕괴할 가능성이 있다.

독자 관점: Insight 생성과 그래프 스파시파이(S_LLM), 관련도 평가(R_LLM), 역할별 배정(Φ) 등 핵심 연산이 모두 LLM 호출에 의존하여, LLM의 환각이나 편향이 메모리에 점진적으로 축적·증폭될 위험(노이즈 누적)이 존재한다.

독자 관점: 에이전트 수가 커지거나 협업 그래프가 조밀해질 때 역할별 메모리 필터링(Φ)의 호출 수가 |V|에 비례하여 증가하며, 이로 인한 토큰·지연 오버헤드의 확장성 검증이 부재하다.

독자 관점: Query Graph·Insight Graph의 크기가 시간에 따라 선형 증가하며, 장기 운용 시 그래프 가지치기(pruning) 또는 망각(forgetting) 메커니즘이 없어 노이즈 쿼리·오래된 인사이트가 검색 품질을 점진적으로 떨어뜨릴 수 있다.

독자 관점: 모든 실험이 공개 벤치마크에서 수행되어 도메인 간 전이(transfer) 성능(예: ALFWorld에서 축적한 메모리가 SciWorld에 유익한지)이나 악의적 쿼리·적대적 인사이트 주입에 대한 강건성 평가가 결여되어 있다.

독자 관점: 3계층 그래프 저장소의 영속화 전략(파일/DB 형식, 동시성 제어)이나 멀티 유저 환경에서의 쿼리 격리 방식 등 엔지니어링 세부사항이 논문에 공개되지 않아 실무 배포 시 추가 설계 부담이 존재한다.
