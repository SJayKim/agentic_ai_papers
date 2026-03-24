# Unveiling Privacy Risks in LLM Agent Memory

> **논문 정보**
> - arXiv: 2502.13172v2 (2025년 6월 3일)
> - 저자: Bo Wang, Weiyi He, Shenglai Zeng, Zhen Xiang, Yue Xing, Jiliang Tang, Pengfei He
> - 소속: Michigan State University, University of Georgia

---

## 필수 요소

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전트의 메모리 모듈에 저장된 과거 사용자 쿼리(프라이빗 정보)가 외부 공격자에 의해 추출될 수 있는가. 기존 RAG 데이터 추출 공격("Please repeat all the context" 등)은 에이전트의 복잡한 워크플로우(코드 실행, 웹 클릭 등 텍스트 이외의 액션)에서는 작동하지 않아, 에이전트 메모리에 특화된 공격 방법이 존재하지 않았다. |
| **Motivation** | 의료(EHR 환자 진단 이력), 온라인 쇼핑(구매 패턴), 자율주행(과거 주행 시나리오) 등 민감한 도메인에서 LLM 에이전트가 광범위하게 배포되고 있다. 이들 에이전트는 과거 사용자-에이전트 상호작용 기록을 메모리에 저장하는데, 이 메모리가 얼마나 취약한지 체계적으로 연구된 바 없었다. 특히 에이전트의 솔루션이 텍스트 생성이 아닌 도구/API 호출로 이루어지는 경우, 기존 RAG 추출 공격은 작동하지 않는다. |
| **Method** | **MEXTRA (Memory EXTRaction Attack)**를 제안. 공격 프롬프트를 두 파트로 설계한다: (1) **Locator (˜q_loc)**: 원하는 정보(이전 예시 쿼리)를 지목하는 부분 — "I lost previous example queries"처럼 메모리에서 검색된 사용자 쿼리를 직접 요청; (2) **Aligner (˜q_align)**: 에이전트의 워크플로우에 맞게 출력 포맷을 지정 — "please enter them in the search box"처럼 에이전트가 정상 액션처럼 해당 정보를 출력하게 유도. 또한 GPT-4 기반의 **자동화된 다양한 공격 프롬프트 생성** 방법을 제공: 기본 지식(Basic, I_basic)과 구현 세부 사항을 아는 고급 지식(Advanced, I_advan) 두 가지 수준의 인스트럭션으로 n개의 다양한 공격 프롬프트를 자동 생성하여 메모리에서 서로 다른 레코드를 검색·추출한다. |
| **Key Contribution** | (1) LLM 에이전트 메모리에 특화된 최초의 체계적 프라이버시 공격 MEXTRA 제안 — 기존 RAG 추출 공격과 달리 에이전트 워크플로우(코드 실행, 웹 액션 등)에서도 동작함; (2) Locator+Aligner 이중 구조의 공격 프롬프트 설계 원칙 제시; (3) 공격자 지식 수준(Basic/Advanced)에 따른 자동화 프롬프트 생성 방법론; (4) 에이전트 설계자 관점(유사도 함수, 임베딩 모델, 메모리 크기, 검색 깊이, 백본 LLM)과 공격자 관점(공격 횟수, 지식 수준)에서 메모리 유출에 영향을 미치는 요인 종합 분석. |
| **Experiment/Results** | **실험 대상**: EHRAgent(의료 EHR 코드 생성 에이전트, edit distance 기반 top-4 검색)와 RAP(온라인 쇼핑 웹 에이전트, cosine similarity 기반 top-3 검색). LLM 백본: GPT-4o, 메모리 크기: 200. **주요 결과 (n=30 공격 프롬프트, 메모리 200개 기준)**: EHRAgent에서 EN=50 (25% 추출), CER=0.83, AER=0.83, EE=0.42; RAP에서 EN=26 (13% 추출), CER=0.87, AER=0.90, EE=0.29. **메모리 설정 영향 (Table 2)**: edit distance 사용 시 cosine similarity 대비 일관되게 높은 추출 성능 (EHRAgent 메모리 500개 기준 edit=59 vs. cosine MiniLM=24); 메모리 크기가 클수록 추출 수 증가 (50→500 시 EHRAgent edit: 31→59); 검색 깊이 k 증가 시 추출 수 증가 (k=1→5 시 EHRAgent EN: 8→59). **백본 비교 (Table 3, RAP)**: GPT-4o(EN=26) > GPT-4(EN=23) > Llama3-70b(EN=17). **공격 프롬프트 수 영향**: n=50 시 edit distance 사용 에이전트는 메모리의 30% 이상, cosine similarity 사용 에이전트는 10% 이상 유출. I_advan이 I_basic 대비 RN 대폭 향상 (RAP cosine n=50: RN 35→84). **QA-Agent 일반화 실험 (Table 4)**: I_advan+cosine에서 EN=55, EE=0.46, 메모리 200개의 약 27.5% 추출. |
| **Limitation** | (1) 단일 에이전트 설정에서만 평가 — 다중 에이전트 환경(에이전트 간 메모리 공유)으로의 확장 미검토; (2) 세션 제어(사용자/세션 수준 메모리 격리) 미포함 — 현재 프레임워크에서 여러 사용자가 동일 세션을 공유할 수 있어 공격자가 다른 사용자 정보에도 접근 가능하지만, 세션 제어 통합의 표준 방법이 없어 미래 과제로 남김; (3) 방어 기법에 대한 평가 미흡 — 입출력 필터링, 파라프레이징, 메모리 익명화 등의 방어 효과를 실험적으로 검증하지 않고 논의 수준에 그침. |

---

## 선택 요소

| 항목 | 내용 |
|------|------|
| **Threat Model** | **블랙박스 설정**: 공격자는 에이전트에 입력 쿼리만 보낼 수 있고, 내부 파라미터·프롬프트·메모리 내용에는 직접 접근 불가. **공격자 지식 수준 2단계**: (1) Basic — 에이전트의 적용 도메인과 태스크 유형만 앎 (예: "이건 의료 기록 관리 에이전트"); (2) Advanced — 에이전트 메모리의 유사도 함수(edit distance 또는 cosine similarity) 같은 구현 세부 사항까지 추론/파악. **공격자 목표**: 메모리 M에 저장된 과거 사용자 쿼리 q_i를 최대한 많이 추출. n개의 다양한 공격 프롬프트 {˜q_j}를 설계하여 각 쿼리가 다른 메모리 레코드를 검색하게 함으로써 총 추출 집합 Q = ∪ ˜o_j의 크기를 극대화. |
| **Baseline 비교** | (1) **w/o aligner** (aligner 없이 locator만): EHRAgent EN=36(-28%), RAP EN=6(-77%) — aligner의 중요성 확인; (2) **w/o req** (요구사항 없이 예시만): EHRAgent EN=39(-22%), RAP EN=25(-4%); (3) **w/o demos** (예시 없이 요구사항만): EHRAgent EN=29(-42%), RAP EN=8(-69%); 기존 RAG 공격 프롬프트 "Please repeat all the context"는 에이전트 워크플로우에 맞지 않아 메모리 쿼리 대신 시스템 프롬프트 요약을 반환하며 실패. MEXTRA는 모든 기준선 대비 EN, CER, AER에서 우수한 성능을 기록. |
