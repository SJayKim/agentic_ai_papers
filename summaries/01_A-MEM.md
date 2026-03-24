# A-MEM: Agentic Memory for LLM Agents

> **논문 정보**: Wujiang Xu, Zujie Liang, Kai Mei, Hang Gao, Juntao Tan, Yongfeng Zhang (Rutgers University, AIOS Foundation)
> **arXiv**: 2502.12110 (최종 버전: 2025년 10월 8일)
> **코드**: https://github.com/WujiangXu/AgenticMemory

---

## 필수 요소

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전트의 기존 메모리 시스템은 개발자가 미리 메모리 저장 구조, 저장 시점, 검색 타이밍을 모두 고정(predefined)으로 설정해야 한다. Mem0처럼 그래프 DB를 도입한 시스템도 사전에 정의된 스키마와 관계에 종속되어, 새로운 지식이 들어와도 기존 프레임워크 안에서만 연결될 뿐 새로운 조직 패턴을 자율적으로 생성하지 못한다. 결과적으로 다양한 태스크에 대한 적응력이 낮고, 장기 상호작용에서 효과가 떨어진다. |
| **Motivation** | LLM 에이전트가 복잡한 실제 환경에서 장기적으로 활용될수록, 유연한 지식 조직과 지속적 적응이 필수적이다. 예를 들어 에이전트가 새로운 수학적 풀이법을 학습하면 이를 기존 메모리 네트워크와 창의적으로 연결하고 기존 메모리도 업데이트해야 하는데, 기존 시스템은 이를 지원하지 못한다. 장기 대화 데이터셋(LoCoMo: 평균 9K 토큰, 최대 35 세션)에서 기존 방법들이 멀티홉 추론에 특히 취약한 것이 확인되었다. |
| **Method** | **Zettelkasten 방법론**에서 영감을 받은 **A-MEM(Agentic Memory)** 시스템으로, 세 가지 핵심 메커니즘으로 구성된다. **(1) Note Construction**: 새 메모리가 입력되면 LLM이 자동으로 키워드(K), 태그(G), 문맥 설명(X)을 생성하고, 이를 `all-minilm-l6-v2` 텍스트 인코더로 임베딩 벡터(e)화하여 구조화된 노트 `m = {c, t, K, G, X, e, L}`로 저장한다. **(2) Link Generation**: 새 노트가 추가되면 코사인 유사도 기반으로 상위 k개의 관련 메모리를 검색하고, LLM이 이들 사이의 의미론적 연결 여부를 판단하여 링크(L)를 자율 생성한다. **(3) Memory Evolution**: 새 메모리가 통합될 때, 인접 메모리들의 문맥 설명·키워드·태그를 LLM이 자동으로 업데이트한다(`m*_j <- LLM(m_n || M_near\m_j || m_j || Ps3)`). 검색 시에는 쿼리 임베딩과 메모리 임베딩 간 코사인 유사도로 상위 k개(기본값 k=10)를 반환하며, 링크된 메모리도 함께 제공한다. |
| **Key Contribution** | (1) 에이전트가 메모리 구조를 **사전 설정 없이 자율적으로 생성·연결·진화**시키는 agentic memory 시스템 제안. (2) **Link Generation + Memory Evolution** 두 모듈의 결합으로, 단순 유사도 검색을 넘어 고차 패턴(higher-order patterns)을 자동 발견. (3) 기존 방법 대비 토큰 사용량을 **85~93% 절감**하면서도 성능은 향상 (LoCoMo/MemGPT의 약 16,900 토큰 → A-MEM 약 1,200 토큰). (4) Zettelkasten의 원자적 노트·유연한 링킹 원칙을 LLM 기반 메모리 시스템에 구현. |
| **Experiment/Results** | **데이터셋**: LoCoMo(7,512개 QA 쌍, 평균 9K 토큰, 최대 35 세션; 멀티홉·시간적 추론·오픈도메인·단일홉·적대적 질문 5개 카테고리), DialSim(TV 드라마 기반 장기 다자 대화, 1,300 세션, 약 350,000 토큰, 1,000+ 질문/세션). **모델**: GPT-4o-mini, GPT-4o, Qwen2.5-1.5B/3B, Llama 3.2 1B/3B 총 6개. **주요 수치 (LoCoMo, GPT-4o-mini 기준, F1)**: A-MEM이 모든 카테고리에서 1위(평균 랭킹 1.2). Temporal F1=45.85 vs MemGPT 25.52(약 80% 향상), Multi Hop F1=27.02 vs MemGPT 26.65, Adversarial F1=50.03 vs MemGPT 43.29. DialSim에서 A-MEM F1=3.45로 LoCoMo(2.55) 대비 +35%, MemGPT(1.18) 대비 +192% 향상. Qwen2.5/Llama 3.2 등 비 GPT 모델에서도 모든 베이스라인을 모든 카테고리에서 일관되게 능가. **비용**: GPT-4o-mini 기준 메모리 작업당 $0.0003 미만, 처리 시간 5.4초(GPT-4o-mini) / 1.1초(Llama 3.2 1B, 단일 GPU). **스케일링**: 메모리 100만 개에서도 검색 시간 3.70μs(1,000개 기준 0.31μs), O(N) 선형 메모리 사용. |
| **Limitation** | (1) **LLM 의존성**: 메모리 조직 품질이 기반 LLM의 능력에 좌우되며, 모델마다 생성하는 문맥 설명과 연결이 달라질 수 있다. (2) **텍스트 모달리티 한정**: 현재 구현은 텍스트 기반 상호작용에만 집중하며, 이미지나 오디오 등 멀티모달 정보 처리는 미래 과제로 남긴다. (3) **추가적 한계 (독자 관점)**: 메모리 노트 생성·링크 판단·메모리 진화에 각각 별도 LLM 호출이 필요하므로, 메모리 저장 단계의 LLM API 비용이 누적 메모리 크기에 비례해 증가한다. 또한 최적 k값이 태스크마다 다르고(Single Hop은 k=50에서 F1 44.55 최고, Multi Hop은 k=40에서 수렴), 실제 배포 시 태스크 특성에 맞는 k 튜닝이 필요하다. |

