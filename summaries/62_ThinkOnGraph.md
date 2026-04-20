# Think-on-Graph: Deep and Responsible Reasoning of LLM on Knowledge Graph

> **논문 정보**: Jiashuo Sun, Chengjin Xu, Lumingyuan Tang, Saizhuo Wang, Chen Lin, Yeyun Gong, Lionel M. Ni, Heung-Yeung Shum, Jian Guo (IDEA Research, Xiamen Univ., USC, HKUST, HKUST-Guangzhou, Microsoft Research Asia)
> **arXiv**: 2307.07697 (2023.07, v6 2024.03)
> **학회**: ICLR 2024
> **코드**: https://github.com/IDEA-FinAI/ToG

---

## Problem

LLM은 사전학습 시점 이후의 최신 지식이나 도메인 특화 전문 지식을 요구하는 질문에서 잦은 환각(hallucination)을 일으킨다.
특히 다중 홉(multi-hop) 추론이 필요한 복잡한 지식 집약적 태스크에서 긴 논리 체인을 유지하지 못해 중간 사실을 잘못 생성한다.
LLM의 추론은 블랙박스이기 때문에 책임성(responsibility), 설명 가능성(explainability), 투명성(transparency)이 부족하다.
LLM 재학습은 비용이 막대하고 시간이 오래 걸려, 지식을 최신 상태로 유지하기 어렵다.
기존 LLM⊕KG 패러다임(예: SPARQL 자동 생성 기반 KBQA)은 LLM이 번역기 역할만 수행하고 KG 탐색에는 직접 참여하지 않아, KG가 불완전한 경우(예: "majority party" 관계 누락)에는 즉시 실패한다.
이러한 느슨한 결합(loose-coupling) 방식은 성공 여부가 KG의 완결성·품질에 과도하게 의존한다.

---

## Motivation

LLM과 KG를 서로의 약점을 보완하도록 **긴밀하게 결합(tight-coupling)** 하는 새로운 패러다임이 필요하다.
KG는 구조화되고 명시적이며 편집 가능한 지식 표현을 제공하여 LLM의 파라미터 지식을 업데이트 없이 확장할 수 있다.
한편 LLM은 KG의 빈 공간(missing relations)을 내재적 지식(inherent knowledge)으로 채울 수 있다.
따라서 LLM을 KG 위에서 능동적으로 탐색하는 에이전트로 위치시키면, 매 추론 단계마다 KG의 구조 정보와 LLM의 언어·상식 추론 능력을 상호 보완적으로 활용할 수 있다.
Figure 1c의 예시처럼, Canberra→Australia→Anthony Albanese→Labor Party 경로는 KG에 "majority party" 관계가 없어도 "prime minister" 관계와 LLM의 정치인 소속 지식으로 정답에 도달할 수 있다.
탐색 경로를 명시적 트리플 체인으로 유지하면 추적성(traceability)과 수정 가능성(correctability)도 함께 확보된다.

---

## Method

### 1. LLM⊗KG 패러다임 정의
기존 LLM⊕KG가 KG를 정적 참조 소스로 사용하는 반면, LLM⊗KG는 LLM을 KG 위의 능동적 탐색 에이전트로 활용한다. 매 단계에서 어떤 관계·엔티티를 확장할지 LLM이 스스로 판단한다.

### 2. 전체 알고리즘 구조 (3 Phase)
Think-on-Graph(ToG)는 LLM에게 KG 위에서 빔 서치(beam search)를 수행하게 하는 프레임워크이다. 너비 N, 최대 깊이 D_max의 상위 N개 추론 경로 P={p₁,...,pN}를 반복적으로 갱신하며, 총 **Initialization → Exploration → Reasoning** 3단계로 구성된다.

### 3. Initialization (그래프 탐색 초기화)
질문 x가 주어지면 LLM이 topic entity를 자동 추출하여 상위 N개 초기 엔티티 집합 E⁰={e⁰₁,...,e⁰N}을 구성한다. N보다 적을 수도 있으며, 이것이 각 추론 경로의 출발점이 된다.

### 4. Exploration – Relation Exploration (Search)
D번째 반복의 시작에서, 현재 꼬리 엔티티 e^(D-1)_n에 연결된 인·아웃바운드 관계를 KG에서 조회하여 후보 관계 집합 R^D_cand를 생성한다. 조회는 사전 정의된 단순 formal query(Appendix E.1, E.2)로 수행되어 다양한 KG에 학습 없이 적용 가능하다.

### 5. Exploration – Relation Exploration (Prune)
LLM이 질문 x와 후보 관계 R^D_cand의 자연어 표현을 보고 상위 N개 관계를 선택하여 새 경로 P_ending을 형성한다. 예: Canberra에서 {capital of, country, territory} 선택.

