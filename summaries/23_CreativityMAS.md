# Creativity in LLM-based Multi-Agent Systems: A Survey

> **논문 정보**: Yi-Cheng Lin, Kang-Chieh Chen, Zhe-Yan Li, Tzu-Heng Wu, Tzu-Hsuan Wu, Kuan-Yu Chen, Hung-yi Lee, Yun-Nung Chen (National Taiwan University)
> **arXiv**: 2505.21116 (2025.05) | **학회**: -
> **코드**: https://github.com/MiuLab/MultiAgent-Survey

---

## Problem

LLM 기반 멀티에이전트 시스템(MAS)은 인간과 AI가 협업하여 아이디어·산출물을 생성하는 방식을 근본적으로 변화시키고 있다.

그러나 기존 MAS 서베이들은 아키텍처, 통신 프로토콜, 환경/시뮬레이션 플랫폼 등 인프라 측면에만 집중해왔다.

창의성(creativity) 차원, 즉 새로운 산출물이 어떻게 생성되고 평가되는지, 에이전트 페르소나가 창의성에 어떤 영향을 주는지, 창의 워크플로우가 어떻게 조율되는지에 대한 체계적 분석은 공백 상태이다.

단일 에이전트 파이프라인은 격리된 환경에서 실행되어 익숙한 패턴에 수렴하며, 개방형 창의 공간을 넓게 탐색하는 데 구조적 한계를 가진다.

창의성 평가 자체가 주관적·다면적이어서 보편적으로 합의된 평가 프레임워크가 부재하고, 과제별로 커스텀 메트릭이 난립하는 상황이다.

에이전트의 proactivity(주도성)가 높아지면 아이디어 공간이 평탄화되거나 사용자 신뢰가 훼손되는 트레이드오프도 정량적으로 분석되지 않았다.

페르소나 설계가 편향을 전파시키거나 특정 배경의 관점을 과잉 대표하는 구조적 위험 역시 체계적으로 문서화되지 않았다.

따라서 창의적 MAS의 기법·데이터셋·평가·도전과제를 통합한 로드맵이 긴급히 필요하다.

---

## Motivation

MAS는 비평 루프, 경쟁적 인센티브, 연합 형성 등 다양한 역학을 통해 설계자가 예상하지 못한 창발적(emergent) 결과물을 만들어낼 수 있다.

에이전트마다 서로 다른 관점·프롬프트 스타일·지식 도메인을 부여하면 독립적인 창의 방향 탐색이 가능하여 조기 수렴을 예방한다.

예컨대 HoLLMwood는 Writer·Editor·Actor 역할 분담을 통해 대본 창작에서 단일 LLM 대비 풍부한 캐릭터 전개와 서사 일관성을 달성했다.

그러나 Collaborative Canvas 연구는 AI의 과도한 제안이 토론 중 의견을 평탄화시켜 동질적 출력을 낳는다는 부작용을 실증적으로 보여주었다.

Co-Quest 실험은 에이전트 주도성이 높아질수록 아이디어 양은 증가하지만 사용자 만족도·신뢰는 오히려 하락함을 관찰했다.

또한 정밀성이 중요한 과제(자동 정리 증명 등)에서는 낮은 proactivity가 오히려 신뢰성·책임성을 보장한다는 점이 관찰되었다.

이러한 트레이드오프를 체계적으로 정리하고, 텍스트·이미지 양 모달리티에 걸친 창의성 기법을 분류하는 통합 서베이가 필요한 시점이다.

본 논문은 이 공백을 메우는 최초의 MAS 창의성 전담 서베이로서, 기법·페르소나·평가·데이터셋·미해결 과제를 포괄한다.

---

## Method

1. **MAS 워크플로우 3단계 분해**: Planning(목표 설정·작업 분할), Process(중간 산출물 생성·에이전트 간 상호작용), Decision Making(산출물 평가·선택) 단계로 창의 파이프라인을 구조화.

2. **Proactivity 2축 정의**: initiative(행동 개시 주체)와 control(만족도 판단 주체)을 축으로 설정하여, reactive에서 proactive까지의 연속 스펙트럼을 정의하고 기존 시스템을 좌표 평면에 배치.

