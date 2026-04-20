# MIRIX: Multi-Agent Memory System for LLM-Based Agents

> **논문 정보**: Yu Wang, Xi Chen (MIRIX AI)
> **arXiv**: 2507.07957v1 (2025.07.10) | **학회**: -
> **코드**: https://mirix.io/

---

## Problem

대부분의 LLM 기반 개인 비서는 현재 프롬프트 윈도우를 넘어서는 상태를 유지하지 못하며, 맥락이 명시적으로 재공급되지 않는 한 지속적인 메모리를 보유하지 않는다.

이 stateless 특성은 사용자가 시간이 지남에 따라 진화하고 개인화되는 비서를 기대하는 실세계 환경에서 장기적 사용성을 심각하게 저해한다.

기존 메모리 보강 시스템의 첫 번째 근본적 한계는 구성적 메모리 구조의 부재이다. 대부분이 단일 평탄(flat) 저장소에 모든 이력 데이터를 저장하여 전문화된 메모리 유형(절차적, 에피소드적, 의미적)으로의 라우팅이 없어 검색이 비효율적이고 부정확하다.

두 번째 한계는 멀티모달 지원 부족이다. 텍스트 중심 메모리 메커니즘은 이미지, 인터페이스 레이아웃, 지도 등 대다수 실세계 입력이 비언어적인 경우를 처리하지 못한다.

세 번째 한계는 확장성과 추상화의 결여이다. 원시 입력(특히 이미지)을 그대로 저장하면 금지적 수준의 메모리 요구량이 발생하며, 핵심 정보만 요약하여 보존하는 추상화 계층이 없다.

특히 ScreenshotVQA와 같이 사용자 1명당 5,000~20,000장의 고해상도 스크린샷을 처리해야 하는 환경에서는, 기존 long-context 모델조차 해상도를 256×256으로 축소해야 간신히 3,600장만 컨텍스트에 수용할 수 있다는 본질적 한계가 드러난다.

또한 지식 그래프 기반 접근(Zep, Cognee)은 구조적 관계 표현에는 강하나 순차적 사건·감정 상태·전체 문서·멀티모달 입력을 모델링하지 못하는 편향을 가진다.

---

## Motivation

인간 인지는 대화 회상, 패턴 인식, 과거 경험 기반 행동 적응 등 메모리에 크게 의존하며, LLM 에이전트도 일관되고 개인화된 상호작용·피드백 학습·반복 질의 회피를 위해 동등한 메모리 메커니즘이 필수적이다.

저자들은 Routing(라우팅)과 Retrieving(검색)이 메모리 보강 에이전트가 갖춰야 할 두 가지 핵심 역량이라 주장한다. 현재 시스템 대부분은 Short-Term/Long-Term 이분법(Letta, Cognitive Memory), 기껏해야 Mid-Term을 포함하는 Memory OS 수준에 머물러 라우팅 세분도가 낮다.

이에 반해 인지과학은 단기 메모리와 장기 메모리를 구분하고, 장기 메모리 내에서도 에피소드(episodic), 의미(semantic), 절차(procedural) 메모리를 세분화한다 — 이 분류는 real-world reasoning과 추상화에 중요한 것으로 알려져 있다.

저자들은 기존 연구들이 개별 메모리 유형의 중요성을 지적했음에도(A-Mem의 episodic, Tulving의 semantic, Wheeler & Jeunen의 procedural), 이들을 포괄적 통합 시스템으로 구성한 사례가 없다는 공백을 발견한다.

또한 Mem0와 MemGPT에서 볼 수 있듯 명시적 "memory search" 트리거가 없으면 모델이 자신의 파라메트릭 지식(예: "Twitter CEO는 Elon Musk")을 기본값으로 회귀하는 문제가 있으며, 매번 사용자가 "search your memory"를 명시하는 것은 자연 대화에서 실용적이지 않다.

마지막으로 스마트 글래스·AI pin 같은 웨어러블 디바이스와 미래의 메모리 마켓플레이스 시나리오에서는 멀티모달·지속·개인화 메모리가 핵심 차별점이 되므로, 저자들은 이를 위한 기반 인프라가 필요하다고 본다.