### 6. Exploration – Entity Exploration (Search)
선택된 관계 r^D_n에 대해 (e^(D-1)_n, r^D_n, ?) 또는 (?, r^D_n, e^(D-1)_n) 쿼리로 후보 꼬리 엔티티 집합 E^D_cand,n을 수집하고 전체 P_cand로 확장한다.

### 7. Exploration – Entity Exploration (Prune)
자연어로 표현된 후보 엔티티들에 대해 LLM이 상위 N개를 선택한다. 관계별 후보가 유일하면 자동으로 1점 스코어를 할당한다. 이로써 경로가 한 홉 확장된다.

### 8. Reasoning (평가 및 답 생성)
확장된 경로 P에 대해 LLM이 "현재 정보로 답할 수 있는가"를 판정한다. 긍정이면 답을 생성하고, 부정이면 Exploration을 한 번 더 반복한다. 최대 깊이 D_max 도달 시까지 충분한 경로를 얻지 못하면 LLM 내재 지식만으로 답한다.

### 9. ToG-R (Relation-based 변형)
triple 기반 경로 대신 관계 체인 (e⁰_n, r¹_n, ..., r^D_n)을 유지한다. entity prune 단계에서 LLM 호출을 제거하고 **random beam search**를 사용한다. 가정: 같은 관계로 얻은 후보 엔티티들은 대체로 동일 클래스에 속해 이후 관계 탐색에 미치는 영향이 작다.

### 10. LLM 호출 비용
ToG: 최대 **2ND+D+1** 회의 LLM 호출. ToG-R: **ND+D+1** 회로 약 절반. BM25/SentenceBERT로 prune 시에는 D+1 회까지 축소 가능.

### 11. 프롬프트 표현 형식
추론 경로를 (1) Triple 포맷 "(Canberra, capital of, Australia)", (2) Sequence 포맷, (3) Sentence 포맷(자연어 문장 변환) 중 선택 가능. ToG는 Triple, ToG-R은 Sequence가 기본값.

### 12. 지식 추적·수정 루프
모든 추론 경로를 명시적 트리플 체인으로 저장한다. 오답 시 사용자/전문가/다른 LLM이 경로를 역추적해 오류 트리플(예: 구식 스타디움 이름)을 찾고, LLM에게 수정된 triple로 재추론을 시킨다. 이를 통해 LLM+KG 양방향 개선(knowledge infusion) 루프를 형성한다.

### 13. 하이퍼파라미터·플러그앤플레이
기본값 N=3, D_max=3. 추가 학습 없이 ChatGPT, GPT-4, Llama-2-70B와 Freebase, Wikidata 조합 어디든 교체 가능.

---

## Key Contribution

1. **LLM⊗KG 패러다임 제안**: LLM을 KG 위에서 빔 서치하는 능동적 에이전트로 통합하는 tight-coupling 프레임워크 최초 정립.
2. **Deep Reasoning 성능**: 추가 학습 없는 prompting만으로 9개 데이터셋 중 **6개에서 전체 SOTA** 달성(대부분 기존 SOTA가 fine-tuning 기반).
3. **Responsible Reasoning**: 명시적·편집 가능한 추론 경로로 설명성 확보 및 knowledge traceability/correctability 실현.
4. **비용 효율성**: Llama-2-70B + ToG가 GPT-4 단독(CoT)을 여러 데이터셋에서 초과 → 작은 모델 + KG 조합이 대형 모델 대체 가능성을 실증.
5. **플러그앤플레이**: 학습 비용 0, LLM·KG·프롬프트 전략을 자유롭게 교체 가능한 범용 프레임워크.
6. **ToG-R 변형**: 비용 절반으로 유사 성능 달성하는 관계 중심 변형 제시.

---

## Experiment

### 실험 설정
- **KG**: Freebase (CWQ, WebQSP, GrailQA, Simple Questions, WebQuestions), Wikidata (QALD10-en, T-REx, Zero-Shot RE, Creak)
- **LLM 백본**: ChatGPT(GPT-3.5-turbo), GPT-4, Llama-2-70B-Chat (8×A100-40G, no quantization)
- **하이퍼파라미터**: N=3, D_max=3, temperature 0.4(exploration)/0(reasoning), max token 256, 5-shot
- **데이터셋**: Multi-hop KBQA 4종 + Single-hop 1종 + Open QA 1종 + Slot Filling 2종 + Fact Checking 1종 = 총 9개
- **평가 지표**: Hits@1 (exact match accuracy)

