# A Survey of Test-Time Compute: From Intuitive Inference to Deliberate Reasoning

> **논문 정보**: Yixin Ji, Juntao Li, Yang Xiang, Hai Ye, Kaixin Wu, Kai Yao, Jia Xu, Linjian Mo, Min Zhang (Soochow University, National University of Singapore, Ant Group)
> **arXiv**: 2501.02497v3 (2025.07, 36 pages) | **학회**: Manuscript submitted to ACM
> **코드**: https://github.com/Dereck0602/Awesome_Test_Time_LLMs

---

## Problem

대규모 언어 모델(LLM)의 훈련 시점 스케일링은 데이터 희소성과 계산 자원의 한계로 점차 한계에 부딪히고 있다.

기존 모델들은 ResNet, Transformer, BERT처럼 훈련 분포에 강하게 결합된 System-1 직관적 사고에 의존해, 분포 변화(distribution shift)와 복잡한 과제에서 취약성을 드러낸다.

Chain-of-Thought(CoT) 프롬프팅이 중간 추론 과정을 명시화해 System-2 사고를 가능케 했으나, 오류 누적과 선형적 사고 구조로 인해 사람의 비선형 인지 과정(브레인스토밍·반성·백트래킹)을 충실히 흉내 내기 어렵다.

RAG는 사실 오류를 어느 정도 완화하지만 추론 능력 향상 자체에는 기여가 제한적이라, CoT 기반 LLM은 여전히 "약한 System-2" 단계에 머문다.

OpenAI o1/o3, DeepSeek-R1, Gemini 2.5 같은 대형 추론 모델(LRM)의 등장으로 추론 연산량과 성능의 관계(test-time compute scaling)가 실증되었지만, System-1 시대의 TTA부터 System-2의 반복 샘플링·자기 교정·트리 탐색까지를 포괄하는 통합 서베이가 존재하지 않았다.

각 기법이 어떤 조건에서 서로 대체 가능한지, 어떻게 결합해야 하는지에 대한 체계적 지도(map)가 부재했다.

이 공백은 LRM 연구자가 실험 설계 시 선행 기법의 전수를 파악하기 어렵게 만든다.

본 논문은 System-1에서 강한 System-2로 이어지는 진화 경로를 하나의 프레임워크로 정리해 이 공백을 메우는 것을 목표로 한다.

---

## Motivation

저자들은 "test-time compute"라는 개념이 LLM 이전 System-1 모델의 test-time adaptation(TTA) 연구에서 시작되었음을 지적한다.

TTA는 파라미터 업데이트, 입력 수정, 표현 편집, 출력 보정의 네 갈래로 발전했으며, 모델의 robustness와 generalization을 개선했다.

하지만 TTA는 명시적 논리 흐름을 드러내지 않는 "암묵적 느린 사고"에 머물러, 복잡한 추론 과제에서 한계가 뚜렷하다.

CoT 이후 LLM은 명시적인 System-2 사고로 진입했지만, vanilla CoT는 여전히 단일 경로에 묶여 있어 반복 샘플링(다양성), 자기 교정(반성), 트리 탐색(백트래킹)을 결합해야 강한 System-2 사고에 근접할 수 있다.

또한 feedback modeling(ORM/PRM/critic)을 병용하지 않으면 탐색 공간에서 올바른 경로를 고르기 어렵다는 점이 최근 연구에서 반복적으로 드러났다.

저자들은 이 모든 흐름이 "추론 시 연산을 더 투입해 성능을 끌어올린다"는 공통 원리를 공유한다는 관점에서, System-1 → 약한 System-2 → 강한 System-2로 이어지는 단일 taxonomy를 제안한다.

이 프레임워크는 각 방법이 어디에 위치하는지, 어떤 개선 훈련(improvement training)으로 자기 증류되는지, 어떤 미래 방향(일반화·멀티모달·효율·스케일링 법칙·전략 결합)이 열려 있는지를 통합적으로 보여주는 것을 목표로 한다.

---

## Method

### A. Test-time Adaptation (System-1 → 약한 System-2)