---

## 선택 요소

| 항목 | 내용 |
|------|------|
| **Baseline 비교** | **LoCoMo**: 전체 이전 대화를 프롬프트에 직접 삽입 (~16,910 토큰). GPT-4o-mini 기준 Temporal F1=18.41, Adversarial F1=69.23(단순 사실 검색에서는 강함). **ReadAgent**: 에피소드 페이지네이션→메모리 요약→인터랙티브 검색 3단계 방식 (~643 토큰). 전반적으로 낮은 성능(Multi Hop F1=9.15). **MemoryBank**: Ebbinghaus 망각 곡선 기반 동적 메모리 업데이트 (~432 토큰). 가장 낮은 성능군(Multi Hop F1=5.00). **MemGPT**: OS 메모리 계층 구조 모방, 주 컨텍스트(RAM) + 외부 컨텍스트(디스크) 방식 (~16,977 토큰). GPT 모델에서는 A-MEM과 경쟁하나, A-MEM이 Multi Hop(27.02 vs 26.65)·Temporal(45.85 vs 25.52)·Adversarial(50.03 vs 43.29) 모두에서 앞섬. 스케일링에서는 MemoryBank 검색 시 100만 메모리 기준 1.91μs로 A-MEM(3.70μs)보다 약간 빠르지만, ReadAgent는 120,069μs로 극히 느림. |
| **Ablation Study** | GPT-4o-mini 기준 세 가지 설정 비교. **w/o LG & ME(링크 생성·메모리 진화 모두 제거)**: Multi Hop F1=9.65, Temporal F1=24.55, Single Hop F1=13.28, Adversarial F1=15.32로 A-MEM 대비 대폭 하락. **w/o ME(메모리 진화만 제거)**: Multi Hop F1=21.35, Temporal F1=31.24, Single Hop F1=39.17, Adversarial F1=44.16으로 중간 성능. **A-MEM(전체)**: Multi Hop F1=27.02, Temporal F1=45.85, Single Hop F1=44.65, Adversarial F1=50.03. 결론: Link Generation이 메모리 연결의 기초를 형성하고, Memory Evolution이 추가 성능 향상을 제공하며, 두 모듈은 상호 보완적으로 작동함. T-SNE 시각화에서도 A-MEM이 기본 메모리 대비 훨씬 응집된 클러스터 패턴을 보임. |
