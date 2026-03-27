# AvaTaR: Optimizing LLM Agents for Tool-Augmented Reasoning via Contrastive Reasoning

> **논문 정보**: Shirley Wu, Shiyu Zhao, Qian Huang, Kexin Huang, Michihiro Yasunaga, Kaidi Cao, Vassilis N. Ioannidis, Karthik Subbian, Jure Leskovec, James Zou (Stanford University / Amazon)
> **arXiv**: 2406.11200 (2024.06, NeurIPS 2024)
> **코드**: https://github.com/zou-group/avatar

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전트의 도구 사용 프롬프트를 수동으로 최적화하는 것은 비효율적이고 태스크 특화적이다. 기존 자동 프롬프트 최적화(self-reflection, self-refine)는 단일 인스턴스 기반 피드백에 집중하여 복잡한 다단계 도구 사용에서 발생하는 시스템적 오류를 파악하지 못한다. |
| **Motivation** | 성공(positive)과 실패(negative) 도구 사용 궤적을 배치 단위로 대조적으로 분석하면, 특정 케이스에 과적합되지 않고 시스템적이고 범용적인 도구 사용 전략을 자동으로 추출할 수 있다. 이를 반복적으로 프롬프트에 반영하면 재학습 없이도 도구 활용 능력 향상이 가능하다. |
| **Limitation** | (저자 언급) 프롬프트 최적화의 수렴 속도가 태스크 복잡도에 비례하며, 고비용 LLM 호출이 다수 필요하다. (독자 관점) 대조적 추론의 효과는 도구 수와 도구 간 상호작용이 많아질수록 확장성이 미검증이며, 훈련 샘플 수(100개 내외)가 충분한지 일반화 근거가 약하다. 비용 대비 효과 분석도 부족하다. |

---

## Method

AvaTaR는 **Actor LLM**과 **Comparator LLM** 두 컴포넌트로 구성되며, 최적화와 배포 단계로 나뉜다.

**1. Actor 구성**
- Actor는 초기 태스크 설명과 도구 정보를 프롬프트로 받아 도구 호출 시퀀스(action sequence)를 Python 코드 + 자연어 설명 형태로 생성
- 최적화 중 Comparator로부터 업데이트된 instructions를 받아 반복적으로 개선

**2. Comparator를 통한 대조적 추론 기반 자동 지시 생성**
- Step 1: 현재 action sequence를 훈련 데이터에 적용하여 성능 상위(positive, Recall > ℓ)와 하위(negative, Recall < h) 쿼리를 분류 (배치 크기 b=20)
- Step 2: Comparator가 positive/negative 배치를 비교하여 (1) 문제 분해 전략 결함, (2) 비효율적 도구 조합, (3) 점수 합성 방식 문제를 식별하고 전체적(holistic) 개선 지시문 생성
- 배치 단위 대조를 통해 특정 케이스에 과적합되지 않는 "robust gradient"를 추출하는 것이 핵심

**3. Logistic Instructions와 Memory Bank**
- Validity Check: 각 action 실행 시 함수 호출의 올바름을 내부적으로 검증
- Timeout Error: 비효율적 action sequence의 교착 상태 방지
- Memory Bank: 과거 상위 5개 action sequence와 해당 성능 및 Comparator 지시문을 저장 (Reflexion의 episodic memory에서 영감)

**4. 배포 단계**
- 최적화 완료 후, 최고 성능 action sequence 또는 optimized instruction을 새로운 쿼리에 직접 적용
- 검색 태스크에서는 optimized action sequence 직접 배포, QA 태스크에서는 optimized instruction 사용

**5. 전체 최적화 특성**
- 파인튜닝 없이 소규모 훈련 데이터(~100개)와 도구 설명만으로 에이전트를 최적화
- Self-Improvement, Memory, Generalization, Holistic Prompt Generation 모두를 지원하는 유일한 프레임워크

---

## Key Contribution

1. **대조적 추론 기반 자동 프롬프트 최적화**: positive/negative 배치를 비교해 시스템적 도구 사용 오류를 식별하고 holistic instruction을 자동 생성하는 Comparator 모듈 최초 제안
2. **7개 벤치마크에서 일관된 SOTA**: 검색 태스크(4개)에서 Hit@1 평균 +14%, QA 태스크(3개)에서 평균 +13% 향상
3. **강력한 일반화**: leave-out 쿼리에서 STARK 벤치마크 Hit@1 평균 +20.9% 향상
4. **신흥 행동(Emerging Behavior)**: 최적화 과정에서 IDF 기반 재가중치 같은 고수준 도구를 에이전트가 자체 개발하는 현상 관찰

---

## Experiment & Results

- **벤치마크**: STARK(AMAZON, MAG, PRIME), FLICKR 30K-ENTITIES, HotpotQA, ArxivQA, ToolQA(SciREX/Agenda) 총 7개
- **베이스라인**: DPR, QAGNN, ada-002, ReAct, Reflexion, ExpeL, Retroformer, CoT

**검색 태스크 주요 결과**:
- STARK-AMAZON: Hit@1 49.87% (Reflexion 42.79% 대비 +16.6%), MRR 58.70%
- STARK-MAG: Hit@1 44.36% (Reflexion 40.71% 대비 +9.6%)
- STARK-PRIME: Hit@1 18.44% (Reflexion 14.28% 대비 +20.7%)
- FLICKR: Hit@1 42.4%, Recall@20 79.2%, MRR 52.3%

**QA 태스크**:
- HotpotQA: 53.0% (Reflexion 46.0% 대비 +15.2%)
- ToolQA SciREX-HARD: 23.3% (Reflexion 13.3% 대비 +33.1% 상대 향상)

**최적화 진행**: STARK 검증 성능이 AMAZON 35%→75%, MAG 20%→78%로 대폭 향상

**Ablation**: Comparator 제거 시 대부분 ReAct 수준으로 하락 — Comparator가 핵심 성능 기여 요소

**일반화**: leave-out 쿼리에서 Hit@1 평균 +20.9% 달성
