# 91. O-Researcher: An Open Ended Deep Research Model via Multi-Agent Distillation and Agentic RL

> 📄 **저자**: Yi Yao, He Zhu (core contributors), Wangchunshu Zhou (corresponding) (OPPO AI Agent Team / PersonalAI Lab)
> 📚 **학회/발표 기관**: arXiv preprint (OPPO)
> 📅 **발표 날짜**: 2026.01
> 🔗 **arXiv**: https://arxiv.org/abs/2601.03743
> 💻 **코드**: https://github.com/OPPO-PersonalAI/O-Researcher (모델: HuggingFace PersonalAILab/O-Researcher-72B-sft·-rl)

---

## Problem

오픈소스 LLM이 폐쇄형(GPT-4o, OpenAI o1 등) 대비 뒤처지는 핵심 원인은 모델 구조가 아니라 고품질 학습 데이터와 막대한 연산 자원에 대한 접근성 격차다.
이 격차는 특히 긴 사고 사슬(chain-of-thought)과 엄밀한 문제 해결을 요구하는 추론 집약적 태스크, 즉 deep research 영역에서 가장 두드러진다.
기존 데이터 확보 방식인 인간 주석은 비용이 과도하고 규모가 제한적이며, 더 큰 교사 모델로부터의 distillation은 교사의 한계를 그대로 물려받는다.
더 결정적인 병목은, 표준 distillation이 최종 답변(final answer)만 포착하고 복잡한 문제 해결에 필요한 "사고 과정(thought process)"은 전이하지 못한다는 점이다.
즉 deep research의 본질인 질의 계획 수립 → 도구 통합 탐색 → 증거 종합 → 최종 보고서 작성으로 이어지는 반복적·탐색적 전 과정(end-to-end trajectory)을 담은 학습 코퍼스가 부재하다.
따라서 독점 API나 모델에 의존하지 않고 오픈소스 모델을 SOTA 수준으로 끌어올릴 자동화된 데이터 합성 프레임워크가 필요하다.

---

## Motivation

핵심 직관은 "전문화된 AI 에이전트들의 협업 생태계가 인간의 엄밀한 연구 과정(특히 peer-review식 분해·토론·검증)을 자율적으로 시뮬레이션할 수 있다"는 것이다.
단일 모델이 긴 호흡의 복잡한 질의를 한 번에 처리하면 컨텍스트 경쟁(context competition)으로 세부 증거가 희석되므로, 질의를 직교적(orthogonal) 하위 작업으로 분해해 병렬 처리하면 각 차원에서 고밀도 증거를 보존할 수 있다.
이렇게 합성된 고품질 trajectory는 단순 정답이 아니라 전체 추론 트레이스를 담으므로, SFT만으로도 모델이 연구 프로토콜 자체를 학습하게 된다.
그러나 SFT만으로는 trajectory가 길어지며 중복·노이즈가 늘어 인용 정확도가 떨어지는 부작용이 생기므로, 이를 교정할 보상 기반 정렬(agentic RL)이 추가로 필요하다.
즉 멀티에이전트 distillation(지식 기반 구축)과 agentic RL(품질·사실성 정밀 교정)을 결합한 2단계 전략이, 독점 자산 없이 격차를 메우는 확장 가능한 경로라는 것이 저자들의 핵심 동기다.

---

## Method

전체는 3단계 파이프라인이다: (1) deep research 보고서 생성 워크플로우 설계 및 고품질 trajectory 합성, (2) 오픈소스 모델에 SFT, (3) agentic RL로 도구 사용·보고서 생성 능력 강화.

**(1) 병렬 실행 기반 고품질 trajectory 합성 (SFT 데이터)**
멀티에이전트 시스템은 planner, tool-user, summarizer(fusion 모델)로 구성된다.
planner가 하나의 질의를 직교적 하위 질의(sub-query) 집합으로 분해하여, 장기 호흡 문제를 병렬화 가능한 원자적(atomic) 작업으로 변환한다(TaskCraft의 width-based task extension 차용).
서로 다른 모델들이 각 하위 질의에 대해 독립적으로 다회차 도구 통합 추론, 즉 연속적인 Plan-Execute-Observe(Think-Tool-Observation) 루프를 수행해 하위 보고서를 생성한다.
summarizer가 하위 보고서들을 통합해 최종 답변을 만들고, 모든 하위 질의의 트레이스와 보고서를 하나의 SFT 추론 트레이스로 병합한다(병렬 추론의 깊이를 전부 학습 데이터에 담음).
시드 질의는 Zhihu-KOL, WideSearch, ELI5 등 오픈 데이터셋과 LLM 합성 주제에서 개방형·고난도 기준으로 5,000개를 큐레이션했다.

