# SWE-bench: Can Language Models Resolve Real-World GitHub Issues?

> **논문 정보**: Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik Narasimhan (Princeton University, University of Chicago)
> **arXiv**: 2310.06770 (2023.10) | **학회**: ICLR 2024 Oral
> **코드**: https://swebench.com

---

## Problem

기존 코딩 벤치마크(HumanEval, APPS, MBPP 등)는 자기 완결적인 짧은 코드 스니펫 생성에 초점을 맞추고 있어, 실세계 소프트웨어 엔지니어링의 복잡성을 전혀 반영하지 못한다.
현실의 버그 수정과 기능 구현은 수천 개의 파일로 구성된 대규모 레포지토리를 탐색하고, 여러 파일에 걸친 함수 간 상호작용을 이해하며, 실행 환경과 반복적으로 상호작용해야 하는 작업이다.
평균 438K 라인의 코드베이스에서 32.8 라인짜리 패치를 정확히 만들기 위해서는 문제 위치 식별(localization)과 정교한 추론이 동시에 필요하지만 기존 벤치마크는 이런 능력을 측정하지 못한다.
또한 Dynabench, HELM 류의 "potpourri" 벤치마크들은 각 태스크가 너무 협소하여 모델의 versatility를 측정하지 못하고, 성능이 포화(saturated)되어 최신 LM의 frontier를 드러내지 못한다.
LM이 실제로 상용 코딩 어시스턴트로 배포되고 있음에도 불구하고, 실세계 엔지니어링 워크플로를 반영하는 평가 체계가 부재하다.
결과적으로 모델 개발의 방향성을 가이드할 수 있는, 쉽게 검증 가능하면서도 충분히 어려운 실세계 기반 벤치마크가 시급히 필요한 상황이다.

---

## Motivation

GitHub의 이슈(issue)와 이를 해결하는 merged pull request(PR) 쌍은 실세계 소프트웨어 엔지니어링 워크플로를 자연스럽게 포착하는 풍부한 데이터 소스이다.
각 이슈-PR 쌍은 자연어 버그 리포트 또는 기능 요청, 이를 해결하는 코드 수정, 그리고 수정의 정확성을 자동 검증하는 단위 테스트를 모두 포함한다.
이러한 구조는 "어렵지만 자동으로 검증 가능하다"는 좋은 벤치마크의 두 조건을 동시에 만족시킨다 (Martínez-Plumed et al., 2021).
더불어 GitHub는 지속적으로 새로운 이슈가 생성되므로, 모델의 학습 컷오프 이후 데이터로 재평가가 가능하여 데이터 오염(contamination) 문제를 완화할 수 있다.
인기 Python 레포는 잘 유지보수되고 기여 가이드라인과 테스트 커버리지가 견고하여, 고품질 태스크 수집에 적합하다.
Python 생태계의 12개 대표 레포(django, scikit-learn, sympy, matplotlib 등)만으로도 약 9만 개의 PR을 수집할 수 있어 대규모 벤치마크 구축이 실현 가능하다.
실행 기반(execution-based) 평가는 레포의 실제 테스트 프레임워크를 활용하므로, 수작업 참조 답안 없이도 정확성을 신뢰할 수 있게 판정할 수 있다.

---

## Method

