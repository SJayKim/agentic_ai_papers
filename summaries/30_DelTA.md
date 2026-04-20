# DelTA: An Online Document-Level Translation Agent Based on Multi-Level Memory

> **논문 정보**: Yutong Wang, Jiali Zeng, Xuebo Liu, Derek F. Wong, Fandong Meng, Jie Zhou, Min Zhang (HIT Shenzhen, Tencent WeChat AI, University of Macau)
> **arXiv**: 2410.08143 (2024.10, v2 2025.03)
> **코드**: https://github.com/YutongWang1216/DocMTAgent

---

## Problem

LLM 기반 문서 수준 기계 번역(DocMT-LLM)은 LLM의 최대 컨텍스트 길이 제약 때문에 긴 문서를 한 번에 처리할 수 없고, 문서를 창(window) 단위로 나누어 번역해야 한다.
창 크기를 키우면 고유명사 번역 일관성은 개선되지만(윈도우 1에서 LTCR-1 75.09% → 윈도우 50에서 86.94%), 번역 누락 문장 수가 급증하는 부작용이 나타난다(윈도우 50에서 10문장 누락).
반대로 창 크기를 줄이면 문장 간 담화(discourse) 정보와 문맥 단서가 사라져 대명사·고유명사 번역이 불일치하고 문서 전체의 톤과 장르가 깨진다.
Doc2Doc 방식(전체 문서를 한 대화에 넣고 번역)은 환각(hallucination)과 긴 텍스트 처리 능력 부족으로 문장 단위 정렬이 깨지며, sCOMET 같은 문장 단위 품질 지표로 평가하기조차 어렵다.
특히 영어→중국어처럼 고유명사를 음차해야 하는 언어쌍에서는 동일 인물/지명이 문서 안에서 여러 번역으로 나타나 독자의 가독성을 심각하게 해친다.
기존 LTCR 지표는 최초 번역과의 일치 여부를 평가하지 못하고 전체 번역 쌍 간 단순 일관성만 측정해, 독자 경험을 반영하기에 부적합하다.

## Motivation

법률·기술 매뉴얼·문학 번역처럼 정밀도와 일관성을 동시에 요구하는 도메인에서는 단일 고유명사의 번역 흔들림만으로도 신뢰도가 급락한다.
실제 GPT-3.5-Turbo로 IWSLT2017 En→Zh를 번역한 예비 실험에서 고유명사 일관성(LTCR-1) 75~87%, 누락 문장 최대 10건이라는 두 문제가 창 크기와 양(兩)방향 트레이드오프를 보인다.
LLM 기반 자율 에이전트가 전용 메모리 구조를 통해 환경으로부터 핵심 정보를 저장/검색하며 복잡한 장기 과제를 해결한다는 선행 연구(Generative Agents, ReadAgent 등)에 주목한다.
문서 번역에도 서로 다른 granularity(고유명사-단어, 요약-문서, 문장-국소)와 span(전역, 장기, 단기)의 정보가 동시에 필요하다는 관찰을 방법론의 출발점으로 삼는다.
Doc2Sent(문서→문장) 접근은 문장 누락을 구조적으로 방지하고 메모리 누적을 억제하지만, 전통적 Doc2Sent는 단순히 소스 문맥만 인코딩해 담화 일관성에 한계가 있었다.
따라서 저자들은 문장 단위 온라인 번역에 "다중 레벨 메모리+LLM 보조 컴포넌트"를 결합하면 정확성과 일관성을 동시에 달성할 수 있다고 가정한다.
추가로 기존 LTCR 대신 "최초 번역과의 일치율"인 LTCR-1을 도입해 독자 경험 중심으로 일관성을 재정의할 필요성도 제기한다.
이러한 동기에서 DELTA(Document-levEL Translation Agent)라는 온라인 에이전트가 설계된다.

## Method

1. **전체 알고리즘**: 소스 문서 Ds={s1,…,sN}를 문장 단위로 순차 처리하며, 각 단계에서 (a) 메모리 검색 → (b) 번역 → (c) 메모리 갱신의 3단계를 반복한다.

2. **Proper Noun Records R (최상위 메모리)**: 고유명사 p와 최초 번역 T1(p)의 딕셔너리를 유지. 번역 직전 현재 문장 si에 포함된 고유명사를 조회(R̂)해 프롬프트에 삽입하여 일관성을 강제한다.

3. **Proper Noun Extractor L_Extract**: LLM 기반 컴포넌트로, 각 문장 번역 직후 (si, ti)에서 신규 고유명사와 그 번역을 추출해 R에 추가한다. 기존에 없던 쌍만 등록한다.

4. **Bilingual Summary (2단계 메모리)**: 소스 요약 As와 타겟 요약 At를 쌍으로 유지. As는 이미 번역된 부분의 주요 내용·도메인·스타일·톤을 담고, At는 번역 결과의 주요 내용을 담아 번역 전 전역 문맥을 LLM에 제공한다.