3. **Planning 단계 분석**: 대부분 MAS가 인간에게 계획을 위임하지만, Co-Scientist의 supervisory agent나 VirSci의 "team leader" agent처럼 자율 계획을 수행하는 사례를 proactive 극단으로 분류.

4. **Process 단계 분석**: 완전 자율 파이프라인(LLM Discussion처럼 페르소나가 명령을 자동 활성화)부터 human-in-the-loop(Hou et al. 등 단계마다 프롬프트 주입 필요)까지 2차원 평면에 매핑.

5. **Decision Making 단계 분석**: 인간 평가(Scideator), 전담 judge agent(Liang et al. 2024), 손실 기반 자동 선택(CICADA, Drawing with Reframer)을 proactivity 순으로 분류.

6. **3대 창의성 기법 분류**:
   - **Divergent Exploration**: 각 에이전트에 서로 다른 관점을 부여하여 독립적으로 다양한 창의 방향 탐색 (Co-GPT Ideation, Group-AI Brainwriting, ICCRI, Long-Term Impact Study).
   - **Iterative Refinement**: Proposer·Reviewer·Implementer 등 역할 분담으로 피드백·수정 사이클을 반복 (HoLLMwood, DesignGPT, Baby-AIGS-MLer, Multi-agent Debate).
   - **Collaborative Synthesis**: 다양한 에이전트 관점을 통합하여 일관된 고수준 산출물 생성 (MaCTG, CollabStory, Human-AI Co-creativity, CoQuest).

7. **페르소나 Granularity 3단계 체계화**:
   - **Coarse-Grained**: "marketing strategist" 등 역할 라벨만 부여, Solo Performance Prompting이 대표 사례.
   - **Medium-Coarse**: 도메인 지식·도구·기능 추가, HoLLMwood 및 TRIZ Agents가 대표 사례.
   - **Fine-Grained**: Big Five 성격 특성·학력·경력 등 심리측정 프로필 부여, PersonaFlow가 대표 사례.

8. **Agent Profiling Paradigm 3분류**: Human-Defined(수동 설계), Model-Generated(LLM 자동 생성), Data-Derived(논문·CV 등 실데이터 기반 "digital twin")으로 구분.

9. **Artifact Evaluation — Objective Metrics**: 텍스트용 Distinct-n, Entropy-n, 4-gram repetition rate, Self-BLEU, SBERT 코사인 유사도, Semantic Entropy; 이미지용 FID, Truncated Inception Entropy(TIE).

10. **Artifact Evaluation — Subjective Metrics**: TTCT(Fluency·Flexibility·Originality·Elaboration 4차원), Boden's Criteria, Creative Product Semantic Scale(CPSS), Likert 기반 LLM-as-a-judge.

11. **Interaction Evaluation 방법론**: Self-Report Instruments(Creativity Support Index CSI, Mixed-Initiative Creative Support Index MICSI)과 Interviews, Researcher Observation(녹화·로그 분석).

12. **Additional Artifact Criteria**: Helpfulness, Relevance, Clarity, 이미지 도메인 전용 Inspiring 차원 추가.

13. **심리 검사 데이터셋**: Wallach-Kogan Creativity Tests, Alternative Uses Task(AUT), Remote Associates Test(RAT), TTCT 배터리를 MAS 평가에 적응.

14. **Task-Specific 데이터셋**: Chakrabarty et al.의 공동 저작 스토리 코퍼스, AI Idea Bench 2025, Chatbot Arena, Titanic, ProofNet 등 과제별 수집.

15. **7가지 미해결 도전과제 분류**: Proactivity-Trust 균형, 페르소나 편향, 창의적 갈등 관리, 통합 평가 벤치마크, 저작권 귀속, 자원 효율적 오케스트레이션, 종단적 사용자 연구.

---

## Key Contribution

1. **MAS 창의성 전담 최초 서베이**: 기존 인프라 중심 서베이의 공백을 메워 창의성 차원의 기법·페르소나·평가·도전과제를 통합적으로 제시.

2. **Proactivity 2축 스펙트럼**: initiative와 control을 좌표축으로 기존 MAS 프레임워크를 체계적으로 배치하는 새로운 분석 도구 제공.

3. **창의성 기법 3대 분류 체계**: Divergent Exploration, Iterative Refinement, Collaborative Synthesis로 정리하여 후속 연구자가 기법을 대조·선택할 수 있는 공통 어휘 확립.

