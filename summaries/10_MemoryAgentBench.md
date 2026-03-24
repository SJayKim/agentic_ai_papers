# MemoryAgentBench: Evaluating Memory in LLM Agents

> Hu et al., "Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions"
> ICLR 2026 / arXiv:2507.05257v3 (2026-03-17)
> UC San Diego (Yuanzhe Hu, Yu Wang, Julian McAuley)

---

## 필수 요소

| 항목 | 내용 |
|------|------|
| **Problem** | LLM 에이전트 평가 벤치마크들이 추론·계획·실행 능력에만 집중하고, **메모리(기억·갱신·검색)** 능력을 체계적으로 평가하는 통합 벤치마크가 존재하지 않는다. 기존 장문 맥락 벤치마크(LongBench ~20K, ∞-Bench ~150K 등)는 전체 문서를 한 번에 제공하는 **정적(static) 설정**이어서, 정보를 점진적으로 누적하는 실제 메모리 에이전트의 동작 방식을 반영하지 못한다. LongMemEval은 대화 분할 방식을 시도했으나 주제 다양성이 제한적이고 비현실적인 상호작용 패턴을 지닌다. 무엇보다 기존 벤치마크 중 **네 가지 핵심 메모리 역량을 동시에 포괄하는** 것이 없다. |
| **Motivation** | 메모리 에이전트(MemGPT, Mem0, MIRIX 등)는 상업적으로 빠르게 확산되고 있으나 실제 메모리 품질은 일화적으로만 평가된다. 메모리는 단순한 긴 컨텍스트가 아니라 **압축·추상화·선택적 저장**이라는 별개의 능력을 요구한다. 예를 들어, RAG 시스템은 부분 정보만 검색하므로 전체적 이해나 지식 갱신이 필요한 태스크에서 실패한다. 인지과학과 기억 과학의 이론(James 1890, McClelland et al. 1995, Wimber et al. 2015)에 기반한 4가지 역량 정의를 통해 메모리 에이전트에 무엇이 부족한지를 규명할 필요가 있다. |
| **Method** | **MemoryAgentBench**: 기존 장문 데이터셋을 멀티턴 청크 형식으로 재구성하고, 2개의 신규 데이터셋(EventQA, FactConsolidation)을 추가해 4가지 메모리 역량을 평가하는 통합 벤치마크. **(1) 데이터셋 구성**: 모든 데이터를 `c₁, c₂, …, cₙ` (청크) + `q₁, …, qₘ` (질문) + `a₁, …, aₘ` (정답) 형식으로 표준화. 각 청크는 "Please memorize it…" 지시문과 함께 에이전트에 순차 투입. **(2) 4가지 역량별 데이터셋**: Accurate Retrieval(SH-Doc QA 197K, MH-Doc QA 421K, LongMemEval(S*) 355K, EventQA 534K), Test-Time Learning(BANKING77·CLINC150·NLU·TREC 5종 103K, Movie Recommendation 1.44M), Long-Range Understanding(∞Bench-Sum 172K, Detective QA 124K), Selective Forgetting(FactConsolidation-SH·MH 262K). **(3) 평가 에이전트 3유형**: Long-Context Agents(FIFO 컨텍스트 버퍼), RAG Agents(Simple/Embedding/Structure-Augmented), Agentic Memory Agents(MemGPT, MIRIX 등 반복적 추론 루프). |
| **Key Contribution** | 1) **최초의 4역량 통합 메모리 에이전트 벤치마크**: Accurate Retrieval(AR), Test-Time Learning(TTL), Long-Range Understanding(LRU), Selective Forgetting(SF)를 모두 포괄. 기존 벤치마크는 최대 2개 역량만 커버. 2) **새로운 데이터셋 2종 신설**: EventQA(소설 등장인물 이벤트 순서 추론, 완전 자동화 파이프라인)와 FactConsolidation(MQUAKE 기반 반사실적 편집 쌍으로 선택적 망각 평가, 6K~262K 다중 길이). 3) **점진적 멀티턴 평가 프로토콜**: 정보가 시간 순서로 투입되는 실제 메모리 에이전트 시나리오 재현. 4) **Long-Context, RAG, Agentic Memory 3범주 에이전트 공정 비교** 프레임워크 및 오픈소스 코드베이스 제공. 5) 컨텍스트 깊이 103K~1.44M 토큰, 총 2,071개 질문으로 기존 대비 규모 확장. |
| **Experiment/Results** | **전체 순위**: Long-Context 에이전트가 TTL·LRU에서 우세, RAG 에이전트가 AR에서 우세, **모든 방법론이 SF(특히 멀티홉)에서 심각하게 실패**. 주요 수치(Table 3 Overall Scores): GPT-4o 48.8, Claude-3.7-Sonnet 49.6, GPT-4.1-mini 46.9, Gemini-2.0-Flash 42.4, GPT-4o-mini 42.2~42.3; HippoRAG-v2 41.6, BM25 41.5, MIRIX(4.1-mini) 37.7, Text-Embed-3-Large 38.0; MemGPT 28.3, MIRIX 26.2, Self-RAG 18.7. **SF 멀티홉(FC-MH) 정확도**: 모든 에이전트 최대 7% 이하(대부분 2~5%). 추론 모델(o4-mini)도 6K 컨텍스트에서 FC-MH 80%이나 32K에서 14%로 급락. **TTL 제로샷 검증**: 역사적 예시 없는 제로샷 설정에서 GPT-4o-mini MCC 0.6%, 평균 3.4%에 불과 → 전체 컨텍스트 제공 시 48.6%로 45.2%p 개선, TTL 역량의 유효성 확인. **비용-성능**: MIRIX(GPT-4.1-mini)가 MH-Doc QA에서 $0.016/query로 GPT-4.1-mini Long-Context($0.043)보다 저렴하면서 성능 75.0 vs 66.0으로 우수. |
| **Limitation** | 1) **예산 제약**으로 일부 대표적인 메모리 에이전트만 평가. 향후 더 많은 에이전트 평가 예정. 2) **SF 데이터셋의 합성적 특성**: FactConsolidation은 MQUAKE 반사실 편집 쌍 기반의 합성 데이터로, 실제 자연스러운 forgetting 시나리오와 다를 수 있음(저자들이 의도적 설계임을 명시하며 정당화). 3) **TTL 프로토콜의 단순화**: 완전한 온라인 학습 루프(피드백 기반 메모리 정제) 대신 2단계(획득→평가) 방식으로 단순화. 4) **LRU 태스크의 정보 임계값 효과**: 부분 정보(4K~40K)로는 전체적 이해 불가능, 충분한 컨텍스트(100K+)가 확보될 때만 의미 있는 성능 달성. 5) **상업적 에이전트(MIRIX, Mem0 등)의 극단적 메모리 구성 비용**: MIRIX는 메모리 구성에 최대 29,000초 소요, Mem0·Cognee도 10,000초 이상 요구. |

