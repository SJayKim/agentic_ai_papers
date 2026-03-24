# Automated Design of Agentic Systems (ADAS)

**논문 정보**: Shengran Hu, Cong Lu, Jeff Clune (University of British Columbia, Vector Institute)
**게재**: ICLR 2025 (arXiv:2408.08435v2, 2025년 3월)

---

## 필수 요소

| 항목 | 내용 |
|------|------|
| **Problem** | 에이전틱 시스템(Chain-of-Thought, Self-Reflection, Toolformer 등)의 빌딩 블록과 설계가 현재 모두 인간이 수작업으로 제작(hand-designed)되고 있음. 빌딩 블록을 새로 발견하거나 이를 효과적으로 조합하는 데 도메인별 수작업 튜닝과 막대한 연구자·엔지니어 노력이 요구됨. 기존 자동화 시도(PromptBreeder, DSPy, GPT-Swarm 등)는 프롬프트 최적화나 제한된 그래프/네트워크 구조에만 국한되어 있어 에이전트가 가질 수 있는 모든 설계 공간을 탐색하지 못함. |
| **Motivation** | ML 역사의 반복되는 교훈: 수작업 산출물은 결국 학습된 솔루션으로 대체됨(HOG → CNN, 수작업 손실 함수 → DiscoPOP, 수작업 신경망 구조 → NAS). 에이전틱 시스템도 같은 경로를 밟을 것이므로, 빌딩 블록과 에이전트 설계를 자동으로 발명·최적화하는 연구 분야(ADAS)가 필요함. 또한 가능한 빌딩 블록의 수가 방대하여 연구자들이 수작업으로 모두 발견하기에는 시간이 지나치게 많이 소요됨. |
| **Method** | **ADAS(Automated Design of Agentic Systems)** 프레임워크를 정의하고, 그 안에서 **Meta Agent Search** 알고리즘을 제안. 핵심 아이디어: 에이전트를 Python 코드(Turing Complete)로 표현하여 모든 가능한 에이전트 설계를 이론적으로 탐색 가능하게 함. **알고리즘 동작 방식**: (1) 아카이브를 기존 베이스라인 에이전트(CoT, Self-Refine 등)로 초기화; (2) 메타 에이전트(GPT-4)가 아카이브를 바탕으로 고수준 설계 아이디어를 기술하고 `forward()` 함수를 Python 코드로 구현; (3) 2회 자기반성(self-reflection)으로 novelty 및 오류 점검; (4) 검증 데이터로 평가 (오류 발생 시 최대 5회 재시도); (5) 평가 결과와 함께 아카이브에 추가 후 반복. 100줄 미만의 간단한 프레임워크(namedtuple Info, FM 쿼리 래퍼)를 메타 에이전트에게 제공하여 `forward()` 함수만 작성하면 되도록 구성. **ADAS 세 구성 요소**: 탐색 공간(Search Space), 탐색 알고리즘(Search Algorithm), 평가 함수(Evaluation Function). |
| **Key Contribution** | (1) **ADAS라는 신규 연구 분야 정의**: 에이전틱 시스템 자동 설계를 AutoML/AI-GAs 맥락에서 형식화. (2) **코드 공간 탐색 접근법 제안**: Python과 같은 Turing-Complete 언어로 에이전트 전체(프롬프트, 툴 사용, 워크플로 등 모든 구성 요소)를 표현·탐색하는 최초 알고리즘 중 하나. 기존 프롬프트 최적화(OPRO 등)나 그래프 최적화(GPT-Swarm 등) 대비 설계 공간이 본질적으로 더 포괄적. (3) **도메인/모델 간 전이 가능성 실증**: 한 도메인(수학)에서 발견된 에이전트가 비수학 도메인에서도 수작업 베이스라인을 초과하는 성능 달성. (4) **진화적 stepping stone 패턴 관찰**: 메타 에이전트가 여러 단계에 걸쳐 아이디어를 축적·조합하여 점진적으로 더 강력한 에이전트 발명. |
| **Experiment/Results** | **태스크**: (1) ARC 챌린지(시각 그리드 변환 규칙 추론, 5×5 이하 Easy 부분집합, 검증 20문항 / 테스트 60문항); (2) 4개 추론 벤치마크: DROP(읽기 이해), MGSM(다국어 수학), MMLU(다중 태스크), GPQA(대학원 수준 과학); (3) 도메인/모델 전이 실험. **설정**: 메타 에이전트=GPT-4, 발견된 에이전트 평가=GPT-3.5. ARC는 25 iteration, 나머지는 30 iteration 수행. **주요 수치**: ① DROP(읽기 이해): 최고 베이스라인(Role Assignment) F1 65.8 → Meta Agent Search **F1 79.4** (+13.6); ② MGSM(수학): 최고 베이스라인(LLM Debate) 39.0% → **53.4%** (+14.4%p); ③ MMLU(다중 태스크): 65.9% → **69.6%**; ④ GPQA(과학): 32.9% → **34.6%**; ⑤ ARC: CoT 6.0% → 최적 발견 에이전트 **13.7%**(GPT-3.5), Claude-Sonnet 전이 시 **48.3%**. **전이 실험**: MGSM에서 발견한 에이전트를 GSM8K로 전이 시 베이스라인 대비 +25.9%p, GSM-Hard +13.2%p 향상. 비수학 도메인(DROP, MMLU)으로 전이해도 수작업 베이스라인 초과. **비용**: ARC 실험 약 $500, 추론 도메인 실험 약 $300 (OpenAI API). |
| **Limitation** | (1) **단일 목표 최적화만 고려**: 현재 성능(accuracy/F1)만 최적화하며 비용, 지연 시간, 안전성 등 다목적 최적화는 미포함. (2) **단일 단계 QA 태스크에 국한**: 복잡한 환경과 다단계 상호작용이 필요한 실제 응용에는 아직 미검증. (3) **검색 알고리즘의 단순성**: 현재 메타 에이전트는 "흥미로운 새 설계 탐색"에만 집중하며 탐색-활용 균형, Quality-Diversity 등 정교한 전략은 미사용. (4) **고비용 평가 함수**: 검증 셋 전체 실행이 비용을 높이며 성공/실패 패턴 등 풍부한 정보를 활용하지 못함. (5) **안전성 우려**: 모델이 생성한 코드가 의도치 않은 파괴적 행동을 할 위험이 있으며, 저자들은 컨테이너화 실행과 수작업 검사로 일부 완화하였으나 근본적 해결은 아님. (6) **초기화 방식에 따른 민감성**: 수학 도메인의 경우 빈 초기화(empty initialization)가 오히려 더 좋은 성능(Math 67.5% vs 53.4%)을 보여, 초기화 전략의 이론적 이해가 아직 부족함. |