5. **Two-step Summary Update**: m=20 문장마다 갱신. ① L_WriteS/L_WriteT가 최근 m문장의 세그먼트 요약 Ãs, Ãt를 생성 → ② L_MergeS/L_MergeT가 기존 요약 A^(i)와 세그먼트 요약을 병합해 A^(i+1)을 만든다. 두 단계 분리로 요약 길이 폭주를 억제한다.

6. **Long-Term Memory N (3단계)**: 직전 l=20 문장의 소스-타겟 쌍을 슬라이딩 윈도우로 보관. 번역 전 L_Retrieve(si, N)이 현재 문장과 가장 관련 있는 n=2 문장을 선택해 few-shot 예시로 삽입한다.

7. **Short-Term Memory M (최하위 4단계)**: 직전 k=3 문장의 소스-타겟 쌍을 그대로 프롬프트 문맥으로 주입해, 대명사·시제·담화 마커 같은 국소 단서를 유지한다.

8. **Document Translator L_Translate**: 통합 프롬프트로 번역 수행. ti = L_Translate(si, R̂^(i), N̂^(i), As^(i), At^(i), M^(i)) — 네 메모리를 모두 소비한다.

9. **온라인 문장-단위 출력**: 문장별로 즉시 번역해 타겟 문서 Dt에 추가하므로 문장 정렬이 자동 보장되고, 문장 단위 메트릭(sCOMET) 적용이 가능하다.

10. **메모리 갱신 주기 설계**: 고유명사 기록과 STM/LTM은 매 문장 즉시 갱신, Bilingual Summary만 m=20 주기로 갱신해 LLM 호출 비용을 제어한다.

11. **메모리의 추상-구체 계층화**: 상위(Record·Summary)는 전역·추상·고밀도 정보, 하위(LTM·STM)는 국소·구체·원문 그대로의 정보를 담아 각기 다른 번역 결정 요소를 지원한다.

12. **프롬프트 통합 방식**: R̂는 "이 단어는 이렇게 번역" 지시어로, Summary는 "지금까지의 문서 맥락"으로, LTM은 "관련 예시"로, STM은 "직전 문맥"으로 각각 역할 분리되어 삽입된다.

---

## Key Contribution

1. **다중 레벨 메모리 문서 번역 에이전트 DELTA**: 고유명사 레코드·이중 요약·장기 메모리·단기 메모리의 4단계 계층을 설계해 서로 다른 granularity/span의 정보를 독립적으로 저장·검색한다.

2. **Doc2Sent 재평가와 실증**: 문장 단위 온라인 번역이 문장 누락을 완전히 없애고 메모리 효율적임을 보이면서, 다중 메모리로 문맥 단절 문제까지 해결함을 실증한다.

3. **LTCR-1 및 LTCR-1f 지표 제안**: 기존 LTCR과 달리 "최초 번역과의 일치율"을 측정해 독자 관점의 일관성을 정량화한다. awesome-align 오류를 완화하는 퍼지 버전 LTCR-1f도 함께 제안한다.

4. **DocMT-LLM의 핵심 문제 정량 분석**: 창 크기 1~50에 대한 체계적 실험으로 "일관성 vs. 누락" 트레이드오프를 수치로 드러내고(윈도우 50에서 누락 10문장) 해결 방향을 제시한다.

5. **Summary 컴포넌트의 범용성**: Bilingual Summary를 QMSum 질의 기반 요약에 적용해 ReadAgent 대비 ROUGE-L 21.50 → 23.60으로 향상, 번역 전용 모듈이 일반 요약에도 유효함을 보인다.

6. **장거리 일관성 및 Pronoun/Context-Dependent 번역 개선**: 51문장 이상 거리에서도 DELTA가 일관성 유지, APT 59.96→61.07, 컨텍스트-의존 번역 정확도 29.7%→51.0%로 담화 현상 처리 능력을 입증한다.

7. **Doc2Doc 대비 메모리 비용 절감**: Qwen2-72B로 En→Zh 번역 시 Doc2Doc는 490 문장 근처에서 OOM 발생하지만 DELTA는 꾸준히 완만한 증가만 보여 로컬 배포 친화적이다.

---

## Experiment

**데이터셋**: IWSLT2017 tst2017 (TED 토크, 8개 언어쌍 En↔Zh/De/Fr/Ja, 언어쌍당 10~12문서 약 1.5K 문장), Guofeng Webnovel V1 TEST 2 (Zh→En 웹소설).

**백본 모델 4종**: GPT-3.5-Turbo-0125, GPT-4o-mini, Qwen2-7B-Instruct, Qwen2-72B-Instruct. max_new_tokens=2048, m=l=20, n=2, k=3.

