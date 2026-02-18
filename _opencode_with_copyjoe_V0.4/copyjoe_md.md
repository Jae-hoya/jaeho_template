Copyjoe(카피조)

카피조: 마케팅에서 고객의 행동을 이끌어내기 위해 쓰는 모든 설득 문장.
고객이 ‘행동’하도록 만드는 것

# 카피조
- 고객의 행동을 이끌어내기 위해 쓰는 모든 설득 문장 생성
- 스토리보드용 콘치 토안 자동 생성

- RAG를 받아서 사용할 수도 있음
    - RAG로 데이터를 받아서 카피 아이디어를 제공
    - file upload로 받아서 사용할 수도 있음

- 카피의 목적
    - 브랜드를 기억하게 하기
    - 제품을 클릭하게 하기
    - 장바구니에 담게 하기
    - 상담을 신청하게 하기

-  좋은 카피의 특징
    - 고객의 언어를 쓴다
    - 길지 않다
    - 구체적이다
    - 감정을 건드린다
    - 차별점이 명확하다

- 카피의 유형
    - 슬로건형 카피(브랜드 이미지를 각인시키는 문장)
    - 문제 해결형 카피(고객의 고민을 건드리는 방식)
    - 혜택 강조형 카피(결과를 먼저 보여주는 방식)
    - CTA형 카피(행동을 직접적으로 요구)

## 필수 기능 요소
- 복사 버튼 동작
- 작업물에 대해서는 word로 export하는 기능이 있어야함
- 이미지 파일, document(docx, doc, ppt, pdf)파일등을 업로드 할 수 있어야 함
- 업로드 된 파일에 대해서 문서변환 엔진은 docling사용
- 임베딩 모델에 대해서는 qwen3-embedding
- vector db는 milvus
- 웹 서치 모드시 tavily사용하고, 이 창 선택이 있어야함
- 카피 스타일을 head, body, cta, slogan, sns, desciprtion등으로 설정하게 해야함.




## 필수/권장 라이브러리
- 백엔드(Python 권장): fastapi, uvicorn, pydantic, python-multipart (업로드/추론 API)
- RAG 파이프라인: langchain, langgraph, langchain-ollama langfuse
- 문서 변환/파싱: docling (요구사항 충족), 이미지 OCR 필요시 pillow(+ 필요 시 OCR 엔진)
- 임베딩/벡터DB: qwen3-embedding(Ollama/서빙 방식에 맞춤), pymilvus, langchain-milvus
- 모델: 추가 다운로드 예정 (qwen3-vl:32b, qwen3-vl:8b gpt-oss)
- 웹서치: tavily-python 
- Word 내보내기: python-docx (서버에서 .docx 생성 후 다운로드)
- 프론트(Vue3): vue, vue-router, vue-i18n, typescript, vite-svg-loader, 추가로 axios(API 통신), pinia(상태관리 권장)

## 프론트 구성
- copyjoe안에,
    - sections
        - PromptSection.vue
        - GenerationSection.vue
    
    - models-service
        - type.js
        - service.js
        - WebAgentSercice.ts
    
    - Components
        - PromptOption.vue
        - LoadingSpinner.vue
        - GenerateResult.vue
        - ExportDialog.vue

IndexPage.vue (메인화면)


