# OWL: Optimized Workforce Learning for General Multi-Agent Assistance in Real-World Task Automation

> **논문 정보**: Mengkang Hu, Yuhang Zhou, Wendong Fan, Yuzhou Nie 외 (HKU, CAMEL-AI.org, Eigent.AI, UCSB, KAUST)
> **arXiv**: 2505.23885 (2025.05)
> **코드**: https://github.com/camel-ai/owl

---

## Problem

LLM 기반 다중 에이전트 시스템(MAS)은 실세계 태스크 자동화에 유망하지만, 본질적으로 도메인 특화 설계로 인해 교차 도메인 전이성이 극도로 제한된다.
이 한계는 두 가지 측면에서 드러난다.
첫째, 추론 측면에서 새 도메인에 배치하려면 전체 아키텍처를 재설계해야 한다. 예를 들어 MetaGPT는 소프트웨어 공학에 맞춰진 Standard Operating Procedures(SOP)에 의존하기 때문에 다른 분야로의 확장이 어렵다.
둘째, 학습 측면에서 MALT와 같은 기존 작업은 Generator-Verifier-Refiner 같은 고정 파이프라인의 모든 구성 요소를 개별적으로 재학습해야 한다.
따라서 새 도메인으로 시스템을 이전하려면 에이전트 앙상블 전체를 다시 훈련해야 하며, 이는 유연성을 급격히 떨어뜨린다.
또한 기존 오픈소스 프레임워크(HuggingFace Open Deep Research 등)는 상용 시스템(OpenAI Deep Research)에 비해 GAIA 벤치마크에서 상당한 성능 격차를 보인다.
이러한 단점들은 최소한의 재학습과 재설계만으로 다양한 도메인에 빠르게 적응 가능한 일반화·모듈화된 다중 에이전트 아키텍처의 필요성을 강조한다.

---

## Motivation

기존 MAS가 보이는 도메인 특화 경직성은 "전략적 계획"과 "도메인 특화 실행"이 하나의 시스템에 밀결합되어 있기 때문이라는 저자들의 관찰에서 출발한다.
두 역할을 분리하면 계획 모듈은 도메인 간 공통된 일반적 분해 능력을 학습하고, 실행 모듈은 도메인별 도구 호출로 국한된 책임만 갖게 되어 교차 도메인 전이가 자연스러워진다.
또한 CAMEL과 MetaGPT 등에서 역할이 하드코딩되어 있고, 이 하드코딩이 도메인 이식 시 병목이라는 분석은 플러그앤플레이 방식 Worker 교체를 가능케 하는 모듈형 설계의 당위성을 뒷받침한다.
학습 관점에서 전체 에이전트 파이프라인을 공동 훈련하는 것은 비효율적이고 고정된 툴 집합에 과적합하기 쉬우므로, 도메인 무관 Planner만을 표적화하여 최적화하는 "stable core, variable periphery" 철학이 필요하다.
아울러 GAIA 벤치마크처럼 웹 검색, 다중 모달 이해, 코드 실행, 문서 처리 등을 넘나드는 범용 AI 어시스턴트는 단일 에이전트로는 감당이 어려워 특화된 Worker들의 협업이 필수적이다.
마지막으로 오픈소스와 상용의 격차를 메우기 위한 학계의 요구가 커지고 있어, 완전 공개형(모델·데이터·코드)이면서 상용 수준 성능을 달성하는 프레임워크의 기여가 실질적 가치를 가진다.

---

## Method

1. **WORKFORCE 계층적 프레임워크 (3-구성요소)**: 도메인 무관 Planner Agent, 중앙 오케스트레이터 Coordinator Agent, 도메인 특화 Worker Nodes로 분리된 모듈형 추론 아키텍처.

2. **Planner Agent (도메인 무관)**: 입력된 고수준 목표를 Worker capability registry 기반으로 추상적 서브태스크 집합으로 분해하고, 최종적으로 각 서브태스크 결과를 종합해 최종 출력 합성.

3. **Coordinator Agent**: 중앙 오케스트레이션 허브로서 사용 가능한 Worker의 역량을 평가해 서브태스크를 적절한 Worker에게 배정하고 태스크 의존 관계를 관리하며 중간 결과를 통합.

4. **Worker Nodes (플러그앤플레이)**: (i) Web Agent (웹 검색·웹페이지 추출·브라우저 액션), (ii) Document Processing Agent (텍스트·이미지·오디오·비디오·스프레드시트·다형식 파일 처리), (iii) Reasoning/Coding Agent (분석적 추론·코드 실행)의 세 가지로 인스턴스화.

