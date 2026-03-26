# OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments

> **논문 정보**: Tianbao Xie, Danyang Zhang, Jixuan Chen 외 (HKU, Salesforce, XLang Lab)
> **arXiv**: 2404.07972 (2024.04)
> **코드**: https://os-world.github.io/

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 에이전트 벤치마크는 시뮬레이션 환경이나 웹 전용으로, 실제 컴퓨터 환경(OS, 데스크톱 앱, 멀티앱 워크플로우)에서의 에이전트 능력을 평가하지 못한다. |
| **Motivation** | AI 어시스턴트가 실제로 유용하려면 Ubuntu/Windows/macOS에서 브라우저, 오피스, 터미널 등을 조작할 수 있어야 한다. 369개 실세계 태스크에서 인간 72% vs 최고 모델 12%의 격차가 이를 입증. |
| **Limitation** | 저자 언급: 369개 태스크로 규모 제한. 독자 관점: VM 기반 환경이 실제 사용자 환경과 다를 수 있음. |

---

## Method

1. **실제 컴퓨터 환경**: Ubuntu, Windows, macOS VM에서 369개 태스크
2. **태스크 유형**: 웹 브라우징, 데스크톱 앱 조작, 파일 관리, 멀티앱 워크플로우
3. **멀티모달 입력**: 스크린샷 기반 GUI 그라운딩 + 자연어 지시

---

## Key Contribution

1. **최초의 실제 OS 환경 에이전트 벤치마크**: 시뮬레이션이 아닌 실제 컴퓨터에서 평가
2. **GUI 그라운딩의 핵심 병목 발견**: 모델이 스크린샷에서 UI 요소를 정확히 식별하지 못하는 것이 주요 실패 원인

---

## Experiment & Results

- 인간: 72.36%, 최고 모델(GPT-4V): 12.24%
- GUI 그라운딩 실패가 전체 오류의 상당 부분 차지