---

## Method

1. **6종 메모리 컴포넌트 설계**: Core Memory(항상 에이전트에 노출되는 고우선 지속 정보 — persona/human 블록, MemGPT 영감), Episodic Memory(타임스탬프 기반 사건·경험 로그, event_type/summary/details 필드), Semantic Memory(시간 독립적 추상 지식·엔티티, name/summary/details/source 필드), Procedural Memory(목표 지향 워크플로·가이드·스크립트, entry_type/description/steps 필드), Resource Memory(문서·전사본·멀티모달 파일, title/summary/resource_type/content 필드), Knowledge Vault(자격증명·주소·API 키 등 민감 verbatim 정보, entry_type/source/sensitivity/secret_value 필드).

2. **계층적 내부 구조**: 각 메모리 컴포넌트는 내부적으로 계층형으로 조직된다. Semantic Memory는 예컨대 "Social Network", "Favorites" 같은 상위 카테고리 아래 "Sports", "Pets", "Music" 하위 클래스로 트리 구조를 이루며, Knowledge Vault의 high sensitivity 엔트리는 access control로 보호되어 일반 검색에서 제외된다.

3. **Multi-Agent Architecture (8 agents)**: 6개 Memory Manager(각 메모리 컴포넌트 1:1 전담) + 1개 Meta Memory Manager(태스크 라우팅) + 1개 Chat Agent(대화 인터페이스)로 구성된 멀티에이전트 프레임워크가 동적으로 업데이트·검색을 조율한다.

4. **Memory Update Workflow**: 사용자 입력 수신 → 메모리 베이스 자동 검색 → 검색 결과+입력을 Meta Memory Manager로 전달 → 관련 Memory Manager들에 라우팅 → 각 Memory Manager가 병렬로 해당 메모리 업데이트(중복 방지 내장) → Meta Memory Manager에 완료 보고 → 최종 ack 전송.

5. **Conversational Retrieval Workflow**: Chat Agent가 사용자 쿼리 수신 → 6개 컴포넌트 전역에 걸친 coarse retrieval로 high-level summary 획득 → 쿼리 분석하여 타겟 컴포넌트·검색 방법 선택 → 세부 검색 실행 → 정보 통합 후 응답 합성. 쿼리가 메모리 수정 의도를 포함하면 해당 Memory Manager와 직접 교신하여 정밀 업데이트 수행.

6. **Active Retrieval 메커니즘 (2단계)**: (1단계) 에이전트가 입력 컨텍스트로부터 current topic을 명시적으로 생성, (2단계) 해당 topic으로 6개 메모리 컴포넌트 각각에서 top-10 관련 항목 검색. 검색 결과는 `<episodic_memory>...</episodic_memory>`와 같은 소스 태그로 감싸 시스템 프롬프트에 주입되어, 모델이 내용과 출처를 동시에 인지하도록 한다.

7. **다중 검색 함수 지원**: embedding_match, bm25_match, string_match 세 가지 기본 검색 전략을 제공하며, 각 방법이 차별화되어 있어 에이전트가 맥락에 따라 최적 방법을 자율 선택한다. 저자들은 향후 더 다양한 특화 검색 전략을 확장할 계획임을 명시한다.

8. **스크린샷 스트리밍 캡처 파이프라인**: 매 1.5초 간격으로 스크린샷 캡처, 시각적 유사도 >0.99인 이미지는 폐기, 20장의 고유 스크린샷 수집 시 메모리 업데이트 트리거(약 60초 주기). 배치로 20장을 한번에 보내는 대신 수신 즉시 스트리밍 업로드하여 지연을 최소화한다.

9. **Core Memory 용량 관리**: 메모리 크기가 용량의 90%에 도달하면 제어된 rewrite 프로세스를 자동 트리거하여 핵심 정보 손실 없이 컴팩트함을 유지한다.

