# How Memory Management Impacts LLM Agents

> Zidi Xiong, Yuping Lin, Wenya Xie, Pengfei He, Zirui Liu, Jiliang Tang, Himabindu Lakkaraju, Zhen Xiang
> Harvard University, University of Georgia, Michigan State University, University of Minnesota-Twin Cities
> arXiv:2505.16067v2 (2025년 10월 10일)

---

## 필수 요소

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 기반 에이전트는 에피소딕 메모리(episodic memory)를 활용해 과거 실행 경험을 저장·검색하며 성능을 향상시킨다. 그러나 메모리 관리의 두 핵심 연산(추가·삭제)이 장기적 에이전트 동작에 어떤 영향을 미치는지에 대한 체계적 이해가 부족하다. 기존 연구들은 특정 에이전트 유형에만 맞춰진 전략(구조 변환, 요약, 반성 등)을 제안했지만, 서로 다른 에이전트 시스템에 범용적으로 적용 가능한 원리를 제공하지 못했다. |
| **Motivation** | 메모리 뱅크는 본질적으로 노이즈가 많은 에이전트 자체 생성 궤적(trajectory)을 포함하며 시간에 따라 동적으로 변화한다. 단순히 모든 실행을 저장(add-all)하면 잘못된 기록이 누적되어 미래 성능이 저하될 수 있다(자기-퇴화, self-degradation). 반면 메모리를 전혀 갱신하지 않으면(fixed-memory) 에이전트가 새로운 경험으로 자기 개선(self-improvement)을 할 수 없다. 이 두 극단 사이에서 어떤 메모리 관리 전략이 장기적으로 안정적인 성능을 보장하는지 밝혀야 한다. |
| **Method** | **실험 설계**: GPT-4o-mini를 백본으로 사용하는 4개의 에이전트(RegAgent, EHRAgent, AgentDriver, CIC-IoT Agent)에서 실험을 수행한다. **(1) 메모리 추가 전략**: ① 고정 메모리(추가 없음), ② 전체 추가(add-all), ③ 자동 평가 기반 선택적 추가(Coarse 1~3: GPT-4o-mini, GPT-4.1-mini, fine-tuned GPT-4.1-mini), ④ 엄격한 인간(오라클) 평가 기반 선택적 추가. **(2) 메모리 삭제 전략**: ① 주기적 삭제(일정 기간 내 검색 빈도가 임계값 α 이하인 기록 삭제), ② 이력 기반 삭제(n회 이상 검색된 기록 중 평균 유용성이 임계값 β 미만인 기록 삭제), ③ 혼합 삭제(주기적 + 이력 기반). **(3) 핵심 지표**: 입력 유사도(cosine similarity)와 출력 유사도(Pearson r) 간 상관관계, 장기 성공률(SR)/정확도(ACC), 메모리 크기. 태스크 분포 변화(distribution shift)와 메모리 자원 제약 시나리오도 별도로 실험한다. |
| **Key Contribution** | ① **경험 추종 속성(experience-following property) 발견**: 현재 태스크 쿼리와 검색된 메모리 기록 간 입력 유사도가 높을수록 출력 유사도도 높아진다는 현상을 정량적으로 규명. RegAgent에서 메모리가 충분히 커지면 Pearson r ≈ 1에 근접하는 거의 완벽한 상관관계를 확인. ② **두 가지 핵심 도전 과제 규명**: (a) **오류 전파(error propagation)**: 잘못된 메모리 기록이 현재 실행에 오류를 유발하고, 그 결과가 다시 메모리에 저장되면 미래 태스크까지 오류가 연쇄 확산됨. (b) **비정합 경험 재현(misaligned experience replay)**: 평가자의 품질 필터를 통과했음에도 불구하고 현재 태스크 분포와 맞지 않아 성능을 오히려 저해하는 메모리 기록의 존재. ③ **이력 기반 삭제 전략 제안**: 미래 태스크 평가 결과를 무료 품질 레이블로 활용하여 비정합 기록을 사후적으로 제거. ④ **평가자(evaluator) 설계의 결정적 중요성 강조**: 미세조정된 작은 평가자(300개 훈련 데이터)조차 off-the-shelf LLM 평가자보다 우수한 장기 성능을 달성함을 실증. |
| **Experiment/Results** | **메모리 추가 실험 (Table 1)**: 동일한 초기 메모리에서 시작하더라도 전략에 따라 장기 성능이 크게 갈린다. Add-all은 RegAgent 55.48 SR, EHRAgent 13.05 ACC, AgentDriver 32.32 SR, CIC-IoT 59.90 ACC로 최하위. 고정 메모리는 RegAgent 67.53 SR, EHRAgent 16.75 ACC, AgentDriver 40.11 SR, CIC-IoT 71.50 ACC. 엄격한 선택적 추가는 RegAgent 70.95 SR, EHRAgent 38.50 ACC, AgentDriver 51.00 SR, CIC-IoT 85.40 ACC로 최고 성능. 미세조정 평가자(C3)만으로도 EHRAgent 34.66 ACC, AgentDriver 47.37 SR, CIC-IoT 79.50 ACC를 달성하여 다른 coarse 평가자(C1, C2)를 크게 웃돔. **메모리 삭제 실험 (Table 2)**: 주기적 삭제는 메모리를 대폭 축소하면서도 성능 저하가 작다(예: 엄격 추가 + 주기적 삭제 시 AgentDriver SR 50.94로 삭제 전 51.00과 유사, 메모리 467로 1178에서 60% 감소). 이력 기반 삭제는 엄격한 평가자와 결합 시 성능 향상을 달성(EHRAgent 42.06 ACC, CIC-IoT 89.60 ACC — 삭제 전 38.67, 85.40 대비 향상). AgentDriver에서 엄격한 추가 + 혼합 삭제 조합은 약 1,000번째 태스크 이후 오류 없는(error-free) 변형 성능을 추월. **검색된 기록 정확도 (Table 4)**: EHRAgent에서 이력 기반 삭제로 유지된 기록의 정답률이 삭제된 기록보다 높음(4o-mini: 유지 44.1% vs. 삭제 36.3%; fine-tuned: 유지 54.8% vs. 삭제 48.2%). CIC-IoT에서도 유지 78.9% vs. 삭제 56.7%(4o-mini). **다른 LLM 백본에서도 일관된 경향 확인**: GPT-4o, DeepSeek-V3 모두 동일한 패턴을 보임. |
| **Limitation** | (1) **범위 제한**: 메모리 추가·삭제라는 두 가지 기본 연산에만 집중하며, 구조 변환(structural transformation), 병합(merging), 요약(summarization), 반성(reflection) 등 더 복잡한 메모리 업데이트 메커니즘은 다루지 않음. 이러한 고급 메커니즘을 통합한 시스템에 본 연구 결과를 직접 적용하려면 추가 분석이 필요함. (2) **이론적 보장 부재**: 연구 결과가 광범위한 실험적 분석에 기반하며, 수식적 이론 증명은 제공되지 않음. 에이전트 시스템의 복잡성 때문에 이론적 보장을 도출하기 어려움. (3) **읽으면서 느낀 한계**: 이력 기반 삭제의 효과가 평가자 품질에 크게 의존하며, 신뢰할 수 있는 평가자를 구축하는 비용(fine-tuning 등)이 실제 배포 환경에서는 부담이 될 수 있음. 또한 실험이 주로 GPT-4o-mini 기반으로 수행되어, 더 강력한 모델이나 오픈소스 모델에서의 일반화 가능성을 추가로 검증할 필요가 있음. |

