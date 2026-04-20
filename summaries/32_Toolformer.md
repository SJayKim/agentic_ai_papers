# Toolformer: Language Models Can Teach Themselves to Use Tools

> **논문 정보**: Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli, Luke Zettlemoyer, Nicola Cancedda, Thomas Scialom (Meta AI Research, Universitat Pompeu Fabra)
> **arXiv**: 2302.04761 (2023.02)
> **코드**: N/A

---

## Problem

대형 언어 모델은 few-shot 혹은 제로샷 세팅에서 다양한 자연어 태스크를 인상적으로 해결하지만, 가장 단순한 기능들에서 구조적으로 취약한 모순을 보인다.
구체적으로 정밀한 산술 계산이 불가능하고, 최근 사건이나 시간 진행에 대한 정보 접근이 제한되며, 저자원 언어 이해에서 성능이 급격히 떨어진다.
또한 사실 조회가 필요한 상황에서 할루시네이션(hallucination)을 빈번하게 발생시키는 문제가 있다.
이러한 한계는 단순히 모델 스케일을 키운다고 근본적으로 해결되지 않는 본질적 성격을 가진다.
기존 도구 사용 연구들은 대량의 인간 주석(Komeili 2022, Nakano 2021, Thoppilan 2022 등)에 의존하거나, task-specific한 프롬프트로 특정 태스크에만 제한되어 적용(Gao 2022, Parisi 2022, Yao 2022)되는 한계가 있다.
따라서 LM이 "언제, 어떤 도구를, 어떤 인자로" 호출할지를 스스로 결정하고 범용적으로 학습할 수 있는 방법이 부재했다.
인간이 유용하다고 판단하는 도구 사용 패턴과 모델이 실제로 필요로 하는 패턴이 다를 수 있다는 점도 인간 주석 기반 접근의 본질적 한계이다.

---

## Motivation

외부 도구(검색 엔진, 계산기, 캘린더, 번역기, QA 시스템)는 LM이 가진 고유한 한계를 원리적으로 보완할 수 있는 자연스러운 해법이다.
저자들은 도구 사용 학습이 다음 두 가지 desiderata를 만족해야 한다고 주장한다 — (1) 인간 주석 없이 self-supervised 방식으로 학습, (2) 범용성을 잃지 않고 모델 스스로 어떤 도구를 언제 어떻게 쓸지 결정.
인간 주석 비용 문제뿐 아니라 "인간이 유용하다고 판단하는 것"과 "모델이 실제로 유용하다고 판단하는 것"이 다를 수 있기 때문에, 모델 자체의 신호를 기준으로 학습하는 것이 본질적으로 타당하다.
최근 Schick & Schütze(2021b), Honovich(2022), Wang(2022) 등은 LM의 in-context learning 능력을 활용해 데이터셋을 from-scratch로 생성하는 접근을 제안해왔다.
저자들은 이 아이디어를 도구 사용 학습에 확장 적용하여, 소수의 human-written 예시로부터 대규모 LM 데이터셋을 API 호출로 주석화하고, perplexity 감소 여부로 유용한 호출을 선별하는 self-supervised 루프를 설계한다.
사전학습 데이터와 동일한 데이터셋에 API 호출을 추가하므로 원본 언어 모델링 능력의 범용성이 보존된다는 이론적 이점이 있다.
TALM(Parisi 2022)이 유사한 self-supervised 목적을 사용하지만 제한된 도구와 태스크에 한정된 반면, Toolformer는 범용적 툴 사용 능력을 목표로 한다.

---

## Method

