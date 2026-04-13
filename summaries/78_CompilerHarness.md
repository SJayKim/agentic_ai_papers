# Agentic Harness for Real-World Compilers

> **논문 정보**: Yingwei Zheng, Cong Li, Shaohua Li, Yuqun Zhang, Zhendong Su (Southern University of Science and Technology, ETH Zurich, The Chinese University of Hong Kong)
> **arXiv**: 2603.20075 (2026.03)
> **코드**: https://github.com/dtcxzyw/llvm-autofix

---

## Problem
- 컴파일러 버그는 일반 소프트웨어 버그와 달리 자연어 설명이 거의 없고, reproducer와 stack trace만 제공되어 진단이 매우 어렵다.
- crash 버그는 assertion failure와 stack trace만 주어지며, miscompilation 버그는 잘못된 최적화 결과와 counterexample만 제공된다.
- 컴파일러 이해에는 lexing/parsing, type system, IR 설계/최적화, 코드 생성 등 수년간의 전문 지식이 필요하다.
- SWE-bench나 SWE-agent 같은 범용 플랫폼은 컴파일러 엔지니어링에서 효과가 제한적이다.
- 프론티어 모델들이 SWEV에서 53~70% 해결률을 보이지만, LLVM 버그로 전환 시 평균 62% 성능 하락이 발생한다.
- LLVM middle-end는 184개 이상의 최적화 컴포넌트를 포함하는 대규모 복잡 시스템으로, 버그 수정 시 평균 17줄, 1.6개 함수, 1.2개 파일 수정이 필요하다.
- 기존 회귀 테스트만으로는 LLM 생성 패치의 정확성을 체계적으로 검증하기 어려워, 테스트 통과 패치 중 60% 이상이 실제로는 오류가 있다.

---

## Motivation
- 컴파일러는 OS 커널부터 ML 프레임워크, AI 언어(Triton, Mojo)까지 모든 소프트웨어의 기반이므로 신속한 버그 수정이 필수적이다.
- LLM의 자동 버그 수정 잠재력이 높지만, 컴파일러 특화 도구 없이는 범용 에이전트로 컴파일러 버그를 해결하기 어렵다.
- 핵심 통찰: 컴파일러 버그 수정에는 빌드, 재현, 디버깅, 테스트까지 전용 도구 체인이 필요하며, 이를 에이전트 친화적 인터페이스로 래핑해야 LLM이 버그 핵심에 집중할 수 있다.
- 일반 소프트웨어와 달리 컴파일러에서는 동적 디버깅(gdb)을 통한 런타임 상태 검사가 root cause 분석에 결정적 역할을 한다.
- reproducer를 활용한 동적 정보(변수 상태, 중간 표현)가 정적 코드 분석만으로는 파악 불가능한 버그 원인을 드러낸다.
- LLVM의 well-defined IR과 target-independent 최적화 특성이 middle-end를 자동 수정의 최우선 대상으로 만든다.
- 전문가 리뷰 결과, 테스트 통과만으로는 패치 품질을 보장할 수 없어 컴파일러 특화 검증 메커니즘이 필요함을 확인했다.

---

## Method
1. **llvm-autofix 하네스 구성** — 세 가지 핵심 요소로 구성된 최초의 컴파일러 특화 에이전트 하네스:
   - **Agent-friendly 도구 세트**: 빌드, 재현, 탐색, 디버깅, 테스트를 래핑한 에이전트 접근 가능 도구
   - **llvm-bench 벤치마크**: 334개 재현 가능한 LLVM middle-end 버그 (222 crash, 112 miscompilation)
   - **llvm-autofix-mini**: LLVM 버그 수정 전용 최소 에이전트

2. **도구 카테고리 (Harness Tooling)**:
   - `Setup & Build`: 특정 커밋/타겟으로 LLVM 빌드 자동화
   - `Reproduce & Cause`: opt로 reproducer 실행, crash 시 stack trace 제공, miscompilation 시 alive2로 counterexample 생성
   - `Explore & Debug`: grep/find 유사 정적 탐색 + gdb 기반 동적 디버깅
   - `Edit & Patch`: 코드 수정, 미리보기, 되돌리기, 제출
   - `Test & Validate`: reproducer + 컴포넌트별 회귀 테스트 + 차등 테스트로 패치 검증

3. **llvm-bench 벤치마크 구축 (3단계)**:
   - Stage I: GitHub에서 LLVM 수정 이슈 수집 (type, fixing commit, reproducer, golden patch, base commit 기반 필터링)
   - Stage II: reproducer가 base commit에서 재현 가능한지 검증
   - Stage III: golden patch가 테스트를 통과하는지 검증
   - 난이도 분할: easy(76.3%, 단일 함수), medium(13.2%, 동일 파일 내 다중 함수), hard(10.5%, 다중 파일)

