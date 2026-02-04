Windows에서 Windows Subsystem for Linux (WSL) 기능을 활성화하는 명령어
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
wsl --set-default-version 2

# hyper-v 설치
시스템 설정에서!

# 도커설치
docker desktop에서 설치

새창에서 
docker --version 
docker-compose --version 
docker run hello # container에 뜰것. 실험이니까 지우자.
해보기


# qdrant 설치
docker terminal에서, 
docker pull qdrant/qdrant

docker run -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant

기존 컨테이너가 있으면 정리 (없으면 에러 무시됨) 
docker stop qdrant 2>$null
docker rm qdrant 2>$null

# 볼륨을 마운트하여 실행
docker run -d --name qdrant `
  --restart unless-stopped `
  -p 6333:6333 -p 6334:6334 `
  -v qdrant_storage:/qdrant/storage `
  qdrant/qdrant:latest

# ollama 설치
docker pull ollama/ollama