1. **3단계 구축 파이프라인 — Stage I 레포 선정**: 90% 이상 Python 코드로 이루어진 12개 인기 오픈소스 레포(astropy, django, flask, matplotlib, pylint, pytest, requests, scikit-learn, seaborn, sphinx, sympy, xarray)를 선정하고 약 90,000개의 PR을 스크래핑한다.
2. **Stage II 속성 기반 필터링**: merged 상태의 PR 중 (1) GitHub 이슈를 명시적으로 해결(resolve/close/fix)하고 (2) 테스트 파일 변경을 포함하는 PR만 유지하여, 이슈가 실제로 해결되었고 사용자가 검증 테스트를 기여했음을 보장한다.
3. **Stage III 실행 기반 필터링**: PR의 테스트 변경분만 먼저 코드베이스에 적용한 뒤 레포가 정상 install/test 되는지 확인하고, 이어서 PR의 코드 변경을 적용했을 때 최소 1개 이상의 테스트 상태가 fail → pass로 전환되는 인스턴스만 남긴다.
4. **태스크 입력·출력 정의**: 입력은 이슈 텍스트 + 코드베이스 스냅샷(평균 3,010개 non-test 파일, 438K 라인), 출력은 unix `patch` 포맷의 diff 파일이며, 모델은 이 diff를 생성해 코드베이스를 수정해야 한다.
5. **평가 프로토콜**: 생성된 patch를 unix `patch` 프로그램으로 적용 → 성공하면 레포의 unit/system 테스트 실행 → 모든 fail-to-pass 테스트가 통과하고 기존 pass-to-pass 테스트가 회귀하지 않으면 "Resolved"로 판정하며, 최종 메트릭은 전체 인스턴스 대비 Resolved 비율(% Resolved)이다.
6. **BM25 Sparse Retrieval**: Dense retrieval은 긴 코드 문서에 부적합하므로, 이슈 텍스트를 질의로 삼아 BM25로 레포 파일을 랭킹한 뒤 13k/27k/50k 토큰 한도에 맞춰 상위 파일을 컨텍스트로 삽입한다.
7. **Oracle Retrieval**: 분석용 상한선 설정을 위해, 참조 PR이 실제로 수정한 파일들만 컨텍스트로 제공하는 설정을 추가로 정의한다 — 현실적이진 않지만 retrieval 품질이 완벽할 때의 성능을 측정한다.
8. **Oracle-Collapsed Retrieval**: 참조 파일에서 실제 수정된 라인의 ±15줄 버퍼만 남기고 나머지 코드는 축약(collapse)하여, 정확한 위치 단서를 제공했을 때의 성능 상한을 측정한다.
9. **입력 포맷 구성**: 태스크 지시문 + 이슈 텍스트 + retrieved 파일 + 문서 + 예시 patch file + 생성 프롬프트 순으로 조합하며, 모델은 patch 파일 형식으로 응답하도록 few-shot 유도된다.
10. **SWE-bench Lite 서브셋**: 300개 인스턴스를 샘플링하여 functional bug fix 위주로 자기 완결성이 높은 평가 세트를 추가 공개하고, 원본 12개 중 11개 레포를 유사한 분포로 커버한다.
11. **SWE-bench-train 수집**: 평가 레포와 완전히 disjoint한 37개 추가 Python 레포에서 19,000개 이슈-PR 쌍을 수집하며, 이 셋에서는 테스트 변경 요건을 제거해 학습 데이터 규모를 확보한다.
12. **SWE-Llama fine-tuning**: CodeLlama-Python 7B·13B를 기반으로 LoRA를 통해 attention 서브레이어 가중치만 fine-tune하며, 30,000토큰을 초과하는 시퀀스는 제외하여 실질적으로 약 10,000개 인스턴스로 학습한다.
13. **학습 입력 구성**: 지시문 + 이슈 텍스트 + oracle retrieval 파일(gold-edited files)을 프롬프트로 제공하고, 출력 target은 gold patch의 diff 문자열로 두어 모델이 patch 포맷 자체를 습득하도록 유도한다.
14. **평가 모델 세트**: ChatGPT-3.5(16k), GPT-4-32k, GPT-4-turbo(128k), Claude 2(100k), Claude 3 Opus, SWE-Llama 7B/13B(100k+)를 비교하되, 각 모델에 대해 허용 가능한 최대 BM25 컨텍스트 길이 중 best 성능을 보고한다.
15. **Apply Rate와 Resolved Rate의 분리 집계**: 패치 포맷 오류(malformed diff) 때문에 `patch` 적용 자체가 실패하는 경우를 "% Apply"로 별도 측정해, 포맷 적합성 문제와 논리적 해결 실패를 구분한다.

---

## Key Contribution