1. **문제 형식화**: API 호출을 튜플 c=(a_c, i_c)로 표현하며 a_c는 API 이름, i_c는 입력이다. 결과 r을 포함한 선형화된 시퀀스는 `e(c,r) = <API>a_c(i_c)→r</API>` 형태로 특수 토큰을 사용하여 텍스트에 삽입한다.
2. **Step 1 — Sampling API Calls**: 각 API에 대해 소수(~5개)의 데모가 포함된 프롬프트 P(x)를 작성하고, 입력 텍스트 x=x_1,...,x_n의 각 위치 i에서 `<API>` 토큰의 확률 p_i = p_M(`<API>` | P(x), x_{1:i-1})을 계산한다. 임계값 s를 초과하는 위치 I={i | p_i>s} 중 top-k=5만 유지하고, 각 위치에서 최대 m=5개 API 호출 후보 c_i^1,...,c_i^m을 샘플링한다.
3. **Step 2 — Executing API Calls**: 샘플링된 모든 API 호출을 실제로 실행하여 응답 r_i를 얻는다. 실행 방식은 API별로 다르며(별도 LM 호출, Python 스크립트 실행, BM25 검색 등), 응답은 단일 텍스트 시퀀스여야 한다.
4. **Step 3 — Filtering API Calls**: 가중 cross-entropy 손실 L_i(z) = -Σ_{j=i}^{n} w_{j-i} log p_M(x_j | z, x_{1:j-1})을 정의하고, L_i^+ = L_i(e(c_i, r_i))(API 호출+결과 제공)와 L_i^- = min(L_i(ε), L_i(e(c_i, ε)))(호출 없음 또는 결과 없음 중 최솟값)을 비교한다. L_i^- - L_i^+ ≥ τ(필터링 임계값)인 호출만 유지한다.
5. **가중 함수**: w_t = w̃_t / Σ_s w̃_s (여기서 w̃_t = max(0, 1-0.2t))를 사용하여 API 호출 직후 토큰에 더 큰 가중치를 부여, API가 정보를 제공해야 할 위치에 정렬되도록 한다.
6. **Step 4 — Finetuning**: 필터링된 API 호출 (c_i, r_i)를 원본 텍스트에 interleave 하여 x* = x_{1:i-1}, e(c_i, r_i), x_{i:n} 형태의 증강 데이터셋 C*를 생성한다. C*로 GPT-J(6.7B)를 표준 언어 모델링 목적 함수로 파인튜닝한다.
7. **Data-agnostic 설계**: C*는 API 호출이 삽입된 것을 제외하면 원본 C와 동일한 텍스트를 포함하므로 사전학습 데이터와 같은 데이터셋을 쓸 수 있고, 이는 LM의 범용성 유지를 보장한다.
8. **추론 시 디코딩**: Greedy decoding을 사용하되 `<API>` 토큰이 top-k=10에 포함되면 API 호출을 시작한다(k=1은 순수 greedy decoding과 동일). `→` 토큰이 생성되면 디코딩을 중단하고 API를 실행, 결과와 `</API>` 토큰을 삽입 후 디코딩을 재개한다.
9. **입력당 최대 1회 호출 제약**: 모델이 API 호출 루프에 빠지지 않도록 한 입력당 최대 1회의 API 호출만 허용한다.
10. **통합된 5개 도구**: (i) Question Answering — Atlas(Izacard 2022, Natural Questions fine-tuned), (ii) Calculator — Python 기반 사칙연산, (iii) Wikipedia Search — KILT Wikipedia dump 기반 BM25 retriever, (iv) Machine Translation — NLLB 600M(200 언어, fastText로 source language 자동 감지, target은 항상 English), (v) Calendar — 입력 없이 현재 날짜 반환.
11. **휴리스틱 데이터 필터링**: Calculator의 경우 문서에 숫자 3개 이상 + 수학 연산 결과 포함, 또는 "=", "equals", "equal to", "total of", "average of" 뒤 숫자가 오는 패턴을 매칭. Calendar는 URL에서 날짜 추출 가능한 ~18% 문서만 유지. MT는 비영어 chunk(10 토큰, fastText confidence > 0.8)가 영어 문맥에 둘러싸인 경우만 선별.
12. **하이퍼파라미터**: 기본 s=0.05, f=1.0, k=5, m=5. Calculator/MT는 데이터 희소성 때문에 s=0.0, k=20, m=10, f=0.5로 완화.

---

## Key Contribution

1. **최초의 self-supervised 범용 도구 사용 학습**: 인간 주석 없이 모델 자체의 loss 신호(L_i^- - L_i^+ ≥ τ)만으로 "언제/어떤/어떻게" 도구를 호출할지 학습하는 패러다임을 제시. 태스크별 프롬프트 없이도 zero-shot으로 작동한다.
2. **언어 모델링 범용성 보존**: 도구 사용 학습 후에도 WikiText/CCNet perplexity가 거의 동일하게 유지(Toolformer 16.03 vs GPT-J 15.88)되어, 기존 LM 능력을 희생하지 않고 도구 사용 능력만 추가한다.
3. **25배 작은 모델로 175B에 필적**: GPT-J(6.7B) 기반 Toolformer가 GPT-3(175B)를 LAMA/수학 벤치마크에서 상회하거나 필적하여, 도구 접근이 모델 스케일의 유효한 대안임을 실증한다.
4. **Emergent scaling behavior 발견**: 도구를 효과적으로 활용하는 능력은 약 775M 파라미터부터 emergent하게 나타나며, 그 이하 모델은 도구가 있어도 성능 이득이 없다.
5. **5개 이종 도구의 통합 프레임워크**: QA/Calculator/Wikipedia Search/MT/Calendar가 모두 같은 self-supervised 파이프라인으로 통합되어, "텍스트 입출력 가능 + 소수 데모" 조건만 만족하면 확장 가능한 일반화된 설계.
6. **Calibration 관찰**: k=1 greedy decoding에서 모델은 API 호출이 도움될 경우에만 호출하는 self-calibration을 보이며(NC 성능 > 평균 성능), 이는 fine-tuning이 모델의 자기-인식 수준 능력을 학습시켰음을 시사한다.