1. **파라미터 업데이트 — TTT 계열**: 훈련 과정을 수정할 수 있다는 가정 아래 보조 태스크(회전 예측, masked autoencoding, contrastive learning)를 주입하고, 추론 시 해당 태스크 손실로 파라미터를 미세 조정한다.

2. **파라미터 업데이트 — FTTA 계열**: 훈련 과정을 건드리지 않고 불확실성(엔트로피)·KL divergence·moment matching 같은 규제를 통해 테스트 샘플로 모델을 갱신하며, RLCF는 CLIP score를, QA 도메인에서는 사용자 피드백을 학습 신호로 삼는다.

3. **효율 및 안정성 장치**: 정규화 레이어/soft prompt/LoRA/adapter/projection만 업데이트해 계산량을 절감하고, FOA는 역전파 없이 CMA-ES로 soft prompt를 적응시키며, episodic TTA와 EMA로 catastrophic forgetting을 방지한다.

4. **입력 수정 — demonstration selection**: ICL의 민감성을 보정하기 위해 EPR/UDR은 유사 예시를 검색하고, 정보 이론 기반 엔트로피·MDL 순서화, RL 기반 선택·정렬, Bayesian optimal classifier 관점의 demonstration 선정이 제안된다.

5. **입력 수정 — demonstration creation**: Self-ICL/SG-ICL/Auto-CoT는 LLM이 스스로 예시를 생성하고, DAIL은 지나간 테스트 예시를 메모리에 축적해 재사용하며, DAWN-ICL은 테스트 샘플 순회 순서를 MCTS 플래닝으로 최적화한다.

6. **표현 편집 — steering**: PPLM은 gradient 기반 편집으로 스타일을 제어하고, ActAdd는 대조적 프롬프트 쌍의 표현 차이를 residual stream에 더하며, CAA·ITI·SEA는 환각·독성·지시 준수·성격 제어 등 다양한 축에서 효과를 보인다.

7. **출력 보정 — 외부 정보 주입**: AdaNPC는 kNN 메모리 풀로 분포 이동을 점진적으로 추적하고, kNN-MT는 번역에서 datastore로부터 k-nearest 토큰 확률을 결합해 모델 분포를 재보정한다.

### B. Test-time Reasoning (약한 System-2 → 강한 System-2)

8. **피드백 모델링 — score-based verifier**: ORM은 최종 답의 정답 여부로, PRM(Lightman, Math-Shepherd, OmegaPRM, EpicPRM)은 각 단계의 정답 여부로 훈련되며, PAV는 단계의 "이득(advantage)"까지 평가해 탐색 신호를 정교화한다.

9. **피드백 모델링 — generative critic**: LLM-as-a-Judge, Auto-J, Prometheus, Shepherd, GenRM, R-PRM, Critic-RM, CLoud는 prompt 설계, SFT, DPO, Bradley-Terry 등을 조합해 자연어 비평 능력을 모델에 주입한다.

10. **반복 샘플링 — majority voting**: Self-Consistency CoT는 다수결로 수학에서 vanilla CoT 대비 최대 18% 정확도 향상, PROVE는 CoT를 프로그램으로 실행해 필터링, RPC는 저확률 샘플을 제거해 효율을 개선한다.

11. **반복 샘플링 — Best-of-N**: Cobbe et al., DiVeRSe(PRM 기반), Knockout(쌍별 비교)은 verifier로 최고 점수 응답을 고르며, 단계별 pruning이나 speculative decoding 아이디어로 BoN 비용을 줄인다.

12. **반복 샘플링 — improvement training**: ReST는 보상 임계치 이상 샘플을 자가 학습 데이터로 활용, vBoN·BoNBoN·BOND는 BoN 분포를 정책에 증류, Chow et al.은 BoN-aware 손실로 탐색성을 유지한다.

13. **자기 교정 — 피드백 소스**: 인간 평가(NL-EDIT, FBNET), 외부 도구(Self-debug의 컴파일러, CRITIC의 툴 API), 외부 모델(REFINER, Shepherd), 다중 에이전트 토론(MAD, Du et al., GroupDebate), 내재 피드백(Self-Refine, Reflexion, RCI, IoE, ProgCo, SETS, S1).