1. **실세계 SE 벤치마크의 사실상 표준 확립**: 12개 Python 레포에서 수집한 2,294개 실제 GitHub 이슈-PR 쌍으로 구성되어, Devin, SWE-agent, Cursor, Claude Code, OpenHands 등 이후 등장한 코딩 에이전트들의 사실상 표준 평가 기준점이 되었다.
2. **자동화 가능한 실행 기반 검증 파이프라인**: 수작업 레이블링 없이 레포의 기존 테스트 스위트만으로 패치 정확성을 자동 검증하는 방법론을 정립하여, 벤치마크가 지속적으로 확장·갱신될 수 있는 기반을 마련했다.
3. **Continual Update 메커니즘**: 3단계 필터링 파이프라인이 완전 자동화되어 있어, 최신 PR을 추가해 학습 컷오프 이후 데이터로 평가하는 시간적 데이터 오염 회피 프로토콜을 실현했다.
4. **Retrieval의 중요성 실증**: BM25 vs Oracle vs Oracle-Collapsed 세 설정을 체계적으로 비교하여, 컨텍스트 품질이 최종 해결률에 미치는 영향(Claude 3 Opus 기준 3.79% → 9.39%)을 정량화했다.
5. **SWE-Llama 공개**: 100,000 토큰 이상을 처리할 수 있는 오픈소스 리포지토리 편집 특화 모델(CodeLlama 기반 7B·13B + LoRA)과 19,000개 학습 데이터를 공개하여 오픈 모델 연구 토대를 제공했다.
6. **롱 컨텍스트 한계의 실증적 증명**: 컨텍스트 길이가 증가할수록 성능이 오히려 하락한다는 counterintuitive한 현상("Lost in the middle"의 코딩 버전)을 코딩 태스크에서 최초로 정량화했다.
7. **SWE-bench Lite 서브셋 제공**: 300개의 자기 완결적 functional bug fix 문제로 구성된 경량 서브셋을 릴리스하여, 제한된 컴퓨팅 자원으로도 빠른 반복 실험이 가능하도록 했다.

---

## Experiment & Results

