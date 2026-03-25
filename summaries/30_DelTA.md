# DelTA: An Online Document-Level Translation Agent Based on Multi-Level Memory

> **논문 정보**: Yutong Wang, Jiali Zeng, Xuebo Liu, Derek F. Wong, Fandong Meng, Jie Zhou, Min Zhang (HIT Shenzhen, Tencent WeChat AI, University of Macau)
> **arXiv**: 2410.08143 (2024.10)
> **코드**: https://github.com/YutongWang1216/DocMTAgent

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 기반 문서 수준 기계 번역(DocMT)은 번역 윈도우를 키우면 고유명사 일관성은 높아지지만 문장 누락이 발생하고(50문장 윈도우에서 10문장 누락), 윈도우를 줄이면 문맥 단절로 일관성이 떨어지는 트레이드오프가 존재한다. |
| **Motivation** | 법률·기술 문서 등 정밀 번역이 필요한 도메인에서 고유명사 번역 불일치(LTCR-1 75~87%)와 문장 누락은 실용성을 심각하게 저해한다. 문장 단위 번역의 정확성과 문서 수준 문맥의 일관성을 동시에 달성하는 에이전트 설계가 필요하다. |
| **Limitation** | 저자 언급: 문장별 번역으로 인해 문단 단위 번역 대비 LLM 호출 횟수가 증가하여 비용과 지연이 큼. 독자 관점: Proper Noun Extractor와 Retriever가 별도 LLM 호출을 필요로 하여 전체 파이프라인 비용이 상당히 높음. Summary 갱신 주기(m=20)가 고정되어 문서 장르별 최적화 미검증. |

---

## Method

1. **4단계 다중 레벨 메모리 구조** (전역 → 지역, 추상 → 구체)
   - **Proper Noun Records (최상위)**: 고유명사-번역 딕셔너리. 문서 내 최초 등장 번역을 기록하고 이후 동일 고유명사에 재사용하여 일관성 보장
   - **Bilingual Summary (2층)**: 원문/번역문 각각의 요약을 유지. m문장마다 세그먼트 요약 → 기존 요약과 병합하는 2단계 업데이트로 문서 전체의 맥락·장르·톤 보존
   - **Long-Term Memory (3층)**: 최근 l문장(l=20) 쌍을 저장. LLM Retriever가 현재 원문과 가장 관련 높은 n개(n=2) 문장을 검색하여 few-shot 예시로 활용
   - **Short-Term Memory (최하위)**: 직전 k문장(k=3) 쌍을 그대로 프롬프트에 삽입하여 인접 문맥 제공

2. **문장별 온라인 번역 (Doc2Sent)**
   - 원문을 한 문장씩 순차 번역: t_i = L_Translate(s_i, R̂, N̂, A_s, A_t, M)
   - 4개 메모리에서 검색한 정보를 프롬프트에 통합
   - 번역 후 즉시 메모리 업데이트: Proper Noun Extractor로 신규 고유명사 추출, LTM/STM에 문장 쌍 추가

3. **LLM 기반 보조 컴포넌트**
   - Proper Noun Extractor: 원문·번역문에서 새 고유명사와 번역을 추출
   - Source/Target Summary Writer: 세그먼트 요약 생성
   - Summary Merger: 세그먼트 요약을 전체 요약에 병합
   - Memory Retriever: Long-Term Memory에서 관련 문장 검색

---

## Key Contribution

1. **문서 번역 전용 다중 레벨 메모리 에이전트**: 고유명사 일관성(Proper Noun Records), 전역 문맥(Bilingual Summary), 중거리 문맥(LTM), 단거리 문맥(STM)을 계층적으로 분리하여 각기 다른 정보 요구를 충족
2. **Doc2Sent 접근의 재평가**: 문장별 번역이 문장 누락을 완전히 방지하면서 메모리 효율적임을 실증하고, 다중 레벨 메모리로 문맥 단절 문제를 해결
3. **LTCR-1 메트릭 제안**: 최초 번역과의 일관성을 측정하는 새로운 고유명사 일관성 지표

---

## Experiment & Results

- **데이터셋**: IWSLT2017 (8개 언어 쌍, TED 토크), Guofeng Webnovel (Zh→En, 소설)
- **LLM 백본**: GPT-3.5-Turbo, GPT-4o-mini, Qwen2-7B-Instruct, Qwen2-72B-Instruct
- **Baseline**: Sentence (문장 단독), Context (3문장 문맥), Doc2Doc (10문장 배치)

**IWSLT2017 평균 결과**:
- En→Xx: DELTA sCOMET 84.36 (Sentence 81.22, +3.14), LTCR-1 81.63% (Sentence 77.27%, +4.36%p)
- Xx→En: DELTA sCOMET 84.69 (Sentence 81.53, +3.16), LTCR-1f 95.48% (Sentence 90.80%, +4.68%p)
- Doc2Doc 대비: sCOMET과 LTCR-1 모두 DELTA가 우수하며, 문장 누락 0건

**Guofeng Webnovel (GPT-4o-mini)**:
- DELTA LTCR-1 88.94% vs Sentence 58.82%, Doc2Doc 82.04% — 장편 소설에서 고유명사 일관성 +30%p 향상
- DELTA LTCR-1f 96.48% vs Context 74.37%

**Ablation**: 각 메모리 제거 시 성능 하락 확인 — Proper Noun Records 제거 시 LTCR-1이 가장 크게 하락, Bilingual Summary 제거 시 dCOMET 하락이 두드러짐
