# A Survey of Test-Time Compute: From Intuitive Inference to Deliberate Reasoning

> **논문 정보**: Yixin Ji, Juntao Li, Yang Xiang, Hai Ye, Kaixin Wu, Kai Yao, Jia Xu, Linjian Mo, Min Zhang (Soochow University, National University of Singapore, Ant Group)
> **arXiv**: 2501.02497v3 (2025.06)
> **코드**: https://github.com/Dereck0602/Awesome_Test_Time_LLMs

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | o1 모델의 성공으로 test-time compute scaling이 주목받지만, 이를 포괄적으로 다루는 서베이가 부족하다. System-1(직관적) 모델에서 System-2(숙고적) 모델로의 전환에서 test-time compute의 역할을 체계적으로 이해해야 한다. |
| **Motivation** | 학습 단계의 스케일링(데이터·파라미터)이 한계에 도달하면서, 추론 단계에서의 계산 투자가 새로운 성능 향상 경로로 부상했다. System-1 모델의 robustness 문제(분포 변화 취약)와 System-2 모델의 추론 한계(오류 누적, 선형적 사고)를 test-time compute로 극복할 수 있다. |
| **Limitation** | (1) 분야가 빠르게 발전하여 최신 연구(2025년 후반)를 완전히 반영하지 못할 수 있음. (2) System-1과 System-2의 경계가 모호한 방법들에 대한 분류가 명확하지 않을 수 있음. (3) 비용 대비 효과 분석이 정성적 수준에 머물러, 정량적 cost-performance 프레임워크 부재. |

---

## Method

이 서베이는 test-time compute를 **System-1 → Weak System-2 → Strong System-2**의 진화 경로를 따라 분류한다.

1. **Test-Time Adaptation (System-1 모델)**
   - **Parameter Updating**: TTT, Tent 등 — 테스트 샘플로 모델 파라미터 미세 조정
   - **Input Modification**: 데모 선택(EPR, UDR), 데모 생성(Auto-CoT, Self-ICL) — ICL 최적화
   - **Representation Editing**: ITI, ActAdd, CAA — 중간 표현 조작으로 출력 제어
   - **Output Calibration**: kNN-MT, AdaNPC — 출력 분포 보정

2. **Test-Time Reasoning (System-2 모델)**
   - **Feedback Modeling (보상/검증 모델)**
     - Score-based: ORM, PRM — 결과/과정 보상 모델
     - Generative-based: LLM-as-a-Judge, GenRM — 생성형 평가
   - **Search Strategies**
     - **Repeated Sampling**: SC-CoT, Best-of-N — 다양한 답변 생성 후 선택
     - **Self-Correction**: Reflexion, Self-debug, MAD — 자기 성찰·수정·토론
     - **Tree Search**: ToT, RAP, rStar, MCTS 기반 — 탐색 공간의 체계적 탐색

3. **미래 방향**
   - Generalization: 범용 보상 모델, Deep Research
   - Multi-modal: 시각·언어 결합 추론
   - Efficient: 불필요한 계산 pruning
   - Scaling Law: test-time compute의 스케일링 법칙
   - Combination: System-1과 System-2의 결합

---

## Key Contribution

1. **System-1→System-2 통합 분류**: test-time compute를 System-1 적응(TTA)과 System-2 추론(TTR)으로 나누고, 이 전환 과정을 체계적으로 매핑한 최초의 포괄적 서베이.
2. **상세 분류 체계**: TTA의 4가지 전략(파라미터/입력/표현/출력)과 TTR의 2가지 축(피드백 모델링/탐색 전략)으로 세분화.
3. **Improvement Training 통합**: 각 탐색 전략에 대해 test-time 추론과 학습 시 개선(ReST, SCoRe, MCTS-DPO 등)을 함께 다루어 실용적 관점 제공.
4. **5대 미래 방향**: Generalization, Multi-modal, Efficient, Scaling Law, Combination을 구체적 연구와 함께 제시.

---

## Experiment & Results

서베이 논문으로서 문헌 분석 중심:
- **분류 대상**: 200편 이상의 test-time compute 관련 연구를 체계적으로 분류
- **핵심 관찰**: (1) Repeated sampling이 가장 단순하지만 효과적, SC-CoT이 대표적. (2) Self-correction은 외부 피드백 없이는 효과가 제한적이나, 환경/도구 피드백 결합 시 강력. (3) Tree search가 가장 높은 성능 상한이지만 계산 비용이 급격히 증가. (4) PRM(Process Reward Model)이 ORM보다 세밀한 가이드를 제공하나 학습 데이터 구축이 어려움.

---

## 선택 요소 (해당되는 것만)

| 항목 | 내용 |
|------|------|
| **Taxonomy/분류 체계** | **2대 축**: (1) Test-Time Adaptation — Parameter Updating/Input Modification/Representation Editing/Output Calibration. (2) Test-Time Reasoning — Feedback Modeling(Score-based/Generative) + Search Strategies(Repeated Sampling/Self-Correction/Tree Search). **진화 경로**: System-1 → Weak System-2(CoT) → Strong System-2(Search+RL). |