**Baseline**: Sentence(독립 문장 번역), Context(직전 3문장 문맥), Doc2Doc(10문장 배치 번역, Wang et al. 2023b 재현), NLLB-3.3B, Google Translate.

**메트릭**: sCOMET (wmt22-comet-da), dCOMET (wmt21-comet-qe-mqm), LTCR-1, LTCR-1f.

**IWSLT2017 평균 결과 (4모델)**:
- En→Xx: DELTA sCOMET 84.36, dCOMET 6.57, LTCR-1 81.63%, LTCR-1f 87.82% — Sentence 대비 +3.14 sCOMET, +4.36%p LTCR-1.
- Xx→En: DELTA sCOMET 84.69, dCOMET 7.11, LTCR-1 85.09%, LTCR-1f 95.48% — Sentence 대비 +3.16 sCOMET, +4.58%p LTCR-1.
- GPT-3.5-Turbo En⇒Zh: LTCR-1이 80.27 → 86.44로 +6.17%p (En⇒De는 92.06→93.46, +1.40%p — 알파벳 공유 언어는 증가폭 작음).
- t-test: 품질 메트릭은 En↔Xx 전반 p<0.05, 일관성은 En↔Zh에서 p<0.05.

**Guofeng 웹소설 결과 (Zh→En)**:
- GPT-4o-mini: DELTA LTCR-1 88.94% vs Sentence 58.82% (+30.12%p), Doc2Doc 82.04%.
- Qwen2-7B: DELTA LTCR-1 85.50% vs Sentence 37.00% (+48.50%p), LTCR-1f 94.00% vs Sentence 50.00%.
- 강한 모델일수록 DELTA 개선폭이 크다(강한 모델은 메모리 활용이 더 효과적).

**Ablation (GPT-3.5-Turbo En⇒Zh)**: Sentence 기반(80.27 LTCR-1) → +STM(77.89) → +LTM(79.23) → +Bilingual Summary(82.49, 93.60 LTCR-1f) → +Record(DELTA 86.44, 95.25). Bilingual Summary가 Source/Target 단독 요약보다 전 메트릭에서 우수.

**보조 실험**:
- Consistency Distance: 51문장 이상 거리에서 DELTA가 Sentence/Context/Doc2Doc 대비 가장 높은 일관 번역 비율 달성.
- APT(Pronoun 정확도): DELTA 61.07 > Context 60.84 > Sentence 59.96 > Doc2Doc 56.11.
- CTX-PRO context-dependent 번역: Sentence 29.7% → DELTA 51.0% (+21.3%p).
- QMSum 요약: DELTA ROUGE-L 23.60, length 82.28 vs ReadAgent 21.50, 67.86.
- 메모리 비용: Qwen2-72B 2×A800에서 Doc2Doc는 490문장에서 OOM, DELTA는 1200문장 이상 처리 가능.

---

## Limitation

저자 언급: DELTA의 추론 효율성이 최적화되지 않았으며, 문장별 LLM 호출과 4개 보조 컴포넌트(Extractor, 2 Summary Writer, 2 Merger, Retriever, Translator)가 누적되어 실행 시간이 길다.
저자 제안 개선안 1: 문장 경계 태그를 명시적으로 삽입해 여러 문장을 한 번에 번역하도록 하면 호출 빈도를 줄일 수 있으나 본 논문에서는 구현하지 않았다.
저자 제안 개선안 2: 고유명사 추출을 LLM 대신 정밀 정렬 도구와 스크립트로 대체하면 효율이 향상되지만 검증되지 않았다.
독자 관점 한계 1: Summary 갱신 주기 m=20, LTM 길이 l=20, 검색 개수 n=2, STM 길이 k=3 등 하이퍼파라미터가 고정 값으로만 실험되어 도메인/장르별 적응성이 미검증이다.
독자 관점 한계 2: 평가가 IWSLT(강연)와 Guofeng(웹소설) 두 도메인에 집중되어 법률·의료·기술 매뉴얼 등 DELTA의 주요 타깃 도메인에서 직접 검증이 없다.
독자 관점 한계 3: LTCR-1은 spaCy 고유명사 추출과 awesome-align 정렬에 의존해 언어별 도구 성능 편차가 지표 신뢰도에 영향을 주며, LTCR-1f는 부분 문자열 포함 기준이라 짧은 번역에 유리하게 편향될 여지가 있다.
독자 관점 한계 4: En⇒De처럼 알파벳 공유 언어쌍에서는 개선폭이 1.40%p로 작아 방법의 실질 이득이 언어쌍 특성에 강하게 좌우된다.
독자 관점 한계 5: Proper Noun Records는 첫 번역이 오류일 경우 오류가 문서 전체에 전파되는 구조이나, 이러한 첫 번역 품질에 대한 분석이나 보정 기제가 제공되지 않는다.