---

## 선택 요소 (해당되는 것만)

| 항목 | 내용 |
|------|------|
| **Baseline 비교** | **Long-Context Agents**: GPT-4o(Overall 48.8), Claude-3.7-Sonnet(49.6), GPT-4.1-mini(46.9), Gemini-2.0-Flash(42.4), GPT-4o-mini(42.2). AR에서 GPT-4.1-mini 71.8로 최고, TTL에서 Claude-3.7-Sonnet 53.9로 최고, LRU에서 Claude-3.7-Sonnet 62.2로 최고. **Simple RAG**: BM25(41.5) — AR에서 60.5, 적은 비용($0.001 미만)으로 경쟁력 있음. **Embedding RAG**: HippoRAG-v2(41.6)가 최고; Qwen3-Embedding-4B(38.2), Text-Embed-3-Large(38.0), Contriever(29.8). **Structure-Augmented RAG**: MemoRAG(30.9), RAPTOR(27.0), GraphRAG(23.4). **Commercial/Agentic**: MemGPT(28.3), MIRIX(26.2), MIRIX(4.1-mini)(37.7); Mem0(21.1), Zep(24.0), Cognee(20.6). 핵심 격차: Long-Context가 TTL에서 RAG 대비 ~10%p 우세; Selective Forgetting Multi-Hop에서 최강 모델(o4-mini)조차 32K에서 14%에 불과. MIRIX(4.1-mini)는 GPT-4o-mini 대비 cost 절감 + AR 성능 향상을 동시에 달성. |
| **Taxonomy/분류 체계** | **메모리 에이전트 3범주**: (1) Long-Context Agents — 컨텍스트 윈도우를 메모리로 사용, FIFO 방식으로 초과 시 오래된 청크 제거. (2) RAG Agents — 외부 메모리 풀에 저장 후 검색: Simple RAG(BM25 등 키워드), Embedding RAG(밀집 벡터 표현), Structure-Augmented RAG(지식 그래프·계층 트리). (3) Agentic Memory Agents — 반복적 추론-검색-갱신 루프(Self-RAG, MemGPT, MIRIX 등). **4가지 메모리 역량 분류**: AR(정확한 검색, 단일/다중 홉), TTL(테스트 시간 학습, 분류/추천), LRU(장거리 이해, 요약/추론), SF(선택적 망각, 단일/다중 홉 팩트 갱신). **기존 벤치마크 비교 분류 축**: 질문 수(#Q), 컨텍스트 깊이(토큰), 역량 커버리지(AR/TTL/LRU/SF), 평가 대상 에이전트 유형(LCA/RAG/AM). |