---

## Experiment

- **기반 모델**: GPT-J 6.7B. 베이스라인은 GPT-J(vanilla), GPT-J+CC(CCNet subset finetune, API 없음), Toolformer(API 포함), Toolformer disabled(파인튜닝됨, 디코딩 시 API 호출 차단), OPT 66B, GPT-3 175B(davinci, instruction-tuned 아님).
- **평가 세팅**: 모든 태스크에서 zero-shot prompted setup, in-context example 없음. Decoding은 k=10 greedy.
- **LAMA 결과 (SQuAD/Google-RE/T-REx)**: Toolformer 33.8/11.5/53.5 vs GPT-J 17.8/4.9/31.9, GPT-3 26.8/7.0/39.8 — baseline 대비 +11.7/+5.2/+18.6 개선, GPT-3(175B)도 상회. QA 도구를 98.1% 사례에서 호출.
- **수학 (ASDiv/SVAMP/MAWPS)**: Toolformer 40.4/29.4/44.0 vs GPT-J 7.5/5.2/9.9, GPT-3 14.0/10.0/19.8 — Toolformer가 GPT-3(175B)을 2배 이상 상회. Calculator 도구를 97.9% 호출.
- **QA (WebQS/NQ/TriviaQA)**: Toolformer 26.3/17.7/48.8 vs GPT-J 18.5/12.8/43.9, GPT-3 29.0/22.6/65.9 — 동일 크기 baseline 대비 개선했으나 GPT-3에는 부족. Wikipedia Search 99.3% 호출.
- **다국어 MLQA (Es/De/Hi/Vi/Zh/Ar)**: Toolformer 20.6/13.5/1.4/10.6/16.8/3.7 vs GPT-3 3.4/1.1/0.1/1.7/17.7/0.1 — GPT-3는 영어로 답하지 못해 대부분 언어에서 실패. MT 도구는 63.8~94.9%에서 사용(Hi는 7.3% 예외).
- **시간 데이터셋 (TempLAMA/DateSet)**: Toolformer 16.3/27.3 vs GPT-3 15.5/0.8 — DateSet에서 Calendar 도구 54.8% 사용이 큰 개선을 가져옴. TempLAMA는 Calendar 0.2%만 호출(대신 Wiki/QA 활용).
- **Perplexity (WikiText/CCNet)**: GPT-J 9.9/10.6, GPT-J+CC 10.3/10.5, Toolformer disabled 10.3/10.5 — C*로 학습해도 API disabled 시 perplexity 증가 없음.
- **Scaling laws**: GPT-2 124M/355M/775M/1.6B 및 GPT-J 6.7B에 적용 시, 도구 활용 능력은 약 775M부터 emergent. 작은 모델은 도구 사용/미사용 성능 차이가 거의 없음.
- **Decoding k 효과 (T-REx/WebQS)**: k=1 시 API 호출률 40.3%/8.5%, k=10 시 98.1%/100%. 성능은 T-REx 34.9→53.5, WebQS 18.9→26.3으로 상승.
- **Dataset 통계 (f=1.0 기준 샘플 수)**: QA 18,526, Wikipedia 60,974, Calculator 994, Calendar 20,587, MT 1,034 — API 호출 유용성 필터링 후 CCNet 대비 매우 희소함이 드러남.

---

## Limitation

저자 언급: Tool chaining(한 도구의 출력을 다른 도구의 입력으로 사용) 불가 — API 호출들이 독립적으로 샘플링되어 fine-tuning 데이터에 chained example이 없기 때문.
저자 언급: 대화형(interactive) 도구 사용 불가 — 검색 결과 browse나 쿼리 재작성 같은 WebGPT(Nakano 2021) 스타일 다단계 상호작용 미지원.
저자 언급: 입력 프롬프트 wording 민감도 — API 호출 여부가 프롬프트의 정확한 표현에 크게 좌우됨.
저자 언급: Sample inefficiency — 100만 개 이상 문서를 처리해도 Calculator 유용 호출은 수천 개에 불과. Iterative bootstrapping이 해결책일 수 있음.
저자 언급: API 호출 비용 미고려 — 현재 모델은 tool-dependent computational cost를 의사결정에 반영하지 않음.
독자 관점: 입력당 최대 1회 API 호출 제약은 복잡한 multi-hop reasoning(예: TempLAMA에서 "현재 날짜 조회 → 질문 재구성")을 원천적으로 차단함.
독자 관점: GPT-J 6.7B에서만 full evaluation을 수행하여 GPT-3/GPT-4 규모의 대형 모델에서 상대적 gain이 유지되는지 미검증.
독자 관점: 5개 고정 도구 세트로 실험되어, 실제 에이전트에 필요한 수십~수백 개 API 생태계로의 확장성은 검증되지 않았고 새 도구 추가 시 전체 데이터셋 재생성이 필요함.