---

## 선택 요소 (해당되는 것만)

| 항목 | 내용 |
|------|------|
| **Baseline 비교** | **메모리 추가**: 고정 메모리(fixed-memory) 대비 add-all은 모든 에이전트에서 성능 저하(예: RegAgent 67.53 → 55.48 SR). 엄격한 선택적 추가는 고정 메모리를 모두 상회(RegAgent +3.42 SR, EHRAgent +21.75 ACC, AgentDriver +10.89 SR, CIC-IoT +13.90 ACC). C3(fine-tuned) 평가자는 C1(GPT-4o-mini)보다 EHRAgent에서 +8.47 ACC, AgentDriver에서 +10.45 SR 향상. **메모리 삭제**: 삭제 없는 경우(no deletion) 대비 이력 기반 삭제는 엄격한 평가자 사용 시 EHRAgent +3.39 ACC, CIC-IoT +4.20 ACC 향상. 혼합 삭제는 가장 큰 메모리 절감 달성(엄격 평가자 + 혼합: EHRAgent 메모리 1012 → 248로 75% 절감). **오류 없는 변형(error-free baseline) 비교**: AgentDriver에서 엄격한 선택적 추가는 약 2,000번의 실행 이후 오류 없는 baseline과 거의 동일한 성능에 도달하거나 능가함. |
| **Ablation Study** | **평가자 품질의 영향**: C1(최대 오류 허용 1.6), C2(1.4), C3(1.2)로 점점 엄격한 coarse 평가자를 사용할수록 RegAgent SR이 63.18 → 65.78 → 67.35로 단조 증가. 엄격한 평가자(임계값 1.0)에서 70.95로 추가 향상. 이는 평가자 정밀도가 장기 성능에 직접적인 영향을 미침을 보여줌. **이력 기반 삭제 + 평가자 종류**: GPT-4o-mini를 평가자로 쓸 경우 AgentDriver에서 이력 기반 삭제가 오히려 성능 저하를 일으키지만, fine-tuned 평가자에서는 안정적 성능 유지. EHRAgent에서는 GPT-4o-mini 기반 이력 삭제가 성능 향상을 가져옴(에이전트·태스크별 차이 존재). **메모리 용량 제약**: AgentDriver에서 메모리 크기를 점점 늘릴수록 성능이 점진적으로 수렴하는 양상을 보이며, 엄격한 평가자 사용 시 무한 메모리 확장이 불필요함을 시사. |
