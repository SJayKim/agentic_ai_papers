# HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face

> **논문 정보**: Yongliang Shen, Kaitao Song, Xu Tan, Dongsheng Li, Weiming Lu, Yueting Zhuang (Zhejiang University, Microsoft Research Asia)
> **arXiv**: 2303.17580 (2023.03)
> **코드**: https://github.com/microsoft/JARVIS

---

## Overview

| 항목 | 내용 |
|------|------|
| **Problem** | 다양한 도메인과 모달리티의 복잡한 AI 태스크를 해결하기 위해 수많은 전문 모델이 존재하지만, 개별 모델은 자율적으로 복합 태스크를 처리할 수 없다. LLM은 텍스트 생성에만 제한되어 비전·음성 등 다른 모달리티를 직접 처리하지 못한다. |
| **Motivation** | Hugging Face 같은 ML 커뮤니티에는 수천 개의 특화 모델이 잘 정의된 설명과 함께 존재한다. LLM의 언어 이해·계획·추론 능력을 활용해 이 모델들을 컨트롤러로서 오케스트레이션하면, 언어를 범용 인터페이스로 활용한 AGI 접근이 가능하다. |
| **Limitation** | 저자 언급: 효율성(다수 LLM 호출), 컨텍스트 길이 제한(많은 모델 설명을 담기 어려움), 안정성(LLM의 불확실한 출력 형식). 독자 관점: 모든 단계가 ChatGPT에 의존하여 단일 장애점이 되며, 태스크 계획 오류가 전파됨. 실시간 처리에 부적합한 긴 파이프라인 지연. 모델 선택이 텍스트 설명 매칭에만 의존하여 실제 성능과 괴리 가능. |

---

## Method

1. **4단계 파이프라인**

   **Stage 1 — Task Planning**: ChatGPT가 사용자 요청을 파싱하여 태스크 리스트 생성. 각 태스크는 {task, id, dep, args} 구조. 태스크 간 의존 관계(dep)와 리소스 참조(`<resource>-task_id`)를 명시. 사전 정의된 태스크 카테고리(image-classification, object-detection 등)에서 선택

   **Stage 2 — Model Selection**: 각 태스크에 대해 Hugging Face에서 적합한 전문 모델을 선택. 모델 설명(model card), 다운로드 수, 태스크 카테고리를 기반으로 후보를 필터링하고 ChatGPT가 in-context learning으로 최종 선택

   **Stage 3 — Task Execution**: 선택된 전문 모델이 Hugging Face Inference Endpoints(클라우드) 또는 로컬에서 실행. 태스크 의존 그래프의 위상 정렬에 따라 순차/병렬 실행

   **Stage 4 — Response Generation**: ChatGPT가 모든 전문 모델의 실행 결과를 취합하여 사용자에게 구조화된 요약 응답 생성

2. **언어를 범용 인터페이스로**: 각 AI 모델의 기능을 텍스트 설명으로 요약하고, LLM이 이 설명을 읽고 적절한 모델을 선택·배포하는 패러다임

3. **리소스 의존 관리**: `<resource>-task_id` 태그로 태스크 간 데이터 흐름을 추적. 이전 태스크의 출력(이미지, 텍스트, 오디오 등)을 후속 태스크의 입력으로 자동 연결

---

## Key Contribution

1. **LLM-as-Controller 패러다임 최초 제안**: ChatGPT를 컨트롤러로, Hugging Face 모델들을 실행자로 배치하여 멀티모달·멀티도메인 AI 태스크를 자율적으로 해결하는 선구적 아키텍처
2. **오픈 협업 생태계 활용**: ML 커뮤니티의 기존 특화 모델을 프롬프트 변경 없이 지속적으로 통합 가능한 유연한 모델 선택 메커니즘
3. **태스크 계획의 중요성 제기**: LLM의 태스크 분해·모델 선택 능력을 정량적으로 평가하는 실험적 프레임워크 제시

---

## Experiment & Results

- **평가 태스크**: 언어(QA, 감성분석), 비전(이미지 분류, 객체 탐지, 이미지 생성), 음성(ASR, TTS), 크로스모달(이미지 캡셔닝, 비주얼 QA, 포즈→이미지)
- **기반 모델**: ChatGPT (GPT-3.5/GPT-4) as controller
- **전문 모델**: Hugging Face Hub에서 도메인별 top 모델 사용

**태스크 계획 평가**:
- GPT-4: 태스크 분해 정확도 F1 76.7%, 성공률(복합 태스크) 높은 수준
- GPT-3.5: 상대적으로 낮지만 단일 태스크에서는 안정적

**모델 선택 정확도**: ChatGPT가 모델 설명 기반으로 적합한 모델을 선택하는 정확도 높음. 다운로드 수 기반 랭킹과 결합 시 효과적

**종합 평가**: 이미지 분류+캡셔닝+객체탐지 복합 태스크, 포즈 추출→이미지 생성→TTS 체인 등 다단계 멀티모달 태스크를 자율적으로 완수. 단일 모델 대비 멀티모달 커버리지가 압도적으로 넓음

**한계**: 실행 시간이 길고(다수 API 호출), 컨텍스트 길이 제한으로 30개 이상 모델 후보를 동시에 고려하기 어려움