4. **페르소나 Granularity(Coarse/Medium/Fine) 프레임워크**: 에이전트 프로필 세분도가 창의성·편향·일반화에 미치는 영향을 최초로 체계 분석.

5. **텍스트·이미지 양 모달리티 평가 메트릭 종합**: 객관적·주관적·상호작용 평가를 포괄하는 3계층 평가 프레임워크 제시.

6. **창의성 평가 데이터셋 큐레이션**: 심리 검사 기반과 task-specific 데이터셋을 정리하여 표준화된 평가 기반 마련.

7. **7대 도전과제 로드맵**: 편향, 갈등, 벤치마크 통합, 저작권, 자원 효율, 종단 연구 등 각 과제에 구체적 미래 연구 방향 제시.

---

## Experiment

서베이 논문이므로 자체 실험 대신, 인용된 주요 연구의 정량 결과를 종합한다.

- **Co-GPT Ideation**: 참가자가 GPT-3.5와 공동 발상 시 아이디어 다양성·상세도가 향상되었으나, 최고 평점 아이디어는 여전히 인간 단독 생성에서 나옴.

- **Long-Term Impact Study**: AI 보조 시 단기 성과는 향상되지만, 비보조 후속 과제에서 독창성과 다양성이 하락하여 장기 과의존 위험을 시사.

- **CollabStory**: 복수 LLM 순차 문단 작성 실험에서 GPT-4o 평가 결과 문단 전환의 **75% 이상**이 일관성 유지.

- **DynTaskMAS**: 비동기 동적 태스크 그래프로 실행 시간 최대 **33% 단축**, 활용률 **35% 향상**.

- **MaAS(Agentic Supernet)**: 쿼리별 아키텍처 적응으로 추론 비용을 정적 MAS 대비 **6~45% 수준**으로 절감.

- **Multi-agent Debate(Liang et al. 2024)**: Commonsense Machine Translation과 CIAR 벤치마크에서 단일 LLM 대비 성능 향상.

- **HoLLMwood**: Writer·Editor·Actor 반복 정제로 단일 LLM 대비 더 풍부한 캐릭터 개발과 높은 서사 일관성 달성, Distinct-3·Entropy-3·4-gram 반복률로 정량 측정.

- **ICCRI**: 특수교육 환경 5회 세션에서 로봇 공동 창작 시 세션 S1~S3 동안 창의성 유의 증가, 로봇 제거 후에도 베이스라인 이상 유지되어 창의성 잔류 효과 관찰.

- **DesignGPT**: product manager·materials expert 등 역할 분담으로 one-shot 생성 대비 완결성·참신성·실용성 지표 모두 향상.

- **Baby-AIGS-MLer**: Chatbot Arena·Titanic 벤치마크에서 예측 정확도·일반화 성능 개선.

---

## Limitation

- 텍스트와 이미지 두 모달리티에만 집중하여, 오디오·비디오·체화 로보틱스 등 다른 채널의 창의적 MAS 도전과제는 다루지 않음.

- 데이터 라이선싱·저작권, 사용자 프라이버시, 인간-에이전트 데이터 수집 시 informed consent, 대규모 MAS 배포의 환경 비용 등 광범위한 윤리 이슈를 깊이 다루지 않았다.

- 검토 시스템 대부분이 영어 기반·서구 중심 데이터셋에 의존하여, 다국어·저자원 언어·문화권별 창의 표현·평가 기준의 차이를 포괄하지 못함.

- 서베이 특성상 제안된 Proactivity 스펙트럼·Granularity 체계의 실증적 타당성 검증이 이루어지지 않음.

- 통합 벤치마크 필요성을 강조하면서도 구체적 벤치마크 구축·공개까지는 나아가지 못했다.

- 페르소나 편향 논의에서 젠더 등 특정 차원만 예시로 들었을 뿐, 다차원 편향(인종·계급·문화)을 동시에 다루는 측정 방법론은 제시하지 못함.

- Longitudinal User Study의 필요성을 강조했지만, 서베이 내부에서도 기존 연구의 종단 데이터가 제한적이어서 결론이 잠정적.

- "창의성" 정의 자체가 Wiggins·Boden 전통에 제한되어, 비서구권 창의성 이론(예: 집단주의적 창작관)을 충분히 반영하지 못함.