---

## 선택 요소 (해당되는 것만)

| 항목 | 내용 |
|------|------|
| **Baseline 비교** | **수작업 에이전트 7종**: Chain-of-Thought (CoT), COT-SC (Self-Consistency), Self-Refine, LLM Debate, Step-back Abstraction, Quality-Diversity, Role Assignment. **ADAS 베이스라인 1종**: Prompt Optimization (OPRO). 핵심 격차: DROP에서 CoT F1 64.2 대비 Meta Agent Search F1 79.4(+15.2), MGSM에서 LLM Debate 39.0% 대비 53.4%(+14.4%p). OPRO(프롬프트만 최적화) 대비로도 모든 도메인에서 Meta Agent Search가 일관되게 우위 (예: DROP F1 69.1 → 79.4, MGSM 30.6% → 53.4%). 이는 프롬프트뿐 아니라 워크플로 전체를 코드로 탐색하는 것의 이점을 직접 입증. |
| **Ablation Study** | **초기화 방식 ablation (Appendix I, Table 6)**: 베이스라인 에이전트로 초기화하는 표준 방법 vs. 빈 초기화(empty initialization) 비교. ① Reading Comprehension: 초기화 있음 F1 79.4 > 빈 초기화 F1 73.9 (초기화 유리); ② Math: 초기화 있음 53.4% < 빈 초기화 67.5% (빈 초기화가 오히려 유리 - 다양한 추론 전략 탐색 장려); ③ Multi-task: 초기화 있음 69.6% > 빈 초기화 68.5%; ④ Science: 초기화 있음 34.6% > 빈 초기화 32.7%. 빈 초기화에서도 모든 도메인에서 수작업 베이스라인을 초과하여 방법론의 강건성을 입증. |
