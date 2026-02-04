# 빠른 시작 가이드

5분 안에 LangGraph RAG를 실행해보세요!

## 1단계: 클론 및 이동

```bash
git clone <repository-url>
cd LangGraph_RAG
```

## 2단계: 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
nano .env
```

`.env` 파일 내용:
```
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/postgres
```

## 3단계: 의존성 설치

```bash
pip install -r requirements.txt
```

## 4단계: 데이터베이스 설정

### 옵션 A: Docker 사용 (권장)

```bash
# ParadeDB 실행
docker run -d \
  --name langgraph-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=postgres \
  -p 5433:5432 \
  paradedb/paradedb:latest

# 데이터베이스 초기화
python -m search_app.setup
```

### 옵션 B: 기존 데이터베이스 사용

이미 `../hybrid_search`에서 데이터베이스를 초기화했다면 이 단계를 건너뛰세요.

## 5단계: 실행!

### 🌐 Streamlit 웹 UI (권장)

```bash
streamlit run streamlit_app.py
```

브라우저에서 `http://localhost:8501` 열림

### 📟 CLI

```bash
python langgraph_rag.py "의사 전용 대출 상품 추천해줘"
```

### 📓 Jupyter 노트북

```bash
jupyter notebook test_langgraph_rag.ipynb
```

## 예제 질문

**검색이 필요한 질문:**
- "의사 전용 대출 상품 추천해줘"
- "저금리 대출을 찾고 있어요"
- "전세자금대출 상품 알려주세요"

**직접 답변 가능한 질문:**
- "안녕하세요"
- "대출이 뭐예요?"
- "감사합니다"

## 문제 해결

### Import 에러

```bash
python -c "from langgraph_rag import LangGraphRAG; print('OK')"
```

에러가 나면:
1. `.env` 파일 확인
2. 데이터베이스 실행 확인
3. 의존성 재설치: `pip install -r requirements.txt`

### 데이터베이스 연결 에러

```bash
# Docker 컨테이너 확인
docker ps | grep langgraph-db

# 로그 확인
docker logs langgraph-db
```

### OpenAI API 에러

- `.env` 파일에 올바른 API 키가 있는지 확인
- API 키 권한 확인

## 다음 단계

- [전체 문서 보기](README.md)
- [배포 가이드](DEPLOYMENT.md)
- [상세 설정](SETUP.md)

즐거운 코딩 되세요! 🚀
