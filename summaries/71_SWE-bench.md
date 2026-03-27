# SWE-bench: Can Language Models Resolve Real-World GitHub Issues?

> **논문 정보**: Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik Narasimhan (Princeton University, University of Chicago)
> **arXiv**: 2310.06770 (2023.10) | **학회**: ICLR 2024 Oral
> **코드**: https://swebench.com

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 코딩 벤치마크(HumanEval 등)는 자기 완결적 짧은 문제로, 실세계 소프트웨어 엔지니어링의 복잡성(대규모 코드베이스 탐색, 멀티파일 수정, 실행 환경 상호작용)을 반영하지 못한다. |
| **Motivation** | 실제 소프트웨어 엔지니어링은 버그 리포트 이해, 수천 파일 탐색, 여러 파일 패치, 테스트 실행을 동시에 요구한다. GitHub 이슈-PR 쌍은 이를 자연스럽게 포착하는 풍부한 데이터 소스이다. |
| **Limitation** | Python에만 한정. 실행 기반 평가만으로 코드 품질(효율성, 가독성) 보장 못함. 인기 레포 편향. 멀티모달 이슈 처리 불가. |

---

## Method

### 1. 3단계 구축 파이프라인

**Stage I — 레포 선정 및 스크래핑**: 12개 인기 Python 레포(django, flask, matplotlib, scikit-learn 등)에서 ~90,000개 PR 수집

**Stage II — 속성 기반 필터링**: GitHub 이슈를 해결하는 merged PR + 테스트 파일을 수정한 PR만 유지

**Stage III — 실행 기반 필터링**: PR 테스트 변경분 적용 후 fail-to-pass 테스트가 1개 이상 존재하는 인스턴스만 유지 → 90,000개 → **2,294개**

### 2. 태스크 정의 및 평가
- **입력**: 이슈 텍스트 + 코드베이스 스냅샷 (평균 3,010개 파일, 438K 라인)
- **출력**: 패치 파일 (diff 형식)
- **평가**: `patch` 적용 후 레포 테스트 실행, 모든 fail-to-pass 통과 시 해결
- 인스턴스당 평균 9.1개 fail-to-pass 테스트, 총 120.8개 테스트 실행

### 3. 컨텍스트 검색 전략
- **BM25**: 이슈 텍스트로 관련 파일 검색. 컨텍스트 길어질수록 성능 오히려 저하
- **Oracle**: 참조 패치가 수정한 파일 직접 제공 (상한선)
- **Oracle-Collapsed**: 수정 라인 ±15줄만 유지 (위치 단서 제공)
- BM25는 27k 컨텍스트에서 oracle 파일의 약 44%만 포함

### 4. SWE-Llama Fine-tuning
- 37개 추가 레포에서 19,000개 이슈-PR 쌍 수집 (평가와 레포 비중복)
- CodeLlama-Python 7b/13b 기반, LoRA fine-tuning

---

## Key Contribution

1. **실세계 SE 벤치마크의 사실상 표준**: Devin, SWE-agent, Cursor 등 코딩 에이전트 평가 기준점
2. **실행 기반 자동 검증**: 레포의 실제 테스트로 패치 정확성 자동 검증
3. **지속 갱신 가능**: 자동화 파이프라인으로 새 인스턴스 지속 추가 가능
4. **SWE-Llama 공개**: 100k 토큰 컨텍스트 처리 오픈소스 모델

---

## Experiment & Results

**주요 결과 (BM25 Retrieval)**:

| 모델 | % Resolved | % Apply |
|------|-----------|---------|
| Claude 3 Opus | **3.79%** | 46.56% |
| Claude 2 | 1.97% | 43.07% |
| GPT-4-turbo | 1.31% | 26.90% |
| ChatGPT-3.5 | 0.17% | 26.33% |
| SWE-Llama 13b | 0.70% | 53.62% |

**Oracle 설정**: Claude 2 **4.8%** (BM25 1.97% 대비 2.4배), Oracle-Collapsed Claude 3 Opus **9.39%**

**분석**:
- 컨텍스트 길이와 성능 반비례: 20k 이하 인스턴스의 해결률이 >100k 대비 크게 우월
- 모델 패치 평균 19.6 라인 vs gold 패치 44.1 라인 — 실제 해결에 필요한 수정 범위의 절반 미만
- SWE-Llama: oracle 컨텍스트로 학습되어 BM25 컨텍스트에서 불필요 파일까지 수정 시도

**데이터셋 통계**: 평균 이슈 195.1 단어, 코드베이스 3,010 파일/438K 라인, gold 패치 32.8 라인/1.7 파일/3.0 함수

**후속 발전**: SWE-agent 12.29% → Devin 13.86% → 2025년 50%+ 이상으로 해결률 급격 향상
