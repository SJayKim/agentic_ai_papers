# MIRIX: Multi-Agent Memory System for LLM-Based Agents

> **논문 정보**
> - 저자: Yu Wang, Xi Chen (MIRIX AI)
> - arXiv: 2507.07957v1 (2025년 7월 10일)
> - 소속: UCSD, NYU Stern

---

## 필수 요소

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 기반 에이전트는 현재 프롬프트 창을 벗어나면 정보를 유지하지 못해 사실상 stateless 상태이다. 기존 메모리 시스템은 (1) 단일 flat 저장소에 모든 정보를 쌓아 라우팅 및 검색 효율이 낮고, (2) 이미지 등 비텍스트 멀티모달 입력을 처리하지 못하며, (3) 원본 입력(특히 이미지)을 그대로 저장해 스토리지가 폭증하고 효과적인 추상화 레이어가 없다. |
| **Motivation** | 수만 장의 고해상도 스크린샷(한 달치, 최대 18,178장)을 다루는 실세계 시나리오에서 기존 Letta, Mem0, Zep 등은 멀티모달 입력 자체를 처리할 수 없다. Gemini 장문맥 모델로 3,600장을 256×256으로 리사이즈해 밀어 넣어도 ScreenshotVQA 정확도가 0~25% 수준에 그친다. 텍스트 전용 벤치마크 LOCOMO에서도 최강 기존 방법(Zep)이 79.09%로 Full-Context 상한(87.52%)에 크게 못 미친다. 인간의 인지는 에피소딕·의미·절차·핵심·자원 기억 등으로 분화되어 있어 단일 flat 메모리로는 이 다양성을 표현할 수 없다. |
| **Method** | **6종 메모리 컴포넌트 + 8-에이전트 멀티에이전트 아키텍처** <br><br> **메모리 컴포넌트** <br>- **Core Memory**: 사용자 이름·선호도 등 항상 활성화되는 고우선순위 정보. 90% 초과 시 자동 rewrite. MemGPT의 persona/human 블록에서 영감. <br>- **Episodic Memory**: 타임스탬프가 붙은 사용자 행동·경험 이벤트. summary + details 계층 구조. <br>- **Semantic Memory**: 개념·엔티티·사회 그래프 등 시간 독립적 지식. name / summary / details / source 필드. 트리 구조로 시각화 가능. <br>- **Procedural Memory**: 단계별 How-to 절차·워크플로. entry_type (workflow/guide/script) + steps 필드. <br>- **Resource Memory**: 사용자가 다루는 문서·파일·멀티미디어. title / summary / resource_type / content 필드. <br>- **Knowledge Vault**: 자격증명·주소·API 키 등 민감 정보를 verbatim 보존. 민감도(low/medium/high)에 따른 접근 제어. <br><br> **에이전트 구성** <br>- Meta Memory Manager 1개: 입력 분석 후 해당 Memory Manager로 라우팅 <br>- Memory Manager 6개: 각 컴포넌트를 병렬로 업데이트 <br>- Chat Agent 1개: 사용자와 자연어 대화 <br><br> **Active Retrieval** <br>쿼리가 들어오면 (1) 에이전트가 먼저 현재 토픽을 생성하고 (2) 이 토픽으로 6개 컴포넌트 전체에서 Top-10 항목을 자동 검색해 시스템 프롬프트에 주입. embedding_match / bm25_match / string_match 등 복수의 검색 함수 지원. <br><br> **애플리케이션** <br>1.5초마다 스크린샷 캡처 → 유사도 0.99 이상이면 폐기 → 20장 누적 시 메모리 업데이트 (약 60초 주기). Gemini API + Google Cloud URL 스트리밍 업로드로 지연시간 50초 → 5초 이하로 단축. SQLite DB로 압축 저장. |
| **Key Contribution** | 1. **6종 특화 메모리 + 8-에이전트 프레임워크**: 기존 시스템들이 단일·이중 메모리 타입에 그친 반면, 에피소딕/의미/절차/핵심/자원/금고 6종을 완전한 시스템으로 통합. <br>2. **멀티모달 실세계 메모리**: 기존 어떤 메모리 시스템도 처리하지 못한 대량 고해상도 스크린샷 시퀀스(최대 18,178장/월)를 추상·압축·저장. <br>3. **ScreenshotVQA 벤치마크 신규 도입**: 3명 PhD 학생의 실제 컴퓨터 활동 스크린샷 기반, 87개 질문의 멀티모달 메모리 벤치마크. <br>4. **Active Retrieval 메커니즘**: 사용자가 명시적으로 검색을 요청하지 않아도 에이전트가 자동으로 토픽을 추론해 메모리를 조회. <br>5. **LOCOMO SOTA**: 기존 최강 방법(Zep 79.09%) 대비 +8.0%p 향상, Full-Context 상한(87.52%)에 근접. |
| **Experiment/Results** | **ScreenshotVQA** (멀티모달 벤치마크, LLM-as-a-Judge, 평가 모델: GPT-4.1) <br>- 백본: gemini-2.5-flash-preview-04-17 <br>- Gemini (장문맥, 256×256 리사이즈): 정확도 11.66%, 스토리지 236.70 MB <br>- SigLIP@50 (RAG 기반): 정확도 44.10%, 스토리지 15.07 GB <br>- **MIRIX**: 정확도 **59.50%**, 스토리지 **15.89 MB** <br> → SigLIP 대비 +35%p 정확도, 스토리지 99.9% 감소 <br> → Gemini 대비 +410% 정확도, 스토리지 93.3% 감소 <br><br> **LOCOMO** (장문 대화 벤치마크, LLM-as-a-Judge, 백본: gpt-4.1-mini) <br>- RAG-500: 51.62% <br>- Mem0: 62.47% <br>- LangMem: 78.05% (gpt-4.1-mini 기준 재구현) <br>- Zep: 79.09% <br>- **MIRIX: 85.38%** (3회 평균: 83.98 / 87.34 / 84.82) <br>- Full-Context (상한): 87.52% <br><br> 세부 카테고리별 MIRIX 성능 (LOCOMO): <br>- Single-Hop: 85.11% (Full-Context 88.53%에 근접) <br>- Multi-Hop: 83.70% (**+24%p 이상**으로 가장 큰 개선) <br>- Open-Domain: 65.62% <br>- Temporal: 88.39% |
| **Limitation** | 1. **저자가 인정한 한계** <br> - Open-Domain 질문에서 Full-Context 대비 성능 갭이 존재: MIRIX도 RAG 방식에 의존하므로 전역적 이해가 부족하다. <br> - Single-Hop 일부에서 모호한 질문(계획 날짜 vs. 실제 발생 날짜)에 대해 MIRIX가 "확정된 사건"을 우선시해 오답을 내는 경우가 있다. <br> - 현재 ScreenshotVQA는 3명의 PhD 학생으로부터 수집된 87개 질문으로 소규모이다. 저자도 더 도전적인 실세계 벤치마크 구축을 미래 작업으로 남겼다. <br>2. **읽으면서 느낀 한계** <br> - Ablation Study 부재: 6개 컴포넌트 각각의 기여도나 Active Retrieval의 효과를 개별 제거 실험으로 검증하지 않았다. <br> - LOCOMO는 평균 9k 토큰(26k 기준)으로 단일 세션이 비교적 짧아, 진정한 장기 기억의 한계가 드러나지 않을 수 있다. <br> - 비용·속도 분석 부재: 8개 에이전트 병렬 호출로 인한 API 비용 및 지연시간에 대한 정량적 분석이 없다. <br> - 개인정보 보호: Knowledge Vault의 민감 정보가 LLM API로 전송되는 구조에 대한 보안 분석이 빠져 있다. |

