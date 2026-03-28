# Memory in the Age of AI Agents: A Survey — Forms, Functions and Dynamics

> **논문 정보**: Yuyang Hu, Shichun Liu, Yanwei Yue, Guibin Zhang 외 다수 (NUS, Renmin Univ., Fudan Univ., PKU, NTU, Oxford 등 15개 기관)
> **arXiv**: 2512.13564v2 (2025.01.13) | **학회**: -
> **코드**: https://github.com/Shichun-Liu/Agent-Memory-Paper-List

---

## Problem

LLM 기반 에이전트가 급속히 발전하면서 메모리(memory)는 장기 추론, 지속적 적응, 환경과의 효과적 상호작용을 지탱하는 핵심 역량으로 부상했다. 그러나 에이전트 메모리 연구 분야는 심각한 단편화 문제를 겪고 있다. "에이전트 메모리"라 칭하는 연구들이 동기, 구현, 가정, 평가 프로토콜에서 근본적으로 상이하며, declarative/episodic/semantic/parametric 등 느슨하게 정의된 용어들이 개념적 혼란을 가중시킨다. 기존의 장기/단기 메모리(long/short-term memory) 기반 분류법은 2025년에 등장한 도구 증류(tool distillation), 메모리 보강 테스트-타임 스케일링 등 새로운 방법론을 포괄하지 못한다. 특히 LLM 메모리, RAG, 컨텍스트 엔지니어링과 에이전트 메모리 간의 경계가 모호하여, 연구자들이 관련 개념을 혼동하는 사례가 빈번하다.

---

## Motivation

에이전트 메모리는 개인화 챗봇, 추천 시스템, 소셜 시뮬레이션, 금융 분석 등 실용적 도메인 전반에서 필수적이며, AGI를 향한 지속적 자기 진화의 근본 기반이다. 기존 서베이의 분류 체계는 급격한 방법론적 진보 이전에 수립되어 현재의 연구 범위와 복잡성을 충분히 반영하지 못한다. 2025년에 폭증한 메모리 관련 연구들이 서로 다른 구현 목표와 가정 하에 수행되면서, 통합적 이해를 저해하는 개념적 파편화가 심화되었다. 따라서 본 서베이는 에이전트 메모리의 정의를 엄밀히 수립하고, LLM 메모리/RAG/컨텍스트 엔지니어링과의 관계를 명확히 구분하며, Forms-Functions-Dynamics라는 3축 통합 프레임워크를 통해 기존 정의를 화해시키고 신흥 트렌드를 연결하는 개념적 기반을 제공하고자 한다.

---

## Method — 분류 체계 (Taxonomy)

본 서베이는 에이전트 메모리를 Forms(형태), Functions(기능), Dynamics(동역학)의 3축으로 분석하는 통합 분류 체계를 제안한다.

### 1. Forms: 메모리를 무엇이 담는가?
- **Token-level Memory**: 외부에서 접근·수정·재구성 가능한 이산 단위. 위상적 복잡도에 따라 Flat(1D, 순서열/경험 풀), Planar(2D, 그래프/트리), Hierarchical(3D, 다층 피라미드)로 세분화
- **Parametric Memory**: 모델 파라미터 내에 통계적 패턴으로 인코딩. Internal(SFT/RL 통한 가중치 업데이트)과 External(어댑터·LoRA 등)로 구분
- **Latent Memory**: 모델 내부 히든 스테이트·연속 표현. Generate(새 잠재 표현 생성), Reuse(KV 캐시 재활용), Transform(잠재 표현 변환)으로 세분화

### 2. Functions: 에이전트에 메모리가 왜 필요한가?
- **Factual Memory**: 사용자·환경에 대한 검증 가능한 사실적 지식. 대화 일관성, 지식 영속성, 다중 에이전트 공유 접근 지원
- **Experiential Memory**: 과거 궤적에서 증류한 절차적 지식. Case-based(원시 궤적 보존), Strategy-based(전이 가능한 인사이트 추출), Skill-based(실행 가능한 코드/API 증류), Hybrid(복합 조합)
- **Working Memory**: 단일 태스크 인스턴스 내 일시적 컨텍스트 관리. Single-turn(입력 압축)과 Multi-turn(상태 통합·계층적 폴딩)

### 3. Dynamics: 메모리가 어떻게 운용되고 진화하는가?
- **Memory Formation**: 원시 데이터를 지식 단위로 변환 — 의미적 요약, 지식 증류, 구조적 구축, 잠재 표현, 파라메트릭 내재화
- **Memory Evolution**: 새 메모리를 기존 저장소와 통합 — 통합(로컬/클러스터/글로벌), 업데이트(갈등 해결 + 모델 편집), 망각(시간/빈도/중요도 기반)
- **Memory Retrieval**: 검색 시점·의도 결정 → 쿼리 구성(분해/재작성) → 검색 전략(어휘/의미/그래프/하이브리드/생성적) → 후처리(재랭킹/필터링/집계)