**(2) 다단계 거부 샘플링 품질 보증 파이프라인 (funnel 구조)**
질의마다 3개의 후보 trajectory를 oversampling(diversity-driven generation)해 다양한 추론 경로를 확보한다.
규칙 기반 hard rejection: 모든 도구 호출·태그가 완결되었는지(completeness), 컨텍스트가 64k 토큰 이내인지, 최소 10단계 추론 + 5개 distinct 도구 사용을 충족하는지(complexity), 포맷 유효성·언어 일관성(consistency)을 결정론적으로 검사해 탈락시킨다.
규칙을 통과한 후보는 Qwen3 기반 LLM-as-a-Judge가 논리적 일관성·도구 사용 적절성·증거 근거성 같은 고차 품질을 평가해 최적 trajectory를 선별한다(model-based semantic filtering).
마지막으로 최고 점수 trajectory에 대해 주제 계층화된 인간 spot-check를 수행하며, 저품질로 표시되면 원 질의를 재처리하는 regeneration 루프가 작동한다.
이 funnel을 거쳐 3,500+개의 premium instruction-response 쌍이 최종 SFT 코퍼스로 남는다.

**(3) 구조화된 데이터 표현 (XML 스키마)**
trajectory를 8개 함수/태그로 직렬화하여 모델이 Thinking-Acting-Observing-Answering 루프를 강제로 따르게 한다.
워크플로우 제어 태그(`<subtask_list>`, `<subtask>`), 인지 태그(`<think>`=내부 추론 독백, `<plan>`=구체적 단계별 행동 계획), 행동 태그(`<web_search>`, `<crawl_page>`), 피드백 태그(`<observation>`=도구 출력), 응답 태그(`<subtask_answer>`, `<suggested_answer>`=최종 보고서)로 구성된다.
규칙상 항상 `<subtask_list>`로 시작하고 각 subtask 내에서 think가 plan/tool보다 먼저 와야 하며, 모든 핵심 사실에는 `[1]` 형식 인용이 붙고 최종 답은 Introduction/Body/Conclusion/References를 포함해야 한다.

**(4) AI 피드백 기반 강화학습 (RLAIF, GRPO)**
SFT 모델로 정책을 초기화하고 Group Relative Policy Optimization(GRPO)으로 학습한다.
선호 데이터는 LLM으로 다도메인 연구 질문을 합성한 뒤, SFT 모델로 질문당 8개 응답을 생성·평가해 점수가 일관되게 높거나(너무 쉬움) 일관되게 낮은(너무 어려움) 질문을 제거하고 "sweet spot" 난이도만 남겨 학습 신호를 극대화한다.
보상은 R = w1·R_base + w2·R_tool + w3·R_format (w1=0.6, w2=0.2, w3=0.2)의 가중 합으로, 보고서 품질을 가장 중시한다.
R_base는 LLM-as-a-Judge가 comprehensiveness/insight/instruction-following/readability 4차원을 평가한 평균이고, R_tool은 도구 호출 수 N_calls=min(web_search, crawl_page)를 [N_min=2, N_max=8] 구간으로 정규화하되 2 미만이면 0, 8 초과면 -1을 부여해 과소·과다 호출을 모두 벌한다.
R_format은 모든 XML 태그의 대칭적 닫힘과 `<suggested_answer>` 존재를 검증하며 위반 시 0이다(최종 보상은 [0,1]로 정규화).
관찰 마스킹(observation masking)으로 도구 출력 토큰을 손실 계산에서 제외하며, GRPO 학습 중 평균 응답 길이 증가, web-search·crawl-page 호출 증가(특히 crawl-page), 초기 정책 엔트로피 급락 후 점진적 반등이 관찰되었다.

---

## Key Contribution

1. **멀티에이전트 기반 end-to-end deep research 데이터 합성 워크플로우**: 여러 LLM 에이전트가 복잡 태스크를 분해·토론·검증(peer-review식)하여, 표준 모델 생성 텍스트를 능가하는 고품질 학습 코퍼스를 확장 가능하게 생산하는 파이프라인을 제안.
2. **병렬 실행(parallel execution) trajectory 합성**: 질의를 직교 하위 질의로 분해해 독립 병렬 추론 후 트레이스를 병합함으로써, 단일 긴 컨텍스트에서 발생하는 증거 희석(context competition)을 완화하고 추론 깊이를 보존.
3. **2단계 학습 전략(SFT + 신규 RLAIF)**: SFT로 연구 프로토콜의 강한 지식 기반을 세우고, GRPO 기반 RL로 보고서 효과성·사실 근거성·자가 교정 능력을 정밀 교정.
4. **3요소 복합 보상 설계**: 품질(R_base)·도구 사용 효율(R_tool)·포맷 준수(R_format)를 결합하고, 도구 호출 수에 상·하한 페널티를 둔 보상으로 SFT 단계의 인용 정확도 저하를 회복.
5. **다단계 거부 샘플링 + XML 구조화 표현**: 규칙→LLM-judge→인간 검증 funnel과 8태그 스키마로 사고·행동·관찰·답변 루프를 명시적으로 학습 가능하게 만들어, 검증 가능하고 투명한 연구 능력 배양.

