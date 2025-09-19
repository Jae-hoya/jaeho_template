# Docker 기반 Streamlit Cloud 배포 가이드

## 🐳 Docker로 Qdrant 서비스 실행

### 1. 로컬에서 Qdrant 실행

```bash
# Docker Compose로 Qdrant 실행
cd RAG_strategies/Agentic_RAG
docker-compose up -d

# Qdrant 상태 확인
curl http://localhost:6333/health
```

### 2. Streamlit Cloud 배포 설정

#### 방법 1: Streamlit Cloud에서 Docker 서비스 사용

1. **GitHub 저장소에 docker-compose.yml 포함**
2. **Streamlit Cloud 설정**:
   - Main file: `RAG_strategies/Agentic_RAG/fast_main.py`
   - Requirements: `requirements.txt`

#### 방법 2: 외부 Qdrant 서비스 사용

1. **Qdrant Cloud 사용** (권장):
   - [Qdrant Cloud](https://cloud.qdrant.io/)에서 무료 계정 생성
   - 클러스터 생성 후 API 키와 엔드포인트 획득

2. **환경 변수 설정**:
   ```
   QDRANT_HOST=your-cluster-url.qdrant.tech
   QDRANT_PORT=6333
   QDRANT_API_KEY=your-api-key
   OPENAI_API_KEY=your-openai-key
   LANGSMITH_API_KEY=your-langsmith-key
   TAVILY_API_KEY=your-tavily-key
   ```

### 3. 로컬 개발 환경

#### Docker Compose 실행
```bash
# Qdrant 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f qdrant

# 서비스 중지
docker-compose down
```

#### Streamlit 앱 실행
```bash
# Streamlit 앱 실행
streamlit run fast_main.py
```

### 4. 환경 변수 설정

#### .env 파일 생성
```env
# Qdrant 설정
QDRANT_HOST=localhost
QDRANT_PORT=6333

# API 키들
OPENAI_API_KEY=your_openai_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
TAVILY_API_KEY=your_tavily_api_key
LANGSMITH_PROJECT=Agentic RAG System
```

### 5. 벡터 데이터베이스 설정

#### 컬렉션 생성 및 데이터 로드
```python
# 벡터 데이터베이스 초기화 스크립트
from retriever import QdrantRetrieverFactory
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Qdrant 클라이언트 생성
qs = QdrantRetrieverFactory()

# 문서 로드 및 벡터화
loader = PyPDFLoader("path/to/your/document.pdf")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
splits = text_splitter.split_documents(documents)

# 벡터스토어에 저장
vectorstore = qs._get_vectorstore("RAG_Example(RAG_strategies)")
vectorstore.add_documents(splits)
```

### 6. 배포 옵션

#### 옵션 1: Streamlit Cloud + Qdrant Cloud
- **장점**: 완전 관리형 서비스
- **단점**: Qdrant Cloud 비용 발생
- **추천**: 프로덕션 환경

#### 옵션 2: Streamlit Cloud + Mock Retriever
- **장점**: 무료, 간단한 설정
- **단점**: 문서 검색 기능 제한
- **추천**: 개발/테스트 환경

#### 옵션 3: 로컬 Docker + Streamlit
- **장점**: 완전한 기능, 무료
- **단점**: 로컬에서만 접근 가능
- **추천**: 개발 환경

### 7. 문제 해결

#### Qdrant 연결 실패
```bash
# Docker 컨테이너 상태 확인
docker ps | grep qdrant

# 포트 확인
netstat -tulpn | grep 6333

# 로그 확인
docker logs qdrant-rag
```

#### Streamlit Cloud 배포 실패
1. 환경 변수 설정 확인
2. requirements.txt 의존성 확인
3. 파일 경로 확인

### 8. 성능 최적화

#### Qdrant 설정 최적화
```yaml
# docker-compose.yml에 추가
environment:
  - QDRANT__SERVICE__HTTP_PORT=6333
  - QDRANT__SERVICE__GRPC_PORT=6334
  - QDRANT__STORAGE__OPTIMIZERS_CONFIG__DEFAULT_SEGMENT_NUMBER=2
  - QDRANT__STORAGE__OPTIMIZERS_CONFIG__MAX_SEGMENT_SIZE_KB=200000
```

#### 메모리 사용량 최적화
```python
# retriever.py에서 배치 크기 조정
def retriever(self, collection_name: str, fetch_k: int = 3):  # fetch_k 줄이기
    # ...
```

### 9. 모니터링

#### Qdrant 상태 확인
```bash
# 헬스 체크
curl http://localhost:6333/health

# 컬렉션 정보
curl http://localhost:6333/collections

# 통계 정보
curl http://localhost:6333/cluster
```

#### Streamlit 앱 모니터링
- Streamlit Cloud 대시보드에서 로그 확인
- LangSmith에서 추적 정보 확인

### 10. 보안 고려사항

#### API 키 보안
- 환경 변수로 API 키 관리
- GitHub에 .env 파일 커밋 금지
- Streamlit Cloud Secrets 사용

#### 네트워크 보안
- Qdrant 포트를 로컬에서만 접근 가능하도록 설정
- 방화벽 설정 확인

이제 Docker를 사용하여 Qdrant를 실행하고 Streamlit Cloud에서 접근할 수 있습니다!