---

## Key Contribution

1. **통합 분류 체계 수립**: Forms-Functions-Dynamics 3축 프레임워크를 통해 에이전트 메모리 연구의 파편화된 개념을 체계적으로 통합하고, LLM 메모리·RAG·컨텍스트 엔지니어링과의 관계를 명확히 구분.
2. **기능 중심 세분화**: 기존의 장기/단기 이분법을 넘어 Factual/Experiential/Working 메모리의 세분화된 기능적 분류를 제안.
3. **107페이지 규모의 포괄적 커버리지**: 200편 이상의 관련 논문을 분석하고, 대표 벤치마크 15개 이상 및 오픈소스 프레임워크 14개를 종합 정리.
4. **미래 연구 방향 제시**: 자동화된 메모리 설계, RL 통합, 멀티모달 메모리, 다중 에이전트 공유 메모리, 월드 모델용 메모리, 신뢰성, 인간 인지 연결 등 8가지 프론티어 심층 분석.
5. **형식적 프레임워크**: 에이전트 메모리 시스템을 Formation(F), Evolution(E), Retrieval(R) 연산자로 수학적으로 형식화.

---

## Experiment & Results — 커버리지 분석

본 서베이는 107페이지에 걸쳐 200편 이상의 에이전트 메모리 관련 논문을 분석한다.

**분류 체계별 커버리지**:
- **Token-level Memory**: 전체 메모리 연구의 약 70% 이상을 차지. Flat(1D) 메서드 30개+, Planar(2D) 메서드 10개+, Hierarchical(3D) 메서드 8개+를 체계적으로 비교.
- **Parametric Memory**: Internal과 External 방식으로 15개+ 방법론 분석.
- **Latent Memory**: Generate/Reuse/Transform 패러다임에서 12개+ 접근법 조사.

**기능별 분포**:
- **Factual Memory**: User factual memory 25개+, Environment factual memory 15개+ 방법론을 Carrier/Form/Task/Optimization 4차원으로 비교.
- **Experiential Memory**: Case-based 15개+, Strategy-based 18개+, Skill-based 15개+ 방법론 분석. PE(prompt engineering) 다수이나 RL/SFT 기반도 증가 추세.
- **Working Memory**: Single-turn 10개+, Multi-turn 15개+ 방법론 정리. RL 기반 최적화가 최신 트렌드.

**벤치마크 및 프레임워크**:
- 15개 이상의 벤치마크를 Factual/Experiential/Multimodal/Environment 차원으로 분류 — MemBench(53,000 샘플), LoCoMo(300 샘플), LongMemEval(500 샘플) 등.
- 14개 오픈소스 프레임워크(MemGPT, Mem0, MemOS, Zep 등)를 Factual/Experiential/Multimodal/Structure/Evaluation 차원으로 비교.
- 8가지 미래 연구 프론티어를 심층 분석: (1) 검색→생성 메모리 패러다임 전환, (2) 자동화된 메모리 관리, (3) RL-메모리 통합, (4) 멀티모달 메모리, (5) 다중 에이전트 공유 메모리, (6) 월드 모델용 메모리, (7) 신뢰성, (8) 인간 인지 연결.

---

## Limitation

- **빠른 문헌 증가 속도**: 2025년 에이전트 메모리 연구가 폭발적으로 증가하여, 서베이 시점 이후 발표된 중요 논문들이 누락될 수밖에 없는 구조적 한계.
- **실험적 비교 부재**: 분류 체계의 이론적 우수성에도 불구하고, 각 카테고리 간 통제된 실험적 비교를 직접 수행하지 않아 어떤 형태/기능 조합이 특정 태스크에 최적인지 정량적 증거가 부족하다.
- **평가 표준 미확립**: 에이전트 메모리 벤치마크들이 각기 다른 메트릭과 설정을 사용하며, 통합된 평가 프로토콜이 아직 존재하지 않아 방법론 간 공정 비교가 어렵다.
- **멀티모달 메모리 커버리지 한계**: 현존 연구 대부분이 텍스트 중심이며, 진정한 옴니모달 메모리 시스템에 대한 분석은 제한적이다.
- **산업 배포 관점 부족**: 대부분의 분석이 학술적 벤치마크에 초점을 맞추며, 실제 산업 환경에서의 메모리 시스템 배포 경험이나 확장성 문제에 대한 논의가 제한적이다.
