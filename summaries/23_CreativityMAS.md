# Creativity in LLM-based Multi-Agent Systems: A Survey

> **논문 정보**: Yi-Cheng Lin, Kang-Chieh Chen, Zhe-Yan Li, Tzu-Heng Wu, Tzu-Hsuan Wu, Kuan-Yu Chen, Hung-yi Lee, Yun-Nung Chen (National Taiwan University)
> **arXiv**: 2505.21116 (2025.05) | **학회**: -
> **코드**: https://github.com/MiuLab/MultiAgent-Survey

---

## Problem

LLM 기반 멀티에이전트 시스템(MAS)은 인간과 AI가 협업하여 아이디어와 산출물을 생성하는 방식을 혁신하고 있다. 기존 서베이들은 MAS의 인프라스트럭처(아키텍처, 통신 프로토콜, 환경/시뮬레이션 플랫폼)에 집중하면서, 창의성(creativity) 차원을 거의 다루지 않았다. 새로운 출력물이 어떻게 생성·평가되는지, 에이전트 페르소나가 창의성에 어떤 영향을 미치는지, 창의적 워크플로우가 어떻게 조율되는지에 대한 체계적 분석이 부재하다. 단일 에이전트 파이프라인은 격리된 환경에서 실행되어 익숙한 패턴에 수렴하는 경향이 있으며, 방대한 개방형 창의 공간을 탐색하는 데 한계가 있다.

---

## Motivation

멀티에이전트 시스템은 비평 루프, 경쟁적 인센티브, 연합 형성 등 다양한 역학을 통해 설계자가 예상하지 못한 창발적(emergent) 결과물을 만들어낼 수 있다. 그러나 에이전트의 proactivity(자율적 주도성)가 높아지면 아이디어 공간이 평탄화되어 동질적 출력을 낳고, 사용자 신뢰와 만족도가 저하되는 트레이드오프가 존재한다. 또한 창의성 평가는 본질적으로 주관적이고 다면적이어서 보편적으로 합의된 평가 프레임워크가 없으며, 객관적 메트릭과 주관적 평가 간 괴리가 크다. 이 서베이는 이러한 공백을 메우기 위해 MAS에서의 창의성에 초점을 맞춘 최초의 체계적 서베이로서, 기법 분류·페르소나 설계·평가 방법론·데이터셋·미래 과제를 통합적으로 제시한다.

---

## Method — 분류 체계 (Taxonomy)

1. **MAS 워크플로우 3단계 분해**: Planning(목표 설정·작업 분할), Process(중간 산출물 생성·에이전트 간 상호작용), Decision Making(산출물 평가·선택).

2. **에이전트 Proactivity 스펙트럼**: initiative(행동 개시 주체)와 control(만족도 판단 주체) 두 축으로 정의하고, reactive에서 proactive까지의 연속 스펙트럼으로 기존 시스템들을 배치.

3. **MAS 창의성 기법 3가지 분류**:
   - **(a) Divergent Exploration**: 각 에이전트에 서로 다른 관점을 부여하여 독립적으로 다양한 창의적 방향을 탐색.
   - **(b) Iterative Refinement**: Proposer·Reviewer·Implementer 등 역할을 분담한 에이전트가 반복적 피드백·수정 사이클을 통해 초안을 정교화.
   - **(c) Collaborative Synthesis**: 다양한 에이전트 관점을 통합하여 일관된 고수준 산출물을 생성.

4. **페르소나 설계 체계화**: Coarse-Grained(역할 라벨만), Medium-Coarse(도메인 지식·도구 추가), Fine-Grained(Big Five 성격 특성·학력 등)로 3단계 분류. 프로파일링은 Human-Defined, Model-Generated, Data-Derived로 구분.

5. **평가 프레임워크 이원화**: 산출물 평가(Artifact Evaluation)와 상호작용 평가(Interaction Evaluation).
   - 객관적 메트릭: Distinct-n, Entropy-n, Self-BLEU, SBERT 코사인 유사도, Semantic Entropy / FID, TIE.
   - 주관적 평가: TTCT(Fluency·Flexibility·Originality·Elaboration), Boden's Criteria, LLM-as-a-judge.
   - 상호작용 평가: Self-Report Instruments(CSI 등), 인터뷰, 연구자 관찰.

6. **미해결 과제 7가지**: Proactivity-Trust 균형, 페르소나 편향, 창의적 갈등 관리, 통합 평가 벤치마크, 저작권 귀속, 자원 효율적 오케스트레이션, 종단적 사용자 연구.

---

## Key Contribution

1. **MAS에서의 창의성을 전담으로 다룬 최초의 서베이**.
2. **에이전트 Proactivity 스펙트럼**: initiative와 control 두 축으로 기존 MAS 프레임워크들을 체계적으로 배치.
3. **창의성 기법의 3대 분류 체계**: Divergent Exploration, Iterative Refinement, Collaborative Synthesis.
4. **페르소나 세분도(Coarse/Medium/Fine) 프레임워크**: 에이전트 프로필 설계가 창의성에 미치는 영향을 분석한 최초의 시도.
5. **텍스트·이미지 양 모달리티에 걸친 평가 메트릭 종합**: 객관적·주관적·상호작용 평가를 포괄하는 다층적 평가 프레임워크.
6. **7가지 핵심 도전과제와 구체적 미래 연구 방향**을 체계적으로 제시.

---

## Experiment & Results — 커버리지 분석

서베이 논문으로 자체 실험 없이 인용된 주요 연구의 핵심 수치를 종합:
- **Co-GPT Ideation**: GPT-3.5와의 공동 아이디어 발상에서 참가자들이 더 다양하고 상세한 아이디어를 생성했으나, 최고 평점 아이디어는 여전히 인간 단독 생성에서 나옴.
- **Long-Term Impact Study**: AI 보조로 단기 성과 향상, 비보조 후속 과제에서 독창성과 다양성이 감소하여 장기 과의존 위험 시사.
- **CollabStory**: 복수 LLM 순차 문단 작성에서 문단 전환의 75% 이상이 일관성 유지.
- **DynTaskMAS**: 비동기 동적 태스크 그래프로 실행 시간 최대 33% 단축, 활용률 35% 향상.
- **MaAS**: 에이전틱 슈퍼넷으로 추론 비용을 정적 시스템 대비 6~45% 수준으로 절감.
- **HoLLMwood**: Writer·Editor·Actor 역할 분담 반복 정제로 단일 LLM 대비 더 풍부한 캐릭터 개발과 높은 서사 일관성 달성.

---

## Limitation

- 텍스트와 이미지에만 집중하여, 오디오·비디오·체화 로보틱스 등 다른 모달리티의 창의적 MAS 도전과제를 다루지 못했다.
- 데이터 라이선싱·저작권, 사용자 프라이버시 등 광범위한 윤리 이슈를 깊이 다루지 않았다.
- 대부분의 검토 시스템이 영어 기반·서구 중심 데이터셋에 의존하며, 다국어/저자원 환경에 대한 분석이 부재.
- 서베이 특성상 제안된 프레임워크의 실증적 검증이 이루어지지 않았다.
- 통합된 벤치마크의 필요성을 지적하면서도, 구체적 벤치마크 구축까지는 나아가지 못했다.