5. **공유 Task Channel 통신**: Coordinator가 태스크/배정을 공유 채널에 게시하고, Worker는 최종 결과만 채널로 되돌려 보내며, 도구 호출의 세부 실행 컨텍스트는 각 서브태스크 스코프 내에 격리되어 깨끗한 Worker 컨텍스트 유지. 에이전트 간 직접 메시징 제거.

6. **Task 상태 머신**: 서브태스크는 OPEN → RUNNING → DONE 상태로 전이되며, Planner→Coordinator→Worker→Channel→Coordinator→Planner의 6단계 파이프라인으로 실행.

7. **Replanning 메커니즘 (테스트-타임 스케일링)**: Worker가 스스로 서브태스크 실패 여부를 판정하여 실패 정보를 채널에 게시하면 Planner가 피드백을 받아 새 서브태스크를 생성. 기본 replanning threshold는 2이며, 이는 추론 시 동적 자기 교정을 가능하게 함.

8. **OWL 2단계 학습 전략**: (Stage 1) SFT로 Planner Agent를 전문가 궤적 기반 태스크 분해 능력으로 초기화 → (Stage 2) DPO(Direct Preference Optimization)로 SFT 초기화 모델을 실세계 피드백 기반 선호 학습으로 추가 최적화. Worker는 학습하지 않음.

9. **Task Curriculum (4개 데이터셋)**: (i) HotpotQA(멀티홉 추론), (ii) WikiTableQuestions(테이블 탐색·필터링), (iii) 커스텀 Math-related Problems(논리 추론·코딩), (iv) Infinity-MM(멀티모달 처리). 총 3,466 태스크로 Capability Coverage + Transfer Learning 두 원칙 구현.

10. **SFT Trajectory Synthesis**: GPT-4o-mini로 WORKFORCE를 구동하여 Planner 서브태스크 + Worker 실행 궤적을 합성. 데이터셋별 품질 필터 적용 — HotpotQA/WikiTableQuestions는 정확도 지표, Infinity-MM은 cosine similarity 0.7 임계값, Math는 LLM-as-a-judge. 최종 1,599개 궤적(평균 3.41 서브태스크).

11. **DPO Preference Pair 구성**: SFT 초기화 모델로 각 질문당 n=4 궤적 롤아웃 후, 정답/임계값 통과 여부로 "chosen/rejected" 선호 쌍 1,009개 구성.

12. **학습 하이퍼파라미터**: 8× NVIDIA H100, LlamaFactory 프레임워크, 최대 시퀀스 32,768 토큰, 학습률 1e-5, 2 epoch, bfloat16 혼합 정밀도, 유효 배치 크기 12(per-device 1 × gradient accumulation 12).

13. **추론 구성**: 모든 모델을 API로 접근(GPU 불필요), greedy decoding, GPT-4o는 pass@3, Claude-3.7-Sonnet은 pass@1 샘플링, GAIA 정답 유출 URL 차단.

---

## Key Contribution

1. **유연한 모듈형 다중 에이전트 아키텍처 WORKFORCE**: 추론과 학습 양쪽에서 교차 도메인 전이를 가능하게 하는 도메인 무관 Planner + 도메인 특화 Worker 분리 설계 제안.

2. **오픈소스 SOTA 성능**: GAIA 벤치마크에서 69.70% 달성하여 이전 오픈소스 최고(67.4%)를 넘고, 상용 OpenAI Deep Research(67.36%)조차 2.34%p 초과.

3. **효율적 학습 패러다임 OWL**: Planner 단독 학습만으로 Qwen2.5-32B-Instruct가 +16.37%p 향상되어 GPT-4o에 필적하는 성능에 도달하는 저오버헤드 학습 방식.

4. **완전 오픈소스 공개**: 코드·모델·데이터 전부 공개하여 오픈 리서치 커뮤니티에 기반 제공 (github.com/camel-ai/owl).

5. **Replanning 기반 테스트-타임 스케일링 입증**: 지상 정답 접근 없이도 replanning 횟수 증가에 따라 성능이 일관되게 개선됨을 보여 MAS의 자기 교정·자기 진화 능력을 실증.

6. **Planner 학습 우위 검증**: 동일 자원에서 Planner만 학습 시 45.45% vs Worker만 학습 시 31.51%, 둘 다 학습 시 46.68%로, Planner 최적화가 Worker 강화보다 훨씬 큰 효용을 준다는 경험적 근거 제시.

---

## Experiment & Results

- **벤치마크**: GAIA validation set — 범용 AI 어시스턴트 평가, 다중 도메인·다중 모달(멀티모달 이해·웹 브라우징·추론·복합 문제 해결).
- **비교 대상 (Proprietary)**: OpenAI Deep Research(O3), Langfun Agent v2.1(Claude-3.7), Trase Agent v0.3, h2oGPTe Agent v1.6.8, Anges, Ormind v0.1 등.
- **비교 대상 (Open-source)**: HuggingFace Open Deep Research, AutoAgent, TapeAgents, Magnetic-One, FRIDAY, Multi-Agent Exp v0.1, Single Agent, Role Playing(CAMEL).

