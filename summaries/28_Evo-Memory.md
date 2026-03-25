# Evo-Memory: Benchmarking LLM Agent Test-time Learning with Self-Evolving Memory

> **논문 정보**: Tianxin Wei, Noveen Sachdeva, Benjamin Coleman, Zhankui He 외 (UIUC, Google DeepMind)
> **arXiv**: 2511.20857 (2025.11)
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 LLM 메모리 평가는 정적 대화 회상(conversational recall)에 국한되어, 에이전트가 태스크 스트림에서 경험을 축적·재활용하며 전략을 진화시키는 능력(experience reuse)을 측정하지 못한다. 에이전트는 "무엇이 말해졌는지"는 기억하지만 "무엇을 배웠는지"는 기억하지 못한다. |
| **Motivation** | 실세계 에이전트(대화형 어시스턴트, 체화 에이전트)는 연속적인 태스크 스트림을 처리하며 과거 경험에서 학습해야 하지만, StreamBench는 사실 유지만, LifelongBench는 메모리 구조/업데이트를 다루지 않는 등 기존 벤치마크가 분절적이다. |
| **Limitation** | 저자 언급: MemOS, LangMem 등 일부 메모리는 체화 환경과 호환되지 않아 multi-turn 평가에서 제외. 독자 관점: 피드백 신호가 정답 여부(correctness)로 제한되어, 부분 정답이나 정성적 피드백 환경에서의 검증 부족. 태스크 유사도가 높을수록 효과적이라는 결과는 다양한 도메인이 혼재하는 실세계 적용성에 의문을 남김. |

---

## Method

1. **스트리밍 벤치마크 설계**
   - 기존 정적 데이터셋을 순차적 태스크 스트림 {(x₁,y₁), ..., (xₜ,yₜ)}으로 재구조화
   - 각 스텝에서 Search → Synthesis → Evolve의 3단계 루프 수행
   - 10개 데이터셋: MMLU-Pro, GPQA, AIME-24/25, ToolBench (single-turn) + AlfWorld, BabyAI, PDDL, ScienceWorld, Jericho (multi-turn)

2. **10+ 메모리 모듈 통합 평가 프레임워크**
   - 에이전트를 (F, U, R, C) 튜플로 형식화: 기반 LLM, 메모리 업데이트, 검색, 컨텍스트 구성
   - 4개 범주: 에이전트 파이프라인(ReAct, A-Mem), 적응형 메모리(SelfRAG, MemOS, Mem0, LangMem), 절차적 지식(Dynamic Cheatsheet, AWM), 진화형 메모리(ExpRAG, ReMem)

3. **ExpRAG (Experience RAG)** — 간단한 베이스라인
   - 각 태스크 완료 후 (입력, 출력, 피드백)을 구조화된 경험 텍스트로 저장
   - 다음 태스크에서 유사 경험 top-k 검색 후 in-context learning으로 활용
   - 메모리에 단순 append — 반복적 정제 없음

4. **ReMem (Think-Act-Refine)** — 제안 프레임워크
   - ReAct의 Think-Act 루프를 **Refine** 연산으로 확장한 3차원 의사결정
   - **Think**: 내부 추론 및 태스크 분해
   - **Act**: 환경 실행 또는 최종 응답 생성
   - **Refine**: 메모리에 대한 메타 추론 — 유용한 경험 활용, 노이즈 가지치기, 재조직
   - 각 스텝에서 Think/Refine을 여러 번 수행 가능, Act 선택 시 스텝 종료
   - MDP로 형식화: 상태 = (입력, 메모리, 추론 트레이스), 행동 공간 = {Think, Act, Refine}

---

## Key Contribution

1. **최초의 자기 진화 메모리 통합 벤치마크**: "대화 회상" vs "경험 재활용"을 구분하고, 10개 데이터셋에서 10+ 메모리 모듈을 동일 프로토콜로 비교 평가하는 표준화된 프레임워크 제공
2. **ReMem 프레임워크**: ReAct에 메모리 정제(Refine) 차원을 추가하여 추론·행동·메모리 진화를 단일 루프에 통합, 메모리를 수동적 저장소에서 능동적 적응 컴포넌트로 전환
3. **경험 재활용의 효과 실증**: 단순한 ExpRAG조차 복잡한 적응형 메모리 시스템을 능가하는 경우가 많으며, 태스크 유사도와 메모리 개선의 상관관계(Pearson r=0.717)를 정량화

---

## Experiment & Results

- **LLM 백본**: Gemini 2.5 Flash/Flash-Lite/Pro, Claude 3.5 Haiku/3.7 Sonnet
- **Baseline**: ReAct, A-Mem, SelfRAG, MemOS, Mem0, LangMem, Dynamic Cheatsheet, AWM

**Single-turn (Claude 3.7 Sonnet)**: ReMem 평균 0.58, ExpRAG 0.59, Baseline 0.54 — 개선폭 중간 수준

**Multi-turn (Claude 3.7 Sonnet)**: ReMem이 압도적
- 평균 Success Rate: 0.78 (Baseline 0.24 대비 +0.54)
- AlfWorld: 0.92 (Baseline 0.18), ScienceWorld: 0.62 (Baseline 0.10)
- BabyAI: 0.73/0.83 (S/P), PDDL: 0.83/0.95 (S/P)

**Step 효율성**: ReMem은 AlfWorld에서 평균 22.6 → 11.5 스텝으로 단축 (약 49% 감소)

**태스크 난이도 순서**: Hard→Easy가 Easy→Hard보다 약간 우수 (ReMem AlfWorld: 0.94 vs 0.91), 어려운 태스크에서 먼저 학습한 경험이 더 전이 가능

**메모리 개선 상관**: 데이터셋 내 태스크 유사도가 높을수록 ReMem 개선폭 증가 (Pearson r=0.717, Gemini 2.5 Flash)
