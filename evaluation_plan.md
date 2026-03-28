# 논문 재요약 작업 현황 (2026-03-28)

## 작업 목적
- 기존 71편 요약을 새 6-섹션 포맷(Problem/Motivation/Method/Key Contribution/Experiment/Limitation)으로 전면 재작성
- 각 섹션 독립적으로 충실하게 작성 (전체 80줄+, 수치 5개+)
- Notion 업로드 시 `**bold**` → rich_text bold 변환 필요 (미구현)

## 진행 현황: 23/71편 완료 (32%)

### 완료 (새 포맷으로 재작성됨)
| 배치 | 논문 | 상태 |
|------|------|------|
| 1 | 01_A-MEM, 02_MAGMA, 03_AriGraph | ✅ |
| 2 | 04_MemEvolve, 05_ALMA, 06_ADAS | ✅ |
| 3 | 07_SeCom, 08_MIRIX, 09_Preference-Aware-Memory | ✅ |
| 4 | 10_MemoryAgentBench, 11_Memory-Management-Impact, 12_Privacy-Risks-Memory | ✅ |
| 5 | 13_Memory-Survey, 14_MASS, 15_AgentSquare | ✅ |
| 6 | 16_TurnLevelCredit, 17_SelfReflectiveKG, 18_AgentRefine | ✅ |
| 7 | 19_ACE, 20_ChainOfAgents, 21_EvalLongContext | ✅ |
| 8 | 23_CreativityMAS, 24_TestTimeCompute | ✅ |

### 미완료 (구 포맷 — 재작성 필요)
| 번호 | 논문 | 비고 |
|------|------|------|
| 22 | MultiAgentCollab | API 에러 3회 (서베이 논문) |
| 25 | BUTTON | |
| 26 | ToolACE | |
| 27 | G-Memory | |
| 28 | Evo-Memory | |
| 29 | MemGPT | |
| 30 | DelTA | |
| 31 | Gorilla | |
| 32 | Toolformer | |
| 33 | AOP | |
| 34 | OWL | |
| 35 | HuggingGPT | |
| 36 | ScalingTestTimeCompute | |
| 37 | ThinkingOptimal | |
| 38 | CannotSelfCorrect | |
| 39 | CorrectBench | |
| 40 | RethinkingFineTuning | |
| 41 | GraphRAG | |
| 42 | AgenticRAG-KG | |
| 43 | SUBQRAG | |
| 44 | LightRAG | |
| 45 | MemoryOS | |
| 46 | HippoRAG | |
| 47 | HippoRAG2 | |
| 48 | A-MAC | |
| 49 | ToolLLM | |
| 50 | AvaTaR | |
| 51 | TauBench | |
| 52 | MCPSecurity | |
| 53 | AgentProtocols | |
| 54 | AFlow | |
| 55 | WebRL | |
| 56 | SWE-agent | |
| 57 | EvoAgent | |
| 58 | GPTSwarm | |
| 59 | SCoRe | |
| 60 | SuperCorrect | |
| 61 | S2R | |
| 62 | ThinkOnGraph | |
| 63 | ThinkOnGraph2 | |
| 64 | PlanOnGraph | |
| 65 | AgentBench | |
| 66 | GAIA | |
| 67 | OSWorld | |
| 68 | AgentHarm | |
| 69 | AutoGen | |
| 70 | MetaGPT | |
| 71 | SWE-bench | |

**미완료: 48편** (22번 + 25~71번)

## 작업 방식
- 3편씩 배치 처리 (서브에이전트 3개 병렬 → 메인에서 Write)
- 품질 평가 루프는 속도를 위해 생략 중 (추후 일괄 평가 가능)
- PDF 텍스트는 모든 71편에 대해 추출 완료 (`_text.txt` 존재)

## 참고: Notion 볼드 렌더링 이슈
- 현재 Notion 업로드 시 `**text**`가 리터럴 `**`로 표시됨
- Notion API rich_text에서 `bold: true` annotation으로 변환하는 파싱 로직 필요
- 재요약 완료 후 Notion 업로드 시 함께 수정 예정

## 재개 방법
다음 대화에서 "재요약 이어서 진행해줘" 또는 직접 배치 처리를 이어서 진행.
다음 배치: **22_MultiAgentCollab, 25_BUTTON, 26_ToolACE** 부터 시작.