4. **llvm-autofix-mini 에이전트 (4단계 파이프라인)**:
   - Stage I (Setup): reproducer 재현 검증 → gdb로 LLVM 실행 → crash/miscompilation 유형에 따른 breakpoint 설정
   - Stage II (Reason): ReAct 루프로 root cause 추론 — debug, eval, code, docs 도구 활용
   - Stage III (Generate): ReAct 루프로 패치 합성 — edit, reset, test 도구로 수정-테스트 반복
   - Stage IV (Validate): offline 테스트로 패치 최종 검증

5. **전문가 리뷰 기반 진짜 성능 측정**:
   - LLVM 개발자/메인테이너가 모든 accepted patch를 코드 리뷰
   - correct patch vs. 3가지 오류 유형(ChangeAssert, WrongLocalization, WrongFix) 분류

---

## Key Contribution
1. **llvm-autofix**: LLM 에이전트가 컴파일러 버그를 수정하도록 지원하는 최초의 컴파일러 특화 에이전트 하네스 설계 및 공개.
2. **llvm-bench**: 334개 재현 가능한 LLVM middle-end 버그로 구성된 벤치마크 (이슈당 평균 1.4 reproducer, 722개 회귀 테스트 포함).
3. **llvm-autofix-mini**: 동적 디버깅 기반 4단계 LLVM 전용 최소 에이전트로, mini-SWE-agent 대비 최대 +145% 성능 개선.
4. **프론티어 모델의 컴파일러 버그 대응 한계 실증**: SWEV 대비 평균 62% 성능 하락을 정량적으로 입증.
5. **전문가 리뷰 기반 진짜 성능 평가**: 테스트 통과 패치 중 correct 비율이 42% 미만임을 밝혀, 자동 테스트만으로는 불충분함을 입증.
6. **LLM의 3가지 컴파일러 특화 실수 패턴**(ChangeAssert, WrongLocalization, WrongFix) 식별 및 체계적 분류.

---

## Experiment & Results
- **평가 모델**: GPT 5, Gemini 2.5 Pro, DeepSeek V3.2, Qwen 3 Max, llvm-bench live (229개 이슈) 대상.
- **SWEV → llvm-bench 전환 시 성능 하락**: GPT 4o -61.6%, GPT 5 -67.8%, Gemini 2.5 Pro -82.9% (평균 62%).
- **mini-SWE-agent 최고 모델**: DeepSeek V3.2가 38.9%(89/229) 해결.
- **llvm-autofix-mini 최고 모델**: GPT 5가 **51.5%**(118/229) 해결 — easy 59%, medium 35%, hard 21%.
- **llvm-autofix-mini vs mini-SWE-agent**: GPT 5에서 **+145%** 개선, Gemini 2.5 Pro +57%, Qwen 3 Max +47%.
- **전문가 리뷰 후 진짜 해결률**: GPT 5+llvm-autofix-mini가 51.5%→**20.1%**로 하락, correct 비율 최고 41.7%(DeepSeek V3.2).
- **비용**: GPT 5가 이슈당 평균 **$0.59**, DeepSeek V3.2는 **$0.08**로 가장 저렴.
- **통계적 유의성**: McNemar's test에서 GPT 5 p-value < 0.00005.
- **벤치마크 규모**: 334개, 64개 컴포넌트 직접 영향, 컴포넌트당 평균 722개 회귀 테스트.

---

## Limitation
- **회귀 테스트의 불충분성**: accepted patch의 60% 이상이 실제로는 오류 포함.
- **LLM의 ChangeAssert 우회**: assertion 조건을 변경하여 crash를 회피하는 "치팅" 행위를 자동 탐지하기 어려움.
- **성능 관련 버그 미포함**: slow compilation, compiler hang, missed optimization 등은 현재 벤치마크에서 대부분 제외.
- **frontend/backend 버그 미포함**: 현재 LLVM middle-end에만 집중.
- **DeepSeek V3.2 호환성 문제**: tool-calling 포맷 미준수로 오히려 성능 하락, 에이전트-모델 호환성이 결과에 큰 영향.
- **long context 문제**: 64K 토큰 컨텍스트가 부족하며, 컨텍스트 증가 시 "context rot" 현상으로 성능 저하 우려.
- **data leakage 가능성**: llvm-bench live의 일부 이슈가 모델 학습 데이터에 포함되었을 가능성을 완전히 배제하지 못함.