---

## 선택 요소 (해당되는 것만)

| 항목 | 내용 |
|------|------|
| **Baseline 비교** | **ScreenshotVQA** (gpt-4.1-mini / gemini-2.5-flash 기반): <br>- Gemini 장문맥: 11.66% / 236.70 MB → MIRIX 대비 정확도 -47.84%p, 스토리지 14.9배 <br>- SigLIP@50 RAG: 44.10% / 15.07 GB → MIRIX 대비 정확도 -15.40%p, 스토리지 948배 <br><br> **LOCOMO** (gpt-4.1-mini 기준 재구현): <br>- A-Mem (gpt-4o-mini): 48.38% → MIRIX 대비 -37.0%p <br>- LangMem: 78.05% → MIRIX 대비 -7.33%p <br>- RAG-500: 51.62% → MIRIX 대비 -33.76%p <br>- Mem0: 62.47% → MIRIX 대비 -22.91%p <br>- Zep: 79.09% → MIRIX 대비 **-6.29%p** (두 번째로 강한 baseline) <br>- Full-Context 상한: 87.52% → MIRIX 대비 +2.14%p (거의 도달) |
| **Ablation Study** | 논문에 Ablation Study 없음. 6개 메모리 컴포넌트 각각의 기여도, Active Retrieval 유무에 따른 성능 변화, Meta Memory Manager의 라우팅 정확도 등은 별도로 분석되지 않았다. |
