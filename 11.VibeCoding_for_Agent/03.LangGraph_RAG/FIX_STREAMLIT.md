# Streamlit 실행 오류 해결 가이드

## 문제 상황

```
Fatal error in launcher: Unable to create process using '"C:\Users\skyop\jaeho_template\dotenv\Scripts\python.exe"
```

가상환경 경로 문제입니다.

---

## 해결 방법

### 방법 1: 올바른 디렉토리로 이동 + Python 직접 실행 (권장)

```powershell
# 1. LangGraph_RAG 디렉토리로 이동
cd C:\Users\skyop\jaeho_template\11.VibeCoding_for_Agent\LangGraph_RAG

# 2. Python으로 streamlit 모듈 직접 실행
python -m streamlit run streamlit_app.py
```

### 방법 2: Streamlit 재설치

```powershell
# 1. 현재 streamlit 제거
pip uninstall streamlit -y

# 2. 재설치
pip install streamlit

# 3. 실행
streamlit run streamlit_app.py
```

### 방법 3: 새 가상환경 생성 (완전 초기화)

```powershell
# 1. LangGraph_RAG 디렉토리로 이동
cd C:\Users\skyop\jaeho_template\11.VibeCoding_for_Agent\LangGraph_RAG

# 2. 새 가상환경 생성
python -m venv venv

# 3. 가상환경 활성화
.\venv\Scripts\activate

# 4. 의존성 설치
pip install -r requirements.txt

# 5. 실행
python -m streamlit run streamlit_app.py
```

---

## 빠른 해결 (추천)

가장 빠른 방법:

```powershell
cd LangGraph_RAG
python -m streamlit run streamlit_app.py
```

`python -m streamlit`을 사용하면 경로 문제를 우회할 수 있습니다.

---

## 현재 위치 확인

```powershell
# 현재 디렉토리 확인
pwd

# 올바른 위치:
# C:\Users\skyop\jaeho_template\11.VibeCoding_for_Agent\LangGraph_RAG
```

---

## 실행 확인

정상 실행되면 다음과 같이 표시됩니다:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

브라우저가 자동으로 열립니다!

---

## 문제가 계속되면

### 1. Python 경로 확인

```powershell
python --version
Get-Command python
```

### 2. 설치된 패키지 확인

```powershell
pip list | Select-String streamlit
```

### 3. 환경 변수 확인

```powershell
$env:OPENAI_API_KEY
```

없으면 `.env` 파일 생성 필요:

```powershell
cp .env.example .env
notepad .env
```