### 주요 결과 (Table 1)
- **GrailQA**: ToG(GPT-4) **81.4** vs Prior Prompting SOTA 53.2 vs CoT(ChatGPT) 28.1 → +53.3%p
- **Zero-Shot RE**: ToG(GPT-4) **88.3** vs CoT(ChatGPT) 28.8 → +59.5%p
- **WebQSP**: ToG(GPT-4) **82.6** vs Prior FT SOTA(DeCAF) 82.1 → 학습 없이 FT 초과
- **QALD10-en**: ToG(GPT-4) **53.8** vs Prior FT SOTA 45.4 → +8.4%p
- **Simple Questions**: ToG(GPT-4) 66.7 vs Prior FT SOTA 85.8 → single-hop에서는 열세
- **CWQ**: ToG(GPT-4) 69.5 vs Prior FT SOTA 70.4 → 0.9%p 차이로 근접
- **Creak**: ToG(GPT-4) **95.6** vs Prior FT SOTA 88.2

### 백본 모델별 비교 (Table 2, CWQ / WebQSP)
- Llama-2-70B: CoT 39.1/57.4 → ToG 53.6/63.7 (Gain +18.5/+11.5)
- ChatGPT: CoT 38.8/62.2 → ToG 58.9/76.2 (Gain +20.1/+14.0)
- GPT-4: CoT 46.0/67.3 → ToG 69.5/82.6 (Gain +23.5/+15.3)
- 모델이 강할수록 KG 활용 이점이 커짐 → 강한 LLM일수록 KG 잠재력 더 많이 추출
- Llama-2-70B + ToG (CWQ 53.6) > GPT-4 + CoT (46.0) → 소형 모델 + KG가 대형 모델 대체

### Ablation: KG 종류 (Table 3)
- ToG w/Freebase: CWQ 58.8, WebQSP 76.2
- ToG w/Wikidata: CWQ 54.9, WebQSP 68.6 (데이터셋이 Freebase로 구축되어 있어 Wikidata는 열세, 대규모 KG의 가지치기 난도 상승)

### Ablation: 프롬프트 포맷 (Table 4)
- ToG Triples 58.8/76.2 > Sequences 57.2/73.2 ≈ Sentences 58.6/73.0
- ToG-R Sentences는 67.3으로 대폭 하락 → 관계 체인을 자연어로 변환하면 프롬프트가 길어져 성능 저하

### Ablation: Prune 도구 (Table 5)
- ToG w/ChatGPT 58.8/76.2 > SentenceBERT 51.7/66.3 > BM25 51.4/58.7
- LLM 프루닝이 CWQ에서 평균 +8.4%p, WebQSP에서 평균 +15.1%p 우위
- 다만 lightweight prune 사용 시 LLM 호출은 D+1로 급감하여 효율성 이점

### 깊이·너비 분석 (Figure 3)
- D, N을 1→4로 증가시킬수록 성능 향상하나 D=3 이후 포화
- 비용은 깊이에 선형 증가 → 기본값 N=D=3 채택이 정확도·비용 균형점

### 지식 추적·수정 사례 (Figure 4)
- "Phillie Phanatic 팀의 spring training stadium" 질문에서 초기 오답 "Bright House Field" 출력 → ToG가 (Philadelphia Phillies, Arena Stadium, Bright House Field) 트리플이 구식 명칭임을 역추적으로 발견 → 사용자가 수정 후 정답 재생성

---

## Limitation

KG 규모가 커질수록 탐색·가지치기 비용이 증가하며, 특히 대규모 KG(Wikidata)에서는 후보 집합이 방대해 LLM 프루닝 난도가 크게 상승한다.
빔 너비 N과 깊이 D_max를 메모리·비용 제약 때문에 각 3으로 제한해, 3홉 이상의 복잡한 다중 홉 문제에서 최적 경로를 놓칠 수 있다.
최악 경우 2ND+D+1회의 LLM 호출이 필요해 실시간 응답이 어려운 시나리오에서는 비용이 부담된다.
Single-hop 데이터셋(Simple Questions 66.7 vs FT SOTA 85.8)에서는 FT 기반 방법 대비 열세 — 단순 질의에서는 구조적 탐색 이점이 작다.
ToG-R은 비용을 절반으로 줄이지만 엔티티 리터럴 정보를 활용하지 않아 triple 기반 ToG 대비 대부분 벤치마크에서 성능이 낮다.
KG 자체의 품질과 최신성이 여전히 병목이며, traceability/correctability 루프는 사람/외부 검증자의 개입을 요구한다.
성능이 backbone LLM의 능력에 크게 의존(Llama-2 Gain +18.5 vs GPT-4 Gain +23.5)하여, 작은 오픈소스 모델만 쓰는 환경에서는 효용이 축소된다.
탐색 전략이 heuristic beam search이므로 RL/학습 기반 경로 선택과의 비교 및 조합은 미탐색으로 남는다.
