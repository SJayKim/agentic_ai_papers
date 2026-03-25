# ACE: Agentic Context Engineering — Evolving Contexts for Self-Improving Language Models

> **논문 정보**: Qizheng Zhang, Changran Hu, Shubhangi Upasani 외 (Stanford University, SambaNova Systems, UC Berkeley)
> **arXiv**: 2510.04618v2 (2026.01, ICLR 2026)
> **코드**: https://github.com/ace-agent/ace

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM의 컨텍스트 적응(context adaptation) 방법들이 두 가지 핵심 한계를 가진다: (1) **Brevity bias** — 프롬프트 최적화가 간결하고 범용적인 지시로 수렴하여 도메인별 전략·실패 모드를 누락. (2) **Context collapse** — 반복적 전체 재작성이 축적된 지식을 짧은 요약으로 압축하여 갑작스러운 성능 하락 유발. |
| **Motivation** | 에이전트와 지식 집약 추론에서 성공은 상세한 태스크별 지식의 축적에 달려 있다. 인간과 달리 LLM은 긴 상세 컨텍스트에서 더 효과적이므로, 컨텍스트는 간결한 요약이 아닌 **포괄적이고 진화하는 플레이북**이어야 한다. Dynamic Cheatsheet에서 영감을 받되, context collapse 문제를 해결해야 한다. |
| **Limitation** | (1) 컨텍스트 크기가 계속 성장하므로 long-context 모델에 의존하며, 매우 긴 컨텍스트에서의 추론 품질 저하 가능성. (2) Generator/Reflector/Curator 모두 동일 LLM을 사용하므로, 모델 능력이 컨텍스트 품질의 상한. (3) 오프라인 적응에서 5 에포크가 필요하여 초기 비용 존재. (4) AppWorld과 금융 분석에 집중되어 다른 도메인에서의 효과는 추가 검증 필요. |

---

## Method

ACE는 컨텍스트를 **진화하는 플레이북**으로 관리하며, Generator-Reflector-Curator 3단계로 Context Collapse를 방지하는 프레임워크다.

1. **핵심 설계 원칙: 컨텍스트 = 진화하는 플레이북**
   - 컨텍스트를 단일 모놀리식 프롬프트가 아닌, **구조화된 bullet 컬렉션**으로 표현
   - 각 bullet: 메타데이터(고유 ID, helpful/harmful 카운터) + 콘텐츠(전략, 도메인 개념, 실패 모드)
   - 국소화·세분화 검색·점진적 적응 가능

2. **3역할 에이전틱 아키텍처**
   - **Generator**: 새 쿼리에 대해 추론 trajectory 생성, 어떤 bullet이 유용/해로웠는지 표시
   - **Reflector**: trajectory를 비평하여 구체적 교훈(lessons) 추출, 선택적으로 여러 라운드 정제
   - **Curator**: 교훈을 compact delta entries로 합성, 기존 컨텍스트에 결정론적으로 병합 (LLM 불필요)

3. **Incremental Delta Updates (점진적 델타 업데이트)**
   - 전체 재작성 대신, 소규모 delta contexts만 생성하여 기존 컨텍스트에 병합
   - Context collapse 방지: 과거 지식이 보존되고 새 통찰이 점진적으로 추가
   - 병렬 병합 가능 → 배치 적응 지원

4. **Grow-and-Refine**
   - 새 bullet 추가(grow) + 중복 제거(refine)의 균형
   - 시맨틱 임베딩으로 중복 bullet 탐지 및 프루닝
   - 적극적(매 delta 후) 또는 게으른(컨텍스트 윈도우 초과 시) 정제

5. **오프라인/온라인 적응**
   - **오프라인**: 학습 데이터로 시스템 프롬프트 최적화 (최대 5 에포크)
   - **온라인**: 추론 시 태스크 수행하면서 메모리로 실시간 적응 (라벨 불필요)

---

## Key Contribution

1. **Context Collapse 문제 정의 및 해결**: 모놀리식 재작성의 근본 한계를 규명하고, 구조화된 delta update로 해결.
2. **Reflector 분리**: 평가와 통찰 추출을 별도 역할로 분리하여 컨텍스트 품질과 성능 향상.
3. **라벨 불필요 적응**: 실행 피드백만으로 자기 개선 가능 — 라벨 없이도 14.8% 향상.
4. **비용 효율**: 기존 적응 방법 대비 86.9% 낮은 적응 지연, 더 적은 롤아웃과 토큰 비용.

---

## Experiment & Results

**모델**: DeepSeek-V3.1 (non-thinking mode), 동일 LLM으로 Generator/Reflector/Curator 수행

**비교 대상**: ICL, MIPROv2, GEPA, Dynamic Cheatsheet(DC)

**AppWorld (에이전트 벤치마크)**:
- ReAct + ACE (오프라인, GT 라벨): 평균 **59.4%** vs ReAct 42.4%, ICL 46.0%, GEPA 46.4%, DC 51.9% (+17.0%p)
- ReAct + ACE (오프라인, **라벨 없음**): 평균 **57.2%** — GT 라벨 대비 2.2%p만 하락
- test-challenge: ACE **39.6%** vs 리더보드 1위 시스템 수준 달성 (더 작은 오픈소스 모델로)

**금융 분석 (FiNER + Formula)**:
- FiNER: ACE **78.3%** vs DC 74.2%, GEPA 73.5% (+4.1%p)
- Formula: ACE **76.5%** vs DC 69.5%, GEPA 71.5% (+7.0%p)
- 평균 +8.6% over baselines

**효율성**:
- 적응 지연: ACE가 기존 방법 대비 86.9% 감소
- 롤아웃 비용: 더 적은 횟수로 더 높은 성능
- 온라인 모드에서 추가 비용 최소화하며 지속적 개선

**Ablation**:
- w/o Reflector: AppWorld 59.4→54.8 — 반성 역할의 기여 확인
- 단일 에포크 vs 5 에포크: 에포크 증가에 따라 단조 증가
- Context collapse 비교: DC가 18,282→122 토큰으로 붕괴, ACE는 안정적 성장