---

## Experiment & Results

**벤치마크/평가지표**: DeepResearch Bench(박사급 100개 연구 태스크, 4개 도메인)와 DeepResearchGym(commercial 구성, 공식 100-task subset)을 사용.
DeepResearch Bench는 RACE(보고서 품질: comprehensiveness/depth/instruction-following/readability)와 FACT(사실성: citation accuracy / effective citations) 두 지표 군으로 평가.
**백본**은 Qwen-2.5-72B-Instruct이며, baseline은 Deep Research Agents(OpenAI/Gemini/Perplexity/Grok deep research, MiroFlow, OAgents, WebWeaver)와 Deep Research Models(GPT-5, O3, Gemini-2.5, Kimi-K2, MiniMax M2, Tongyi-Deep Research, MiroThinker 등)로 구성.

**DeepResearch Bench 주요 수치**:
- O-Researcher-RL이 RACE Overall **48.48**로 오픈웨이트 deep research 모델 중 신규 SOTA를 달성, Tongyi-Deep Research(45.66)와 MiroThinker(41.79)를 큰 폭으로 상회.
- 검색 강화 상용 LLM도 능가: GPT-5(46.77), OpenAI O3(43.71), Kimi-K2-Thinking(45.65), MiniMax M2(46.06)를 모두 상회하고 Perplexity Deep Research(42.25)도 추월.
- 백본 대비 변화가 가장 극적: Qwen-2.5-72B(Overall 33.38) → O-Researcher-SFT는 **+12.86↑**(46.24), Effective Citations는 8.96 → +13.67↑(22.63)로 급증.
- 단, SFT는 trajectory가 길어지며 Citation Accuracy가 44.27% → 29.13%로 하락(중복·노이즈 부작용).
- RL 단계가 이를 교정: Citation Accuracy 29.13% → **31.99%**, Effective Citations 22.63 → **26.01**로 회복하며 depth는 백본 대비 +26.13↑(49.54) 달성.

**DeepResearchGym(Commercial-100) 주요 수치**:
- O-Researcher-72B가 오픈소스 모델 중 SOTA이며 상용 에이전트와도 경쟁: Clarity **100.00**, Insight **99.3** 기록.
- Citation Precision **51.45**로 표 내 전 카테고리 최고치(높은 recall 94.61 유지하면서 환각 인용 회피), KPR(relevance) 77.28로 검색 강화 LLM을 크게 상회.

**Ablation**:
- 병렬 실행 효과: GPT-5에 병렬 워크플로우 적용 시 Overall 42.92 → **49.60**, Comprehensiveness 40.59 → 49.61, Insight 38.58 → 48.69로 모든 지표 상승.
- 추론 단계 수: OAgents 프레임워크에서 5단계(48.80) < 10단계(49.61) < 20단계(50.76)로, 10단계를 성능/비용 균형의 최적값으로 채택.
- 컨텍스트 길이: 32k→64k에서 큰 성능 향상, 64k→128k는 수확 체감(plateau)으로 64k 채택.

---

## Limitation

저자가 명시한 한계로는, 컨텍스트 길이를 64k 이상으로 늘려도 성능 향상이 정체된다는 점과, FACT 평가에서 reference link를 제공하지 못하는 모델(예: Tongyi)은 비교 자체가 불가능하다는 평가 체계의 제약이 있다.
또한 SFT가 trajectory 길이·복잡도 증가로 인용 정확도를 떨어뜨리는 trade-off가 본질적으로 존재하며, RL로 완화하더라도 31.99%로 여전히 백본(44.27%)보다 낮아 정밀도 손실이 완전히 회복되지는 않는다.
독자 관점에서 보면, R_base와 데이터 필터링 모두 LLM-as-a-Judge(Qwen3 등)에 의존하므로 판정자 모델의 편향·reward hacking 위험이 결과 품질에 직결되며, 인간 검증은 spot-check 수준이라 대규모 품질 보장에는 한계가 있다.
평가가 DeepResearch Bench·DeepResearchGym 두 보고서 생성 벤치마크에 국한되어, GAIA·BrowseComp·HLE 같은 다른 deep research/에이전트 벤치마크에서의 일반화는 검증되지 않았다.
실제 영향 측면에서, 도구가 web_search/crawl_page 2종에 한정되고 보상이 도구 호출 수를 2~8회로 제약하므로, 더 다양한 도구나 장기 호흡 태스크로 확장 시 보상 설계 재조정이 필요할 수 있다.