10. **하이브리드 on-device/cloud 스토리지**: Knowledge Vault의 민감 정보는 로컬 저장하고 Resource Memory 같은 대용량 메모리는 클라우드에 오프로드하여 웨어러블 하드웨어 제약(제한된 컴퓨팅·스토리지)에 대응하는 설계를 제안한다.

11. **애플리케이션 구현**: React-Electron 프론트엔드 + Uvicorn 백엔드 서버로 구성된 크로스 플랫폼 개인 비서 앱을 제공. SQLite를 스토리지 백엔드로 채택하며, ScreenShots 탭 활성화로 실시간 스크린 모니터링·메모리 구축을 시작할 수 있다.

---

## Key Contribution

1. **최초의 포괄적 모듈형 메모리 시스템**: 기존 메모리 아키텍처의 3대 한계(구성 부재·멀티모달 미지원·확장성/추상화 부재)를 체계적으로 분석하고, 6종 전문화된 메모리 컴포넌트 + 8개 에이전트로 구성된 MIRIX를 제안.

2. **Active Retrieval 메커니즘**: 사용자의 명시적 memory search 요청 없이 에이전트가 topic을 생성하고 6개 컴포넌트에서 자동으로 관련 메모리를 검색·주입. parametric knowledge 회귀 문제를 해결.

3. **ScreenshotVQA 벤치마크 신설**: 3명의 PhD 학생이 한 달간 수집한 약 20,000장 고해상도 스크린샷과 87개 검증 질문으로 구성된, 기존 메모리 시스템이 적용 불가능한 멀티모달 실사용 벤치마크 공개.

4. **LOCOMO SOTA 달성**: LOCOMO 벤치마크에서 85.38%의 전체 SOTA 성능 달성, 기존 최강 오픈소스 경쟁자(LangMem) 대비 8.0%p 향상하고 Full-Context 상한선(87.52%)과의 격차를 2.14%p까지 좁힘.

5. **크로스 플랫폼 앱 공개**: React-Electron 기반 설치형 개인 비서 애플리케이션 — 실시간 스크린 모니터링, 메모리 업데이트 시각화(트리/리스트 뷰), 안전한 로컬 SQLite 저장을 통합 제공.

6. **장래 비전 제시**: 웨어러블 AI(Meta Ray-Ban, Humane, Rabbit R1)·Agent Memory Marketplace 같은 신흥 시장에서 MIRIX의 모듈형 메모리가 어떻게 infrastructure로 기능할지에 대한 구체적 유스케이스 제시(개인 AI 동반자, 전문가 커뮤니티, Fan Economy 등).

---

## Experiment

**ScreenshotVQA 설정**: 3명 PhD 학생(CS/Physics 전공)이 초당 1회 스크린샷 캡처(유사도 0.99 이상이면 스킵)하여 각각 5,886장(1일)·18,178장(20일)·5,349장(43일)의 이미지 수집. 질문 수는 각 11개/21개/55개로 총 87개. 평가는 GPT-4.1을 judge로 LLM-as-a-Judge 방식. 백본은 gemini-2.5-flash-preview-04-17.

**ScreenshotVQA 결과**: MIRIX 전체 정확도 **59.50%** (Student1 54.55%, Student2 56.67%, Student3 67.27%) vs SigLIP@50 44.10% vs Gemini 11.66%.

**저장 공간 비교**: MIRIX **15.89MB** SQLite vs SigLIP 15.07GB 원본 2K–4K 이미지 vs Gemini 236.70MB(256×256 리사이즈).

**효율 지표**: RAG 베이스라인(SigLIP) 대비 **정확도 35% 향상** + **저장 공간 99.9% 절감**. Long-context 베이스라인(Gemini) 대비 **정확도 410% 향상** + **저장 공간 93.3% 절감**.

**LOCOMO 설정**: 10개 대화(평균 600 dialogue, 26k 토큰/대화), 대화당 평균 200 질문. 카테고리는 single-hop, multi-hop, open-domain, temporal(adversarial은 Mem0 선행연구 따라 제외). 백본은 gpt-4.1-mini(Berkeley Function Calling Benchmark에서 gpt-4o-mini 22.12% vs gpt-4.1-mini 29.75%로 function calling 우위). MIRIX와 Full-Context는 3회 평균, 나머지 베이스라인은 1회 실행.

