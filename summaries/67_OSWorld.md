# OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments

> **논문 정보**: Tianbao Xie, Danyang Zhang, Jixuan Chen 외 (HKU, CMU, Salesforce, Waterloo)
> **arXiv**: 2404.07972 (2024.04) | **학회**: NeurIPS 2024
> **코드**: https://os-world.github.io/

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 기존 벤치마크는 시뮬레이션이거나 웹/모바일 단일 도메인으로 제한되어, 실제 OS에서 멀티앱 워크플로우를 수행하는 에이전트 능력을 평가하지 못한다. |
| **Motivation** | AI 어시스턴트가 유용하려면 Ubuntu/Windows/macOS에서 임의 앱을 자유롭게 조작할 수 있어야 한다. GPT-4 12.24% vs 인간 72.36%의 60%p 격차가 문제의 미해결 상태를 보여준다. |
| **Limitation** | (1) 369개 태스크, Ubuntu 위주. (2) VM이 실제 호스트 OS와 다를 수 있음. (3) 주석자가 CS 전공 한정. (4) 평가 오류 완전 제거 불가. |

---

## Method

### 1. 환경 인프라
VirtualBox/VMware VM 위에서 Ubuntu/Windows/macOS 실행. POMDP `(S, O, A, T, R)` 형식화. 에이전트는 관찰 `o_t`를 받아 pyautogui 액션 `a_t` 생성. 최대 15스텝.

### 2. 관찰 공간
- 스크린샷 (1920×1080), 접근성 트리(a11y tree), Screenshot+a11y, Set-of-Mark(SoM)

### 3. 액션 공간
pyautogui: click, write, hotkey, scroll, dragTo + DONE/FAIL/WAIT 특수 액션

### 4. 실행 기반 평가
134개 고유 평가 함수. getter→evaluator 구조. 동적 크롤러로 실시간 기준값 획득.

### 5. 벤치마크 구성
- 9명 CS 학생, ~1,800 man-hours, 369개 태스크
- 8개 앱: Chrome, VLC, Thunderbird, VS Code, LibreOffice Calc/Writer/Impress, GIMP
- 기존 벤치마크 84개 통합 (22.8%)

---

## Key Contribution

1. **최초의 범용 실제 OS 에이전트 벤치마크**: 시뮬레이션 아닌 실제 VM 기반
2. **134개 실행 기반 평가 함수**: 복잡하고 다양한 태스크 신뢰성 있게 평가
3. **GUI 그라운딩 병목 발견**: 550개 실패 중 75%+가 클릭 좌표 오차
4. **멀티앱 워크플로우 도전**: 단일 앱 13.74% vs 멀티앱 6.57%

---

## Experiment & Results

| 모델 | 입력 | 전체 SR |
|------|------|---------|
| 인간 | - | **72.36%** |
| GPT-4 | a11y tree | **12.24%** |
| GPT-4V | a11y+Screenshot | 12.17% |
| GPT-4o | a11y tree | 11.36% |
| GPT-4V | Screenshot only | 5.26% |
| CogAgent | SoM | 0.99% |

- **인간 완료 시간**: 중앙값 111.94초 (WebArena 35초의 3배)
- **멀티앱**: GPT-4o 7.56% vs 인간 73.27%
- **난이도별**: Easy 16.78%, Medium 13.12%, Hard 4.59%
- **UI 교란**: 창 위치 변경 시 성공률 60~80% 하락
- **에러 분석**: 75%+ GUI 그라운딩 실패 (마우스 좌표 오차)
