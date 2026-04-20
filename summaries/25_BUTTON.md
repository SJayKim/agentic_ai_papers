# BUTTON: Facilitating Multi-Turn Function Calling for LLMs via Compositional Instruction Tuning

> **논문 정보**: Mingyang Chen, Haoze Sun, Tianpeng Li, Fan Yang, Hao Liang, Keer Lu, Bin Cui, Wentao Zhang, Zenan Zhou, Weipeng Chen (Baichuan Inc., Peking University)
> **arXiv**: ICLR 2025
> **코드**: N/A

---

## Problem

기존 LLM function calling 연구는 대부분 단일 턴(single-turn) 시나리오에 집중되어 왔다.

즉, 주어진 질의 한 번에 적절한 함수 하나를 선택하고 올바른 인자를 채우는 능력을 학습시키는 데 초점이 맞춰져 있다.

그러나 실세계의 사용자 쿼리는 본질적으로 조합적(compositional)이며, 단일 함수 호출로 해결되지 않는 경우가 많다.

예를 들어 "런던에서 에든버러로 가는 첫 비행편을 예약해줘"는 먼저 비행 스케줄을 조회하고, 이어서 첫 편을 예약하는 다단계 함수 호출을 필요로 한다.

이러한 다턴(multi-turn) function calling은 함수 이해·선택을 넘어 함수들 간의 계획(planning with functions)을 요구하지만, 기존 모델들은 이 능력이 부족하다.

또한 조합적 쿼리와 그에 대응하는 다턴 함수 호출 궤적을 가진 지시(instruction) 데이터를 수집하는 것이 매우 어렵다.

기존 합성 데이터 파이프라인들은 조합성(compositionality), 지시와 함수 간 호환성(compatibility), 다턴 궤적 품질을 동시에 보장하지 못한다.

결과적으로 LLM은 조합 태스크의 분해와 순차적 함수 호출 능력에서 심각한 공백을 보인다.

---

## Motivation

실세계 복합 태스크는 본질적으로 조합적이며, LLM은 단순히 함수를 호출하는 수준을 넘어 다단계 계획을 세워야 한다.

"The Great Gatsby 저자의 생일은 언제인가?"라는 질의를 보면, 먼저 `get_author("The Great Gatsby")`로 저자를 찾은 뒤 `search_birthday(Scott Fitzgerald)`로 생일을 조회해야 한다.

이는 하나의 원자(atomic) 태스크가 아니라, 두 개의 원자 태스크를 순차적으로 결합한 조합 태스크이다.

이러한 조합 태스크 데이터를 수작업으로 대규모로 수집하는 것은 비용과 시간 측면에서 비현실적이다.

합성 데이터 생성은 유망한 대안이지만, 세 가지 도전이 존재한다: (1) 지시가 조합성을 가지면서 복잡·합리·해결가능해야 하고, (2) 생성된 지시와 함수 정의가 서로 호환되어야 하며, (3) 인간 감독 없이도 고품질 다턴 궤적을 시뮬레이션해야 한다.

기존 연구(Gorilla, ToolLLM, APIGen 등)는 단일 턴에 집중하거나 함수를 먼저 수집한 뒤 지시를 생성하여 현실성·조합성이 제한된다.

따라서 저자들은 원자 태스크에서 출발해 상향식으로 조합 태스크를 구성하고, 하향식으로 다에이전트 시뮬레이션을 통해 궤적을 생성하는 BUTTON 파이프라인을 제안한다.

---

## Method

BUTTON(Bottom-Up Then Top-Down)은 멀티턴 function calling 데이터를 합성하기 위한 2단계 파이프라인이다.

1. **Scenario Collection**: `glaive-function-calling-v2`와 `ToolLLaMA` 데이터셋에서 "항공편 예약", "식사 주문" 같은 실세계 시나리오를 추출하고, 문장 임베딩 기반 중복 제거 후 확장 프롬프트로 시나리오를 다양화한다.

2. **Atomic Task Construction**: 각 시나리오로부터 단일 단계로 해결 가능한 원자 태스크를 생성하며, 세 가지 제약을 지킨다 — Reasonable(현실적), Self-contained(필요 정보 포함), Function-agnostic(특정 함수·해결책 언급 금지). 30단어 이내.

3. **Compositional Task Construction - Sequential**: 원자 태스크의 결과를 입력으로 사용하는 후속 태스크를 생성하여 둘을 결합한다. 예: "저자 찾기" → "저자 생일 찾기" → "Gatsby 저자의 생일은?".