**LOCOMO 전체 결과**: MIRIX **85.38%** (Single-Hop 85.11%, Multi-Hop 83.70%, Open-Domain 65.62%, Temporal 88.39%) — 전체 SOTA.

**gpt-4.1-mini 베이스라인 비교**: LangMem 78.05%(+7.33%p), Zep 79.09%(+6.29%p), Mem0 62.47%(+22.91%p), RAG-500 51.62%(+33.76%p). gpt-4o-mini 백본 기준 A-Mem 48.38%, OpenAI 52.90%, Memobase 70.91%, Zep 75.14%와의 차이는 10%p 이상.

**카테고리별 격차**: Multi-Hop에서 MIRIX 83.70% vs Zep 69.16%로 **+14.54%p** 격차가 가장 큼 — 통합된 event 저장("Caroline moved from her hometown, Sweden, 4 years ago")이 분산 정보를 query-time에 stitching할 필요를 제거.

**Full-Context 상한선 접근**: Full-Context 87.52%, MIRIX 85.38%로 격차 **2.14%p** — Mem0 선행연구에서 지적한 대로 평균 9k 토큰 규모에서는 Full-Context가 본질적 upper-bound이므로, 거의 상한까지 회복한 셈.

---

## Limitation

Open-Domain 질문에서 상대적 약세가 존재한다 — MIRIX의 Open-Domain 정확도(65.62%)는 Full-Context(71.88%) 대비 6.26%p 낮으며, 이는 "what if" 형태의 질문이 longer terms에 걸친 global understanding을 요구하지만 RAG 기반 검색이 본질적으로 global view를 제공하지 못하기 때문이다.

Single-Hop 질문의 모호성 취약점이 있다 — 계획된 날짜 vs 실제 발생 날짜가 섞인 경우(예: Melanie가 5월에 "다음달 캠핑 갈 계획"이라 말한 뒤 10월에 가족과 실제 캠핑) MIRIX가 consolidated event("19 October 2023, Melanie family went camping")를 우선시하여 "계획 날짜"를 묻는 원래 의도와 불일치하는 응답을 생성한다.

평가 규모가 제한적이다 — ScreenshotVQA 벤치마크는 단 3명 사용자와 총 87개 질문으로 구성되어 통계적 일반화와 다양성 측면에서 한계가 있다.

모델 function calling 능력에 강하게 의존한다 — 멀티에이전트 구조상 Meta Memory Manager에 1회 + 6개 Memory Manager에 0~6회의 function call이 단일 업데이트 step마다 발생하므로, function calling이 약한 gpt-4o-mini 같은 모델에서는 성능 저하가 불가피하다.

강력한 폐쇄형 모델 의존성이 있다 — Latent-space memory 계열과 달리 모델 재훈련은 불필요하나, 반대로 GPT-4.1/Gemini 2.5 같은 고성능 클로즈드 모델에 의존하므로 오픈소스 환경에서의 재현성과 비용 효율성이 제한적이다.

Non-reasoning 모델로의 편향된 평가 설계 — 저자들이 명시하듯 multi-hop에서 MIRIX의 우위는 gpt-4.1-mini 같은 non-reasoning 모델이 partial information을 query-time에 통합하지 못하는 약점에서 기인하며, OpenAI-o3 같은 reasoning 모델에서는 이 격차가 축소될 가능성이 있어 MIRIX의 구조적 이점이 모델 능력 향상에 따라 희석될 위험이 있다.

SQLite 단일 백엔드와 concurrent write 가능성에 대한 논의가 부재하며, 대규모 사용자 동시 운용이나 분산 스토리지 통합에 대한 엔지니어링 검증이 이 논문 범위 밖에 있다.

향후 더 도전적인 실세계 벤치마크와 on-device/cloud 하이브리드 메모리 관리의 구체적 실험 검증이 명시적 future work로 제시되어, 현 시점의 real-world 배포 준비도는 제한적이다.