14. **자기 교정 — improvement training**: GLoRe는 전역·지역 리파이너, Xi et al.은 에이전트 합성 데이터, Self-correct는 온라인 모방 학습, SCoRe는 다중 턴 RL, T1은 RLOO + 엔트로피 보상, DeepSeek-R1은 규칙 기반 보상과 GRPO로 SFT 없이 자기 교정 능력을 창발시킨다.

15. **트리 탐색 — 알고리즘**: ToT는 BFS/DFS, Xie et al.은 beam search, RAP·MCTSr·SR-MCTS·ReST-MCTS*는 MCTS(선택-확장-시뮬레이션-역전파 4단계)를, A* 스타일 휴리스틱 탐색은 heuristic function 기반 최적 경로 보장을 노린다.

16. **트리 탐색 — 가치 함수**: AlphaMath/TS-LLM은 학습형 LLM value function, VerifierQ는 implicit/contrastive Q-learning으로 overestimation을 완화, rStar는 다중 경로 유지 후 두 LLM의 합의 경로 선택, SC-MCTS는 contrastive·likelihood·self-evaluation을 결합해 robust한 가치 추정을 수행한다.

17. **트리 탐색 — improvement training**: ReST-MCTS*, MCTS-DPO, AlphaLLM-CPL은 단계별 선호 데이터를 수집해 DPO·커리큘럼 학습으로 정책·보상 모델을 동시 강화, long CoT 데이터 구축에 트리 탐색이 필수적으로 채택된다.

---

## Key Contribution

1. **최초의 통합 서베이**: System-1 시대의 TTA부터 System-2 시대의 test-time reasoning까지를 하나의 taxonomy(Fig. 2)로 정리한 최초의 포괄적 리뷰다.

2. **진화 단계 프레이밍**: System-1 → 약한 System-2(vanilla CoT) → 강한 System-2(반복 샘플링 + 자기 교정 + 트리 탐색)의 3단계 축을 제시해, 각 기법의 위치와 역할을 명료화한다.

3. **Feedback–Search–Training 삼각 구조**: feedback modeling(score/generative), search strategies(repeated sampling/self-correction/tree search), improvement training(SFT, DPO, RL)을 교차 정리해 강한 System-2 모델을 구성하는 공통 설계 패턴을 드러낸다.

4. **포괄적 분류 체계와 대표 연구 매핑**: TTA 4가지 하위 범주(업데이트·입력·표현·출력)와 test-time reasoning 3가지 전략 × 검증 방식을 Table 1·2에서 대표 논문 수십 편과 함께 조망한다.

5. **TTA ↔ Reasoning 연결고리 명시화**: DAIL·DAWN-ICL처럼 ICL 기반 입력 수정이 MCTS 기반 추론 탐색과 연결되고, TTT가 LRM의 cold-start로 재활용되는 등 두 영역이 단절되지 않음을 보인다.

6. **최신 LRM 흐름 편입**: DeepSeek-R1의 GRPO·규칙 보상, S1의 "wait", SelfBudgeter, DEER, L1, Elastic Reasoning 등 2025년 전후 LRM 최전선 기법을 통일된 관점에서 포섭했다.

7. **5가지 미래 방향 제시**: Generalizable System-2(일반 과제·weak-to-strong), Multimodal test-time compute, Efficient test-time compute, Test-time scaling law, 전략 조합(Marco-o1, HiAR-ICL)을 연구 어젠다로 명시한다.

---

## Experiment

서베이 논문이라 자체 실험은 없지만, 인용된 벤치마크 수치로 각 전략의 실효성을 정량화한다.

- **Self-Consistency CoT**: 수학 추론에서 vanilla CoT 대비 최대 **18% 정확도 향상**을 달성하며, 단순 다수결이 강력한 기준선임을 입증한다.

- **반복 샘플링 스케일링**: Brown et al.은 성능이 샘플링 횟수와 근사 log-linear 관계임을, Chen et al.은 knockout tournament 모델링으로 실패 확률이 **power-law 스케일**을 따름을 이론적으로 증명한다.

- **BoN vs Majority Voting**: Li et al.의 비교 연구에 따르면 BoN은 **어렵고 응답 다양성이 중간 수준**인 문제에 적합하고, 다수결은 쉬운 문제에 강하다.

