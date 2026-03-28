# A Survey of Test-Time Compute: From Intuitive Inference to Deliberate Reasoning

> **논문 정보**: Yixin Ji, Juntao Li, Yang Xiang, Hai Ye, Kaixin Wu, Kai Yao, Jia Xu, Linjian Mo, Min Zhang (Soochow University, National University of Singapore, Ant Group)
> **arXiv**: 2501.02497v3 (2025.07) | **학회**: -
> **코드**: https://github.com/Dereck0602/Awesome_Test_Time_LLMs

---

## Problem

대규모 언어 모델(LLM)의 훈련 단계 스케일링은 데이터 부족과 계산 자원 한계로 인해 점차 어려워지고 있다. 기존 모델은 빠르고 직관적인 System-1 사고에 의존하여, 분포 변화(distribution shift)에 취약하고 복잡한 추론 과제에서 기대 이하의 성능을 보인다. Chain-of-Thought(CoT) 프롬프팅이 명시적 추론을 가능케 했으나, 오류 누적과 선형적 사고 패턴의 한계로 비선형적 인간 인지 과정(브레인스토밍, 반성, 백트래킹)을 충분히 모사하지 못한다. 한편, test-time compute 방법론이 다양하게 제안되었음에도, System-1부터 System-2까지 아우르는 체계적 서베이가 부재했다. OpenAI o1/o3, DeepSeek-R1, Gemini 2.5 등 대형 추론 모델의 등장으로 이 분야의 포괄적 정리가 시급해졌다.

---

## Motivation

OpenAI o1 모델이 복잡한 추론에서 보여준 탁월한 성능은, 추론 시간에 더 많은 연산을 투입할수록 모델 성능이 향상되는 test-time compute scaling 효과를 실증했다. 저자들은 이 개념이 LLM 이전 System-1 모델의 test-time adaptation(TTA)에서부터 시작되었음을 추적하고, System-1에서 약한 System-2, 강한 System-2로 진화하는 흐름을 하나의 통합 프레임워크로 정리하고자 한다. TTA는 파라미터 업데이트, 입력 수정, 표현 편집, 출력 보정을 통해 분포 변화에 대한 강건성을 높이지만, 명시적이고 논리적인 사고 과정을 보여주지 못하는 "암묵적 느린 사고"에 머문다. 반면 CoT 기반 System-2 모델은 명시적 추론이 가능하나, 반복 샘플링, 자기 교정, 트리 탐색 등의 전략을 결합해야 진정한 강한 System-2 사고에 도달한다.

---

## Method — 분류 체계 (Taxonomy)

### A. Test-time Adaptation (System-1 → 약한 System-2)

1. **파라미터 업데이트**: 테스트 샘플의 정보로 모델 파라미터를 미세 조정. TTT(보조 태스크 삽입), FTTA(비지도 신호 기반 적응). 정규화 레이어, soft prompt, LoRA 등 소수 파라미터만 업데이트, EMA로 치명적 망각 방지.

2. **입력 수정**: ICL 능력 활용, 테스트 샘플에 적합한 demonstration을 선택/생성. 정보 이론 기반 순서 최적화, RL 기반 선택, MCTS 기반 순회 순서 계획.

3. **표현 편집**: 중간 레이어에 steering vector를 더하여 출력 제어. 대조적 프롬프트 쌍의 표현 차이를 활용, 환각 완화, 독성 감소 등에 효과적.

4. **출력 보정**: 외부 정보(kNN 데이터스토어 등)로 모델 출력 분포를 보정. AdaNPC, kNN-MT 등.

### B. Test-time Reasoning (약한 System-2 → 강한 System-2)

5. **피드백 모델링**: 점수 기반(ORM 결과 검증, PRM 과정 검증)과 생성 기반(critic, LLM-as-a-Judge). MCTS로 과정 감독 데이터 자동 수집(OmegaPRM, Math-Shepherd).