4. **Compositional Task Construction - Parallel-then-Sequential**: 원자 태스크와 병렬 실행 가능한 또 다른 태스크를 생성한 뒤, 두 결과에 의존하는 후속 태스크를 추가한다. 예: "런던→에든버러 항공편" + "에든버러 시간별 날씨" → "첫 비행 도착 시 날씨는?".

5. **Compositional Task Filtering**: 생성된 조합 태스크가 원래의 원자 서브태스크들로 해결 가능한지 검증하여 일관성 없는 데이터 제거.

6. **Function Generation (Task-first)**: 기존 방식(함수 먼저, 태스크 나중)과 반대로, 조합 태스크와 그 서브태스크 분해를 힌트로 삼아 함수 정의를 생성. `name`, `description`, `parameters`, `responses`, `required` 5개 필드 포함.

7. **Function Design Principles**: Descriptive(이름·설명 명확), General(`get_weather(city)`처럼 재사용 가능), Consistency(순차 호출 시 앞 함수 출력이 뒷 함수 입력과 정렬).

8. **Sub-task to Function Mapping**: 하나의 서브태스크는 0·1·여러 함수에 매핑 가능. 논리·비교·계산 등 LLM 자체로 처리 가능한 작업은 함수 없이 처리.

9. **Multi-Agent Setup**: Top-Down 단계에서 User Agent(조합 쿼리 제시 및 추가 정보 제공), Assistant Agent(ReAct 형식 사고 + 함수 호출), Tool Agent(함수 정의 기반 실행 결과 시뮬레이션) 세 에이전트를 시스템 프롬프트로 구성.

10. **Trajectory Generation**: User가 시작한 대화에서 Assistant가 태스크를 서브태스크로 분해 → 해당 함수 호출 → Tool Agent로부터 결과 수신 → 추가 함수 호출 또는 최종 답변 생성 루프 수행.

11. **Consistency Enforcement**: 각 Assistant 행동을 여러 번 생성한 뒤 일관된 결정만 채택하여 궤적 품질 보장.

12. **Parallel Function Calling**: 독립적으로 호출 가능한 다수의 함수는 같은 턴에 병렬 실행하도록 데이터 구성. 병렬 ON/OFF는 시스템 프롬프트로 제어.

13. **Data Format**: 최종 데이터는 `system`, `user`, `assistant`, `tool` 역할로 구성되며, 시스템 프롬프트에 호출 가능한 함수 목록이 주어진다.

14. **BUTTONInstruct**: GPT-4o(gpt-4o-2024-05-13)로 전 파이프라인을 실행하여 8,000개 멀티턴 function calling 지시-궤적 데이터 생성.

15. **Fine-Tuning**: Llama3-8B, Llama3-70B, Qwen2-7B, Qwen2-72B를 BUTTONInstruct로 instruction-tuning하여 `-BUTTON` 접미사 모델을 생성.

---

## Key Contribution

1. **Bottom-Up Then Top-Down 파이프라인 제안**: 원자 태스크에서 조합 태스크를 구성하는 상향식 단계와, 다에이전트 시뮬레이션으로 궤적을 생성하는 하향식 단계를 결합하여 합성 데이터의 조합성·호환성·궤적 품질을 동시에 확보.

2. **Task-first Function Generation**: 기존의 "함수 먼저, 태스크 나중" 패러다임을 뒤집어, 태스크 분해를 힌트로 함수를 생성함으로써 함수가 더 일반적이고 현실적이며 세분화된 서브태스크에 적합해짐.

3. **두 가지 조합 전략(Sequential / Parallel-then-Sequential)**: 단순하지만 강력한 두 휴리스틱으로 다양한 다턴·다함수 패턴을 커버, 병렬 호출까지 포괄.

4. **BUTTONInstruct 데이터셋 공개**: 8,000개 멀티턴 function calling 지시-궤적 데이터를 오픈소스로 공개(PKU-Baichuan-MLSystemLab/BUTTON).

5. **멀티턴 function calling SOTA 달성**: Llama3-70B-BUTTON과 Qwen2-72B-BUTTON이 GTA 및 Tool-Query 벤치마크에서 GPT-4o에 필적하는 성능 달성.

6. **계획 능력 학습의 효과 입증**: 소규모(8K) 합성 데이터만으로도 LLM이 함수 사용을 넘어 함수 간 계획 능력을 학습할 수 있음을 실험적으로 증명.

---

## Experiment

**모델**: Llama3-8B, Llama3-70B, Qwen2-7B, Qwen2-72B를 BUTTONInstruct로 파인튜닝하여 비교.

**벤치마크 1 - GTA**: 229개 인간 작성 쿼리, 14개 실세계 도구(perception/operation/logic/creation 카테고리), 멀티모달 이미지 포함. Step-by-Step Mode(Inst./Tool./Arg./Summ. 4지표)와 End-to-End Mode(P./O./L./C. F1 + Ans.) 평가.