- **Knockout BoN**: 쌍별 비교 verifier 기반 토너먼트는 단순 점수 최댓값보다 안정적이며, speculative decoding 아이디어로 중간 단계를 pruning하면 비용이 크게 감소한다.

- **MCTS 기반 PRM 수집**: Math-Shepherd, OmegaPRM, EpicPRM은 사람 주석 없이 MCTS 롤아웃으로 PRM 학습 데이터를 자동 수집하며, ASPRM은 **토큰 불확실성 기반 적응형 분할**로 PRM 성능을 추가로 끌어올린다.

- **DeepSeek-R1**: SFT cold-start 없이 **규칙 기반 보상 + GRPO**만으로 강한 추론과 자기 교정 행동이 창발함을 보여, RL의 단독 스케일링 가능성을 실증한다.

- **다중 에이전트 토론**: 참여 LLM 수 증가 시 성능이 향상되나 비용 폭증, GroupDebate는 그룹 내부 토론 + 그룹 간 합의로 비용을 절감하고, ring topology도 fully-connected와 유사한 성능을 낸다.

- **자기 교정의 효과**: Kamoi et al.은 자기 교정이 **오라클 답이나 약한 초기 답에 의존**해 과대평가되었다고 지적하며, 자동 검증 가능한 하위 과제로 분할 가능한 경우에만 실질 이점이 있음을 정리한다.

- **효율적 추론**: DEER은 confidence 기반 조기 종료로 추론 오버헤드 감축, L1·Elastic Reasoning·SelfBudgeter는 토큰 예산 내 **정밀한 응답 길이 제어**를 달성하며, Damani et al.은 난이도 예측 모듈로 샘플별 연산 자원을 적응적으로 할당한다.

- **멀티모달 test-time compute**: VisualPRM은 MC estimation으로 process annotation을 구축해 lightweight PRM을 학습하고, LMM-R1은 텍스트 전용 RL의 추론 능력이 **멀티모달 RL의 효과적 cold-start**임을 보인다.

- **생성 과제 확장**: 비디오 생성에서 Cong et al.과 Liu et al.은 프레임 단위 PRM·frame tree search로 고비용 repeated sampling을 대체, 자기회귀 생성에서는 PARM이 중간 이미지 품질을 평가해 자기 교정을 유도한다.

---

## Limitation

자체 실험이 없어 방법론 간 정량적 우열을 직접 비교하기 어렵고, 공통 벤치마크 프로토콜 부재 때문에 인용된 수치들도 엄밀한 비교 대상이 되지 못한다.

test-time compute의 **보편적 scaling law**가 아직 확립되지 않았다. Brown et al.·Chen et al.·Snell et al.의 부분적 법칙만 존재하며, self-correction·tree search를 아우르는 통합 법칙은 미정립이다.

대부분의 연구가 **수학·코드**라는 자동 검증 가능한 도메인에 집중되어, 일반 과제·다국어·비기호적 추론(CoT 효과가 미미한 영역)으로의 일반화가 충분히 검증되지 않았다.

반복 샘플링·트리 탐색·다중 에이전트 토론은 **추론 비용이 급증**하나 체계적 비용-성능 trade-off 분석이 부족하고, 실서비스 latency budget 내에서 어떤 전략을 택할지에 대한 지침이 미흡하다.

**자기 교정의 효과**는 여전히 논쟁 중이며, 올바른 답을 잘못 수정(over-criticism)하거나 오라클·약한 초기 답에 의존하는 평가 편향이 해결되지 않았다.

**verifier/critic의 일반화 한계**로 도메인 밖 추론에 대한 안정적 신호 제공이 어려우며, weak-to-strong 일반화는 아직 초기 단계다.

**멀티모달 확장**은 텍스트 기반 방법론의 단순 이식이 주류이나, 이것이 최적인지에 대한 체계적 검증이 부족하다.

over-thinking(단순 문제 과복잡화)과 under-thinking(어려운 문제에서 경로 잦은 전환) 현상으로 LRM이 간단한 문제에서 오히려 성능이 떨어질 수 있으며, 이를 해결할 범용 예산 배분 전략이 아직 없다.
