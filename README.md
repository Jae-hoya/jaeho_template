# Agentic RAG System

다중 에이전트 기반 RAG 시스템 - SPRI AI Brief 문서와 웹 검색을 활용한 지능형 질의응답

## 🚀 Streamlit 배포

### 로컬 실행
```bash
# Poetry 사용
poetry install
poetry run streamlit run RAG_strategies/Agentic_RAG/fast_main.py

# 또는 pip 사용
pip install -r requirements_streamlit.txt
streamlit run RAG_strategies/Agentic_RAG/fast_main.py
```

### Streamlit Cloud 배포
1. GitHub에 레포지토리 푸시
2. [Streamlit Cloud](https://share.streamlit.io/)에서 앱 생성
3. 환경 변수 설정:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `LANGSMITH_API_KEY`
   - `LANGSMITH_PROJECT`

### 환경 변수 설정
`.env` 파일 또는 Streamlit Secrets에 다음 변수들을 설정하세요:
```bash
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=Agentic RAG System
```

## 📦 의존성 관리

### pip 사용
```bash
pip install -r requirements_streamlit.txt
```



## 📁 프로젝트 구조

```
├── RAG_strategies/
│   └── Agentic_RAG/
│       ├── fast_main.py          # Streamlit 메인 앱
│       ├── streamlit_wrapper.py  # Streamlit 래퍼
│       └── .streamlit/
│           ├── config.toml       # Streamlit 설정
│           └── secrets.toml      # 시크릿 설정
├── pyproject.toml                 # Poetry 설정
├── requirements_streamlit.txt    # Streamlit 배포용 의존성
└── README.md
```

## 🔧 주요 기능

- 📚 **SPRI 문서 검색**: AI Brief 문서를 활용한 전문적인 질의응답
- 🔍 **웹 검색**: 실시간 웹 정보 검색 및 분석
- 📊 **차트 생성**: 데이터 시각화 및 분석
- 💭 **일반 대화**: 자연스러운 대화형 AI 인터페이스
- 🤖 **다중 에이전트**: 전문적인 작업을 위한 에이전트 시스템

## 📝 라이선스

MIT License
