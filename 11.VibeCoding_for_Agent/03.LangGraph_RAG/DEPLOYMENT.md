# 배포 가이드

이 문서는 LangGraph RAG Streamlit 앱을 다양한 플랫폼에 배포하는 방법을 설명합니다.

## 목차

1. [Streamlit Community Cloud (무료)](#streamlit-community-cloud)
2. [Docker 배포](#docker-배포)
3. [AWS EC2](#aws-ec2)
4. [로컬 배포](#로컬-배포)

---

## Streamlit Community Cloud

가장 쉬운 무료 배포 방법입니다.

### 사전 준비

1. GitHub 계정
2. Streamlit Community Cloud 계정 (무료)
3. 프로젝트를 GitHub에 푸시

### 배포 단계

#### 1. GitHub에 코드 푸시

```bash
cd LangGraph_RAG
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/langgraph-rag.git
git push -u origin main
```

#### 2. Streamlit Community Cloud 설정

1. https://share.streamlit.io 방문
2. "New app" 클릭
3. GitHub repository 선택
4. 다음 정보 입력:
   - **Main file path**: `streamlit_app.py`
   - **Python version**: 3.11

#### 3. Secrets 설정

Streamlit Cloud 대시보드에서 "Settings" → "Secrets" 클릭:

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "your-openai-api-key"
DATABASE_URL = "your-database-url"
```

#### 4. 배포

"Deploy" 버튼 클릭하면 자동으로 배포됩니다!

### 주의사항

- **무료 플랜 제한**:
  - 1GB RAM
  - 1 CPU
  - 공개 앱만 가능

- **데이터베이스**: 외부 PostgreSQL 필요 (예: Neon, Supabase)

---

## Docker 배포

Docker를 사용한 컨테이너 배포입니다.

### Dockerfile 생성

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### docker-compose.yml 생성

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    env_file:
      - .env
    depends_on:
      - db

  db:
    image: paradedb/paradedb:latest
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_DB=postgres
    ports:
      - "5433:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### 배포 실행

```bash
# 빌드
docker-compose build

# 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f app
```

앱은 `http://localhost:8501`에서 접근 가능합니다.

---

## AWS EC2

AWS EC2 인스턴스에 배포하는 방법입니다.

### 1. EC2 인스턴스 생성

- **AMI**: Ubuntu 22.04 LTS
- **Instance Type**: t3.medium (최소)
- **Security Group**:
  - Port 22 (SSH)
  - Port 8501 (Streamlit)
  - Port 5433 (PostgreSQL)

### 2. 서버 설정

```bash
# SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 업데이트
sudo apt update && sudo apt upgrade -y

# Python 설치
sudo apt install python3.11 python3.11-venv python3-pip -y

# Docker 설치 (선택)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 3. 프로젝트 배포

```bash
# 코드 클론
git clone https://github.com/YOUR_USERNAME/langgraph-rag.git
cd langgraph-rag

# 가상환경 생성
python3.11 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
nano .env  # OPENAI_API_KEY 등 설정
```

### 4. Streamlit 실행 (백그라운드)

```bash
# nohup 사용
nohup streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 &

# 또는 systemd 서비스로 등록
sudo nano /etc/systemd/system/langgraph-rag.service
```

**systemd 서비스 파일:**

```ini
[Unit]
Description=LangGraph RAG Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/langgraph-rag
Environment="PATH=/home/ubuntu/langgraph-rag/venv/bin"
ExecStart=/home/ubuntu/langgraph-rag/venv/bin/streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 시작
sudo systemctl daemon-reload
sudo systemctl start langgraph-rag
sudo systemctl enable langgraph-rag

# 상태 확인
sudo systemctl status langgraph-rag
```

### 5. Nginx 리버스 프록시 (선택)

```bash
# Nginx 설치
sudo apt install nginx -y

# 설정
sudo nano /etc/nginx/sites-available/langgraph-rag
```

**Nginx 설정:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 설정 활성화
sudo ln -s /etc/nginx/sites-available/langgraph-rag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 로컬 배포

개발 환경에서 로컬로 실행하는 방법입니다.

### 기본 실행

```bash
streamlit run streamlit_app.py
```

### 포트 변경

```bash
streamlit run streamlit_app.py --server.port=8080
```

### 외부 접근 허용

```bash
streamlit run streamlit_app.py --server.address=0.0.0.0
```

### 브라우저 자동 열기 비활성화

```bash
streamlit run streamlit_app.py --server.headless=true
```

---

## 환경 변수 관리

### 로컬 개발

`.env` 파일 사용:

```bash
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
```

### Production

환경 변수를 시스템에 직접 설정:

```bash
export OPENAI_API_KEY=sk-...
export DATABASE_URL=postgresql://...
```

또는 secrets 관리 도구 사용 (AWS Secrets Manager, etc.)

---

## 데이터베이스 설정

### Neon (무료 PostgreSQL)

1. https://neon.tech 회원가입
2. 프로젝트 생성
3. Connection string 복사
4. `.env`에 `DATABASE_URL` 설정

### Supabase (무료 PostgreSQL)

1. https://supabase.com 회원가입
2. 프로젝트 생성
3. Connection string 복사 (Direct connection)
4. `.env`에 `DATABASE_URL` 설정

### ParadeDB 확장 설치

ParadeDB 확장이 필요합니다. Neon/Supabase에서는 사용 불가할 수 있으므로, 자체 PostgreSQL + ParadeDB를 사용하거나 BM25_MODE=fts로 설정하세요.

---

## 모니터링

### Streamlit Cloud

- 빌트인 로그 확인
- CPU/메모리 사용량 모니터링

### Self-hosted

```bash
# 로그 확인
tail -f /var/log/langgraph-rag.log

# 리소스 모니터링
htop

# Streamlit 메트릭
http://your-app:8501/_stcore/health
```

---

## 문제 해결

### Port 충돌

```bash
# 8501 포트 사용 프로세스 확인
lsof -i :8501

# 프로세스 종료
kill -9 <PID>
```

### 메모리 부족

- 인스턴스 타입 업그레이드
- 또는 swap 메모리 추가

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 데이터베이스 연결 실패

1. DATABASE_URL 확인
2. 방화벽 규칙 확인
3. PostgreSQL 서비스 상태 확인

---

## 보안 권장사항

1. **HTTPS 사용**: Let's Encrypt로 SSL 인증서 설정
2. **환경 변수**: .env 파일을 git에 커밋하지 마세요
3. **방화벽**: 필요한 포트만 열어두세요
4. **업데이트**: 정기적으로 패키지 업데이트

---

## 비용 예측

### Streamlit Community Cloud
- **무료**: 1개 앱
- **제한**: 1GB RAM, 공개 앱만

### AWS EC2
- **t3.medium**: ~$30/월
- **데이터 전송**: 변동

### Digital Ocean
- **$12/월**: 2GB RAM, 1 vCPU
- **$24/월**: 4GB RAM, 2 vCPU

---

## 다음 단계

1. 도메인 연결
2. HTTPS 설정
3. 모니터링 도구 추가 (Sentry, etc.)
4. CI/CD 파이프라인 구축
5. 로드 밸런싱 (트래픽 증가 시)

배포에 성공하셨다면 이제 사용자들이 웹에서 LangGraph RAG를 사용할 수 있습니다! 🎉
