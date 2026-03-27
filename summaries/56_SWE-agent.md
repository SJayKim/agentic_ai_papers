# SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

> **논문 정보**: John Yang, Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, Ofir Press (Princeton University)
> **arXiv**: 2405.15793 (2024.05, NeurIPS 2024)
> **코드**: https://github.com/SWE-agent/SWE-agent

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | LLM이 실제 소프트웨어 엔지니어링 태스크(GitHub 이슈 해결)를 수행하려면 대규모 코드베이스를 탐색하고 수정해야 하지만, 기존 Linux 쉘·RAG 기반 인터페이스는 LLM 특성에 맞지 않아 효율적 상호작용이 불가능하다. |
| **Motivation** | HCI에서 좋은 인터페이스가 인간 생산성을 높이듯, ACI(에이전트-컴퓨터 인터페이스)를 LLM 특성에 맞게 설계하면 별도 파인튜닝 없이도 소프트웨어 엔지니어링 능력을 크게 향상시킬 수 있다. |
| **Limitation** | 저자: 복잡한 멀티파일 수정과 잘못된 구현이 여전히 주요 실패 원인(52%). 독자: 쉘 기반 인터페이스가 GUI 태스크에 부적합. 비용 예산($4/instance) 초과 시 강제 제출. 소형 오픈소스 모델에서 성능 저하가 두드러짐. |

---

## Method

SWE-agent는 ReAct 패턴(Thought + Action + Observation) 기반으로 동작하며, ACI 설계가 핵심이다.

**ACI 설계 4대 원칙**
1. **단순한 액션**: bash 명령 대신 소수 옵션의 커스텀 명령어 제공
2. **간결한 액션**: 탐색, 검색, 편집을 최소 액션으로 통합
3. **풍부하되 간결한 피드백**: 편집 후 즉시 업데이트된 파일 뷰 제공
4. **에러 전파 방지 가드레일**: linter 통합으로 잘못된 편집 즉각 감지·폐기

**주요 ACI 컴포넌트**
- **Search/Navigation**: `search_dir`, `search_file`, `find_file` — Summarized Search로 비효율적 순차 확인 방지
- **File Viewer**: `open`, `scroll_up/down`, `goto` — 100줄 윈도우, 경로·줄 번호 표시
- **File Editor**: `edit [start]:[end]` — 멀티라인 편집, linter 구문 오류 감지 시 자동 폐기
- **Context Management**: 히스토리 프로세서가 최근 5개 관찰만 유지

**에이전트 행동 패턴** (286개 성공 궤적 분석)
- 초반: `find_file`, `search_dir` → `open`, `goto`의 계층적 코드 로컬라이제이션
- 중반 이후: `edit` + `python` 실행의 반복적 "편집-검증" 루프
- 성공: 중앙값 12 스텝·$1.21 / 실패: 평균 21 스텝·$2.52

---

## Key Contribution

1. **ACI 개념 체계화**: LLM용 에이전트-컴퓨터 인터페이스 설계 원칙을 최초로 정립
2. **SWE-bench SOTA**: 당시 비대화형 최고 3.79% 대비 3.3배 향상된 12.47%
3. **인터페이스가 성능에 결정적**: Shell-only 대비 10.7%p 개선을 ablation으로 검증
4. **오픈소스 공개**: 코드, 데이터, 리더보드를 swe-agent.com에 공개

---

## Experiment & Results

- **벤치마크**: SWE-bench Full(2,294개), Lite(300개), HumanEvalFix

**주요 성능**:

| 시스템 | Full | Lite | Avg Cost |
|--------|------|------|----------|
| RAG w/ Claude 3 Opus | 3.79% | 4.33% | $0.25 |
| Shell-only w/ GPT-4 Turbo | - | 11.00% | $1.46 |
| **SWE-agent w/ GPT-4 Turbo** | **12.47%** | **18.00%** | $1.67 |
| SWE-agent w/ Claude 3 Opus | 10.46% | 13.00% | $2.18 |

- HumanEvalFix: Python 87.7%, JS 89.7%, Java 87.9% (이전 최고 WaveCoder 57.9% 대비 대폭 상회)

**ACI Ablation** (Lite, 기본 18.0%):
- edit w/o linting: 15.0% / No edit: 10.3% / Iterative Search: 12.0% / Full file: 12.7% / Full history: 15.0%

**실패 모드** (n=248): 잘못된 구현 39.9%, 편집 회복 실패 23.4%, 과도하게 구체적 12.1%, 탐색 실패 12.9%

**편집 신뢰성**: 51.7%에서 1회 이상 편집 실패. 첫 시도 성공률 90.5%, 1회 실패 후 회복 57.2%