**WORKFORCE 추론 성능 (GAIA)**:
- WORKFORCE(Claude-3.7-Sonnet): 평균 **69.70%** (Level 1: 84.91%, Level 2: 68.60%, Level 3: 42.31%).
- WORKFORCE(GPT-4o): 평균 60.61% — 동일 도구·모델 조건의 Single Agent(37.58%) 대비 +23.03%p, Role Playing(54.55%) 대비 +6.06%p.
- OpenAI Deep Research(O3) 67.36% 대비 +2.34%p, 이전 오픈소스 SOTA 55.76%(TapeAgents) 대비 약 +13.94%p.
- Level 1에서 84.91%로 Langfun Agent v2.1(83.02%) 대비 +1.89%p 신기록.

**OWL 학습 효과 (Qwen2.5-32B-Instruct 기반 Planner)**:
- 베이스: 36.36% (L1: 49.05 / L2: 33.72 / L3: 19.23).
- SFT: 41.21% (+4.85) — L3는 19.23 → 15.38로 -3.85%p 회귀.
- SFT+DPO(OWL): **52.73%** (+16.37%p) — L1: 67.92 (+18.87), L2: 51.16 (+17.44), L3: 26.92 (+7.69).
- OWL-Qwen2.5-32B는 GPT-4o-mini(47.27%)·Qwen2.5-72B-Instruct(49.09%)를 초과하고, Level 3에서 GPT-4o(26.92%)와 동률.

**Ablation — Trajectory Filtering**: 필터링 적용(OWL) 52.73% vs 필터링 없음 46.06%로 데이터 품질 > 양을 입증.

**Training Configuration Ablation**: Planner-only 45.45% > Both 46.68% ≫ Worker-only 31.51% (베이스 36.36%). Planner 학습이 지배적 이득.

**Test-time Scaling (Replanning)**: Claude-3.7-Sonnet WORKFORCE 평균 점수 0.60 → 0.69 (replanning 0→2), GPT-4o WORKFORCE 0.51 → 0.60. 지상 정답 없이 자기 교정.

**Capability별 성능**: Web Browsing·Multi-Modality·Diverse Filetype Reading·Reasoning·Coding 5개 축 전반에서 WORKFORCE가 Single Agent/Role Playing을 초과하며, OWL 학습 후 모든 축에서 일관 개선.

**Robustness (역량 수별)**: Role Playing은 필요 역량 1→≥3 구간에서 62.3% → 34.6%로 급락하지만, WORKFORCE는 모든 복잡도 구간에서 일관된 성능 유지.

**Error Analysis (Claude-3.7-Sonnet 결과, 수동 분석)**: Planner 실패 21.15%(Incorrect Plan·Subtask Ambiguity 등)가 에이전트 특화 오류 중 최대 비중으로, Planner 최적화의 중요성을 뒷받침. 나머지는 파운데이션 모델 한계·도구 관련 이슈가 약 절반.

---

## Limitation

저자 언급으로는 GAIA 벤치마크 한 가지에 집중한 평가로 인해 다른 실세계 태스크 영역에서의 일반화 검증이 부족하다.
또한 Error Analysis에서 약 절반의 실패가 파운데이션 모델 자체 한계 또는 도구 실패에서 기인해, Planner 개선만으로 돌파 가능한 상한에 근접하고 있음이 시사된다.
독자 관점에서 Planner의 DPO 학습은 수집된 HotpotQA·WikiTableQuestions·Math·Infinity-MM 네 데이터셋의 분포에 의존하므로 이 네 범주를 벗어난 완전히 새로운 도메인(예: 로보틱스·장기 계획)에 대한 제로샷 전이 성능은 검증되지 않았다.
Worker 노드의 도구 구성이 여전히 수동 설계에 의존하고 있어 "플러그앤플레이"라는 주장을 자동화된 Worker 합성까지 확장하지는 못한다.
Level 3 태스크에서 OWL 학습 후에도 26.92%에 그쳐, 복잡도가 높은 장기 추론 태스크에서 여전히 큰 갭이 남아 있다.
SFT 단독 학습이 Level 3에서 오히려 -3.85%p의 회귀를 보인 점은 SFT가 고난도 분해 전략을 오히려 왜곡할 수 있음을 시사하며, RL 없이 SFT만 사용 가능한 자원 제한 환경에서는 신중한 적용이 요구된다.
마지막으로 상용 Claude/GPT API에 의존한 추론 평가로 비용·재현성 측면의 제약이 있고, pass@3 vs pass@1 샘플링 차이로 인한 공정 비교 문제도 존재한다.