**데이터셋 스케일**: 전체 **2,294개** 인스턴스, 평균 이슈 텍스트 **195.1 단어**(최대 4,477 단어), 코드베이스 평균 **3,010개 non-test 파일** / **438K 라인**(최대 886K 라인), gold patch 평균 **32.8 라인** 편집 / **1.7개 파일** / **3.0개 함수**(최대 5,888 라인·31 파일·36 함수).
**테스트 스케일**: 인스턴스당 fail-to-pass 테스트 평균 **9.1개**(최대 1,633개), 총 실행 테스트 평균 **120.8개**(최대 9,459개), 40% 인스턴스는 fail-to-pass 테스트가 2개 이상이며 pass-to-pass 테스트 중앙값은 **51개**이다.
**BM25 메인 결과 (% Resolved / % Apply)**: Claude 3 Opus **3.79% / 46.56%**, Claude 2 **1.97% / 43.07%**, GPT-4-turbo **1.31% / 26.90%**, ChatGPT-3.5 **0.17% / 26.33%**, SWE-Llama 7B **0.70% / 51.74%**, SWE-Llama 13B **0.70% / 53.62%**.
**SWE-bench Lite 결과**: Claude 3 Opus 4.33% / 51.67%, Claude 2 3.00% / 33.00%, SWE-Llama 7B 1.33% / 38.00% — Lite에서 모든 모델이 약간 높은 resolve rate를 보인다.
**Oracle Retrieval (Appendix Table 18)**: Claude 2가 **4.8%**까지 상승(BM25 1.97% 대비 약 2.4배), 이는 retrieval 품질이 성능 결정의 핵심 bottleneck임을 보여준다.
**Oracle-Collapsed 결과**: Claude 3 Opus **9.39%**, Claude 2 **5.93%**, GPT-4 **3.40%**, ChatGPT-3.5 **1.09%** — 정확한 위치 단서 제공 시 모든 모델이 유의미하게 향상(GPT-4는 1.3% → 3.4%로 2.6배 상승).
**컨텍스트 길이 효과**: Claude 2의 BM25 최대 컨텍스트별 resolve rate는 **13k 1.96% / 27k 1.87% / 50k 1.22%**로, 컨텍스트가 길어질수록 성능이 **오히려 하락**한다.
**BM25 Recall**: 13k에서 oracle 파일 전체 포함 비율 26.09% / 평균 29.58%, 27k에서 39.83% / 44.41%, 50k에서 45.90% / 51.06% — 27k에서도 약 절반의 인스턴스에서 oracle 파일 중 하나도 포함하지 못한다.
**패치 길이 분석**: Claude 2 생성 패치는 평균 **19.6 라인**(gold 44.1), SWE-Llama 13B는 **17.6 라인**(gold 37.8), ChatGPT-3.5는 **30.1 라인**(gold 39.6)으로 모든 모델이 gold 대비 절반 수준의 짧고 단순한 편집을 생성한다.
**시간적 오염 검증**: 2023년 전/후 PR로 분할한 oracle 실험에서 Claude 2는 **4.87% → 4.23%**, SWE-Llama 13B는 **3.98% → 3.85%**로 큰 차이가 없어, 모델들이 최신 레포 버전을 단순 암기해 "치트"하지 않음을 확인했다.
**패치 vs 전체 파일 생성**: Claude 2가 whole-file 재생성 시 **2.2%**로 patch 생성(4.8%)의 절반 이하 성능을 보여, 간결한 diff 포맷이 편집 태스크에 더 적합함을 실증했다.
**Fine-tuned 모델의 context shift 민감도**: SWE-Llama는 oracle 컨텍스트로 학습되어 제공된 모든 파일을 수정하려 하는 경향이 있으며, BM25처럼 관련 없는 파일이 섞인 컨텍스트에서 **% Apply는 53.62%로 가장 높지만 % Resolved는 0.70%**에 머물러 포맷 학습과 문제 해결이 분리되어 있음을 보여준다.
**질적 분석**: 11개 샘플 분석 결과 모델들은 원시적인 Python 코드를 생성하고, 기존 third-party 라이브러리나 codebase 재사용 없이 "greedy"하게 문제만 해결하려 하며, gold patch처럼 codebase 전반의 구조적 개선이나 미래 이슈 예방은 거의 시도하지 않는다.
**후속 발전 궤적**: 이 논문 발표 직후 SWE-agent가 **12.29%**, Devin이 **13.86%**를 기록했고, 2024년 말~2025년에는 Claude 3.5 Sonnet 기반 에이전트들이 **50%+**를 돌파하며 벤치마크가 에이전틱 발전의 주요 동력이 되었다.

---

## Limitation

Python 단일 언어에만 한정되어 있어 JavaScript, Java, C++, Go 등 타 언어 생태계의 소프트웨어 엔지니어링 특성을 반영하지 못하며, 향후 다중 언어 확장이 필요하다.
실행 기반(execution-based) 평가만으로는 코드의 효율성, 가독성, 스타일 일관성, 유지보수성 같은 human-judged 품질을 보장할 수 없으며, 테스트를 통과하는 저품질 패치가 통과될 위험이 있다.
12개 레포가 모두 인기 PyPI 패키지로 선정되어 popularity-based 편향이 존재하며, 소규모 또는 신규 프로젝트 특유의 노이즈·문서 부족 상황은 반영되지 않는다.
이슈 텍스트에 embedded image(![image](...))가 포함된 인스턴스가 matplotlib에서 32%, seaborn에서 10%에 달하지만 본 평가에서는 멀티모달 처리가 불가능하여 이미지 정보를 활용할 수 없다.
Oracle retrieval은 현실적이지 않고(엔지니어는 수정할 파일을 사전에 모름), 심지어 수정된 파일만으로는 cross-file 종속성을 모두 이해하기 부족할 수 있어 상한선 자체가 불완전하다.
본 논문의 실험은 retrieval + single-turn patch generation이라는 가장 단순한 baseline에 국한되며, agent-based 접근, tool-augmented LM, 반복적 실행 피드백 등 future methodology는 적극적으로 탐구되지 않는다.
Cutoff가 모호한 사전학습 데이터로 인해 일부 레포의 특정 커밋이 학습 코퍼스에 존재할 가능성이 있으며, 본 논문의 pre/post-2023 분할 실험만으로는 완전한 오염 회피가 보장되지 않는다.
