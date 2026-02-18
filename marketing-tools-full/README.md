# Marketing Tools Suite

마케팅 카피 생성, 듀얼 AI 채팅, 브리프 분석을 위한 도구 모음

## 프로젝트 구조

```
marketing-tools/
├── backend/                    # FastAPI + LangChain 백엔드
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config.py               # 설정
│   ├── requirements.txt        # Python 의존성
│   ├── .env.example            # 환경변수 예시
│   └── agents/                 # LangChain 에이전트
│       ├── __init__.py
│       ├── copyjoe_agent.py    # 카피 생성 에이전트
│       ├── chenius_chat_agent.py   # 듀얼 채팅 에이전트
│       └── brief_reader_agent.py   # 브리프 분석 에이전트
│
└── frontend/                   # Vue 3 프론트엔드
    ├── src/
    │   ├── App.vue
    │   ├── main.js
    │   ├── style.css
    │   ├── components/
    │   │   ├── CopyjoeTab.vue
    │   │   ├── CheniusChatTab.vue
    │   │   └── BriefReaderTab.vue
    │   └── composables/
    │       └── useApi.js
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

## 기능

### 1. 카피조 (Copyjoe)
마케팅 카피 생성 도구

- **4가지 카피 유형**
  - 슬로건형: 브랜드 이미지 각인
  - 문제 해결형: 고객 고민 건드리기
  - 혜택 강조형: 결과를 먼저 보여주기
  - CTA형: 행동 직접 요구

- **입력 정보**
  - 브랜드/제품명
  - 타겟 고객
  - 핵심 혜택
  - 고객 문제/고민
  - RAG 파일 (선택)

### 2. Chenius Chat
듀얼 AI 채팅 도구

- **두 가지 관점 동시 생성**
  - 🎨 창의적 관점: 대담하고 트렌디한 아이디어
  - 📊 실용적 관점: 검증된 방법론 기반

- **Best 선택 기능**
  - 원하는 응답 선택
  - 선택된 응답으로 대화 이어가기

### 3. Brief Reader
클라이언트 브리프 분석 도구

- **자동 추출 정보**
  - 회사명, 제품/서비스
  - 타겟 고객
  - 해결 문제, 차별점 (USP)
  - 목표, 키워드
  - 전략적 인사이트

## 설치 및 실행

### 백엔드

```bash
cd backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY 입력

# 서버 실행
python main.py
# 또는
uvicorn main:app --reload --port 8000
```

### 프론트엔드

```bash
cd frontend

# 의존성 설치
npm install

# 환경변수 설정 (선택)
echo "VITE_API_URL=http://localhost:8000" > .env

# 개발 서버 실행
npm run dev
```

## API 엔드포인트

### Copyjoe
- `POST /api/copyjoe/generate` - 카피 생성
- `POST /api/copyjoe/upload-rag` - RAG 파일 업로드

### Chenius Chat
- `POST /api/chenius/chat` - 듀얼 AI 채팅

### Brief Reader
- `POST /api/brief/analyze` - 브리프 분석
- `POST /api/brief/upload` - 브리프 파일 업로드

## 기술 스택

### 백엔드
- FastAPI
- LangChain
- langchain-anthropic
- Pydantic

### 프론트엔드
- Vue 3 (Composition API)
- Vite
- Tailwind CSS
- lucide-vue-next

## 환경 변수

### 백엔드 (.env)
```
ANTHROPIC_API_KEY=your-api-key
HOST=0.0.0.0
PORT=8000
DEBUG=true
DEFAULT_MODEL=claude-sonnet-4-20250514
```

### 프론트엔드 (.env)
```
VITE_API_URL=http://localhost:8000
```

## 라이선스

MIT
