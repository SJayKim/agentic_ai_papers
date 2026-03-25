# SeCom: On Memory Construction and Retrieval for Personalized Conversational Agents

> **논문 정보**: Zhuoshi Pan, Qianhui Wu, Huiqiang Jiang, Xufang Luo, Hao Cheng, Dongsheng Li, Yuqing Yang, Chin-Yew Lin, H. Vicky Zhao, Lili Qiu, Jianfeng Gao (Tsinghua University, Microsoft)
> **arXiv**: ICLR 2025
> **코드**: N/A

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 장기 대화에서 메모리 단위의 세분성(granularity)이 검색 정확도와 응답 품질에 결정적 영향을 미치지만, 기존 접근법들은 턴 단위(너무 세밀), 세션 단위(너무 거칠), 요약 기반(정보 손실) 방식 모두 최적이 아니다. |
| **Motivation** | 턴 단위 메모리는 단편적이고 불완전한 컨텍스트를 제공하며, 세션 단위는 무관한 정보를 과다 포함한다. 요약 기반 방법은 대화를 요약하는 과정에서 QA에 필수적인 세부 정보가 손실된다. 이 세 가지 한계를 동시에 해결하는 새로운 메모리 구성 단위가 필요하다. 또한 자연어의 내재적 중복성이 검색 시스템에 노이즈로 작용함을 발견했다. |
| **Limitation** | (1) 대화 분할 모델의 품질이 전체 성능을 좌우하며, GPT-4 기반 분할이 최고 성능이나 비용이 높다. (2) RoBERTa 기반 경량 분할 모델은 성능 하락이 있다 (GPT4Score 61.84 vs GPT-4 분할 69.33). (3) 압축 기반 디노이징의 최적 압축률이 태스크마다 다를 수 있다. (4) 세그먼트 경계가 모호한 대화에서는 분할 자체가 어려울 수 있다. |

---

## Method

SeCom은 장기 대화를 **토픽 일관 세그먼트**로 분할하고, **압축 기반 디노이징**으로 검색 정확도를 향상시키는 메모리 시스템이다.

1. **Segment-Level Memory Construction (세그먼트 단위 메모리)**
   - 각 대화 세션 `c`를 토픽 일관 세그먼트 `{s_k}`로 분할
   - 턴 단위(너무 세밀)와 세션 단위(너무 거칠) 사이의 최적 세분성 달성
   - 분할된 세그먼트를 메모리 뱅크의 기본 단위로 사용

2. **Conversation Segmentation Model**
   - **Zero-shot Segmentation**: LLM(GPT-4 또는 Mistral-7B)에 분할 가이드라인 `G`를 제공하여 세션을 세그먼트로 분할
   - **Self-Reflection 기반 가이드라인 학습**: SGD에 비유한 반복 최적화
     - 각 반복에서 분할 오류가 큰 "hard examples" K개 선택
     - LLM이 ground-truth 대비 오류를 반성(reflect)하여 가이드라인 `G` 업데이트
     - `G_{m+1} = G_m - η∇L(G_m)` — LLM이 암묵적으로 gradient를 추정

3. **Compression-based Memory Denoising**
   - 자연어의 내재적 중복성이 검색 시스템에 노이즈로 작용한다는 핵심 통찰
   - LLMLingua-2를 사용하여 메모리 단위에서 중복 제거 (압축률 75%)
   - 디노이징 후 검색: `{m_n} ← f_R(u*, f_Comp(M), N)`
   - 압축률 50% 이상에서 관련 세그먼트와의 유사도 증가 + 무관 세그먼트와의 유사도 감소 효과

4. **Retrieval & Response Generation**
   - BM25 또는 MPNet 기반 검색으로 쿼리와 관련된 상위 N개 세그먼트 검색
   - 검색된 세그먼트를 시간 순서로 연결하여 LLM에 컨텍스트로 제공

---

## Key Contribution

1. **메모리 세분성의 체계적 분석**: 턴·세션·요약 단위의 한계를 실증적으로 밝히고, 세그먼트 단위가 검색 정확도와 응답 품질 모두에서 우수함을 입증.
2. **압축 기반 디노이징**: 프롬프트 압축 기법을 메모리 검색의 노이즈 제거에 최초 적용. 자연어 중복이 검색 노이즈로 작용한다는 새로운 통찰.
3. **Self-Reflection 기반 분할 가이드라인 학습**: SGD에 비유한 반복적 가이드라인 최적화로 분할 품질 향상. 별도 학습 데이터 없이도 작동.
4. **경량 모델 지원**: GPT-4 외에 Mistral-7B, RoBERTa 기반 분할 모델도 지원하여 자원 제약 환경에서의 적용 가능성 확보.

---

## Experiment & Results

**데이터셋**: (1) LOCOMO — 평균 300턴, 9K 토큰의 장기 대화. (2) Long-MT-Bench+ — 멀티턴 벤치마크.

**비교 대상**: Turn-Level, Session-Level (BM25/MPNet), SumMem, RecurSum, ConditionMem, MemoChat, Zero/Full History

**LOCOMO 결과 (GPT4Score, BM25 기반)**:
- SeCom(GPT4-Seg): **71.57** vs Turn-Level 65.58, Session-Level 63.16, MemoChat 65.10, ConditionMem 65.92
- SeCom(Mistral-7B-Seg): 66.37 — GPT-4 대비 하락하나 여전히 경쟁력 유지
- Full History 54.15 — 전체 이력이 오히려 낮은 성능 (무관 정보의 해로움 입증)

**Long-MT-Bench+ 결과 (GPT4Score, MPNet 기반)**:
- SeCom(GPT4-Seg): **88.81** vs Turn-Level 84.91, MemoChat 85.14, Session-Level 73.38
- SeCom이 가장 적은 토큰(820)으로 최고 성능 달성

**Ablation - 디노이징 효과 (LOCOMO, MPNet)**:
- SeCom: GPT4Score 69.33 vs 디노이징 제거 시 59.87 (+9.46)
- 압축률 50% 이상에서 검색 recall 일관 향상

**Ablation - 세분성 비교**: 다양한 컨텍스트 예산(2K~8K 토큰)에서 세그먼트 단위가 턴·세션 단위보다 일관되게 우수.

**GPT-4 Pairwise 비교**: SeCom이 RecurSum 대비 58.86% WIN, SumMem 대비 50.49% WIN.