**벤치마크 2 - Tool-Query**: weather(18개 도구), movies(14개), academia(7개) 3개 도메인, 60개 태스크. Grounding Accuracy, Process Rate(서브골 달성), Success Rate 평가. Easy/Hard 분리.

**GTA 주요 결과**:
- Llama3-8B-Instruct의 최종 답변 정확도(Ans.)가 1.4%에서 Llama3-8B-BUTTON 30.5%로 약 22배 향상.
- Qwen2-7B: Ans. 13.1% → 27.3%, Arg. 3.9% → 30.7%.
- Llama3-70B-BUTTON은 Tool. 73.6%, Arg. 38.1%로 GPT-4o(70.3%, 38.6%)를 상회하거나 근접.
- Qwen2-72B-BUTTON의 Ans. 45.7%는 GPT-4o(46.0%)에 필적.

**Tool-Query 주요 결과**:
- Llama3-8B-BUTTON: Process Rate(All) 48.1% → 63.2%, Success Rate 5.0% → 35.0%.
- Llama3-70B-BUTTON: Success Rate 31.7% → 58.3%로 거의 2배 상승, GPT-4o(40.0%)·GPT-4-Turbo(41.7%) 초과.
- Qwen2-72B-BUTTON: Success Rate 41.7% → 58.3%, Hard 샘플 34.4% → 46.9%.
- Grounding Accuracy는 기본 instruct 모델도 95% 이상으로 이미 높지만, Process/Success Rate 격차가 계획 능력 차이를 드러냄.

**Ablation Study (Tool-Query)**:
- w/o Bottom-Up, w/o Top-Down 두 설정과 full BUTTON 비교.
- Llama3-8B: 평균 상대 성능 감소 16.1%, Llama3-70B: 6.4% (소형 모델이 더 큰 영향).
- 모델·설정 전반 평균 Success Rate 감소 15.0%, Process Rate 감소 7.5% — Top-Down이 최종 답변(계획)에, Bottom-Up이 전 과정에 기여.

**Data Scaling**:
- Llama3-8B를 2K/4K/6K/8K로 학습 시, Process Rate 56.5% → 63.2%, Success Rate 21.7% → 35.0%로 증가.
- Average Growth Rate: Process 13.5%, Success 2.7%. Hard 샘플에서 개선이 더 큼(Success Hard AGR 5.5%).

**데이터 통계 (BUTTONInstruct)**:
- 대부분 궤적이 3턴 이상의 Assistant 응답 포함.
- 대부분 궤적이 2개 이상의 function call 포함.
- 턴당 평균 function call 수는 모든 턴에서 1 이상이며, 후속 턴으로 갈수록 증가.

**Parallel Calling 효과**:
- Llama3-8B-BUTTON에서 병렬 호출 비활성화 시 Success Rate 35.0% → 28.3%, Process Rate 63.2% → 58.7%로 감소.

---

## Limitation

BUTTON은 Sequential과 Parallel-then-Sequential 두 가지 조합 전략만 사용하며, 조건부 분기·반복·예외 처리 같은 더 복잡한 제어 흐름은 다루지 않는다.

함수 정의 자체가 LLM으로 합성되므로 실제 세계의 REST API·SDK와의 시그니처·인자 호환성이 보장되지 않으며, 실제 배포 시 재매핑이 필요할 수 있다.

Tool Agent가 함수 실행을 시뮬레이션하기 때문에 실제 API 호출에서 발생하는 네트워크 오류·rate limit·시간 지연·불일치한 응답 처리 능력은 학습되지 않는다.

데이터 규모가 8,000개로 제한적이며, Data Scaling 실험에서 성능이 아직 포화되지 않은 것으로 보여 더 큰 규모에서의 거동은 미검증이다.

벤치마크가 GTA(229개)와 Tool-Query(60개)로 비교적 소규모이고, 특정 도메인(weather/movie/academia 등)에 국한되어 일반화 범위 주장에 제약이 있다.

데이터 생성에 GPT-4o를 사용하므로 생성 비용과 라이선스·정책 제약이 따르며, GPT-4o의 편향이 데이터에 상속될 가능성이 있다.

Compositional Task Filtering은 "원자 서브태스크로 해결 가능한지"만 검증하고 궤적 단계별 정확성·효율성(최소 호출 수)은 엄밀히 검증하지 않아, 학습 데이터에 비효율적 호출 패턴이 포함될 수 있다.

사용자 쿼리에 대한 명시적 선호·대화 맥락 유지·개인화 등 진정한 장기 다턴 대화 능력은 평가 범위에 포함되지 않았다.