6. **반복 샘플링**: Self-Consistency CoT(수학 추론에서 vanilla CoT 대비 18% 향상)와 Best-of-N 샘플링. ReST, vBoN은 BoN 분포를 학습하여 추론 비용 절감.

7. **자기 교정**: 외부 도구, 외부 모델 평가, 다중 에이전트 토론, 자기 비판(Self-Refine, Reflexion). SCoRe는 다중 턴 RL로 자기 교정 능력 향상, DeepSeek-R1은 규칙 기반 보상과 GRPO로 SFT 없이 강한 추론.

8. **트리 탐색**: BFS/DFS 기반 비정보 탐색(ToT)과 MCTS 기반 휴리스틱 탐색. 선택-확장-시뮬레이션-역전파 4단계로 최적 해에 접근. rStar는 다중 후보 경로 유지.

---

## Key Contribution

1. **최초의 통합 서베이**: System-1 TTA부터 System-2 test-time reasoning까지를 하나의 프레임워크로 체계화.
2. **진화 단계 분류**: System-1 → 약한 System-2(CoT) → 강한 System-2(반복 샘플링 + 자기 교정 + 트리 탐색).
3. **포괄적 분류 체계**: TTA 4가지와 test-time reasoning 3가지 + 피드백 모델링을 구조적으로 정리.
4. **개선 훈련(Improvement Training) 통합 논의**: 각 탐색 전략에 대응하는 학습 방법(ReST, SCoRe, MCTS-DPO 등).
5. **5가지 핵심 미래 방향**: 범용 System-2 모델, 멀티모달 test-time compute, 효율적 추론, test-time scaling law, 전략 조합.

---

## Experiment & Results — 커버리지 분석

서베이 논문으로 자체 실험 없이 인용된 주요 수치를 종합:
- **Self-Consistency CoT**: 수학 추론에서 vanilla CoT 대비 최대 **18% 정확도 향상**.
- **DeepSeek-R1**: SFT 없이 GRPO 기반 RL만으로 강한 추론, 규칙 기반 보상만으로 자기 교정 행동이 창발.
- **Best-of-N vs Majority Voting**: BoN은 어렵고 응답 분포 다양성이 중간 수준인 문제에 적합, 다수결은 쉬운 문제에 효과적.
- **반복 샘플링 스케일링**: 성능이 반복 횟수와 근사 log-linear 관계, 실패 확률은 power-law 스케일링.
- **MCTS 기반 탐색**: AlphaMath, TS-LLM이 수학/계획 과제에서 자동 단계별 평가 신호를 생성하며 탐색 깊이 확장.
- **다중 에이전트 토론**: 참여 LLM 수 증가에 따라 추론 성능 향상이나 비용 급증. GroupDebate는 그룹 내부 토론 + 그룹 간 합의로 비용 절감.
- **자기 교정의 한계**: 자동 검증 가능한 하위 과제로 분할 가능한 경우에만 실질적 이점 있다는 분석.
- **효율적 추론**: DEER은 confidence 기반 조기 종료, L1과 Elastic Reasoning은 토큰 예산 내 정밀한 응답 길이 제어.

---

## Limitation

- 자체 실험 부재로 방법론 간 정량적 우열 판단이 어렵다.
- test-time compute에 대한 통합 스케일링 법칙이 아직 미확립.
- 대부분의 연구가 수학과 코드 영역에 집중되어, 일반 과제·다국어·비기호적 추론으로의 일반화가 충분히 검증되지 않았다.
- 반복 샘플링, 트리 탐색, 다중 에이전트 토론 등의 높은 추론 비용에 대한 체계적 비용-성능 트레이드오프 분석이 부족하다.
- 자기 교정의 효과가 과대평가되었다는 반론이 존재하며, 올바른 답을 틀린 답으로 수정하는 위험이 미해결.
- 멀티모달 확장은 아직 초기 단계이며, 텍스트 기반 방법론의 단순 이식이 최적인지 미검증.
