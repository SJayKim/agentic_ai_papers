# SWE-bench: Can Language Models Resolve Real-World GitHub Issues?

> **논문 정보**: Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik Narasimhan (Princeton University, University of Chicago)
> **arXiv**: 2310.06770 (2023.10)
> **코드**: https://swebench.com

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 코딩 벤치마크(HumanEval 등)는 자기 완결적인 짧은 문제로, 실세계 소프트웨어 엔지니어링의 복잡성(대규모 코드베이스 탐색, 멀티파일 수정, 실행 환경 상호작용)을 반영하지 못한다. |
| **Motivation** | 실제 소프트웨어 엔지니어링은 버그 리포트 이해, 수천 파일의 코드베이스 탐색, 여러 파일에 걸친 패치 생성, 테스트 실행을 요구한다. GitHub 이슈-PR 쌍은 이를 자연스럽게 포착하는 풍부한 데이터 소스. |
| **Limitation** | 저자 언급: Python 레포지토리에 한정. 독자 관점: 인기 레포지토리에 편향되어 도메인 특화 코드베이스의 대표성 부족. |

---

## Method

1. **3단계 벤치마크 구축 파이프라인**
   - **Stage 1**: 12개 인기 Python 레포에서 ~90,000 PR 수집
   - **Stage 2**: 이슈 해결 + 테스트 기여 PR 필터링
   - **Stage 3**: 실행 기반 필터링 — PR 적용 전후 테스트 상태 변화 확인
   - 최종: **2,294개 태스크 인스턴스**

2. **태스크 정의**: 이슈 텍스트 + 코드베이스 스냅샷이 주어지면, 이슈를 해결하는 패치를 생성. 레포의 테스트 프레임워크로 자동 검증

3. **SWE-bench-train**: 37개 레포에서 19,000개 학습용 인스턴스 추가 공개

---

## Key Contribution

1. **실세계 소프트웨어 엔지니어링 벤치마크의 사실상 표준**: Devin, SWE-agent, Cursor 등 코딩 에이전트 평가의 기준
2. **실행 기반 자동 검증**: 단위 테스트로 패치의 정확성을 자동 평가하여 높은 평가 신뢰성
3. **코딩 에이전트 발전의 촉매**: SWE-bench 도입 이후 해결률이 1.96% → 50%+ (2024~2025)로 급격히 향상

---

## Experiment & Results

- **초기 결과 (2023)**: Claude 2: 1.96%, SWE-Llama 13B: Claude 2와 동등
- **후속 발전**: SWE-agent 12.29% → Devin 13.86% → 2025년 기준 50%+ (Anthropic Claude 등)
- 코드베이스 규모: 평균 수천 파일, PR은 평균 여러 파일 수정 필요
