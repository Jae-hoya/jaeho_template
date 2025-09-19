#!/bin/bash

# Qdrant Docker 서비스 시작 스크립트

echo "🐳 Qdrant Docker 서비스 시작 중..."

# Docker Compose로 Qdrant 실행
docker-compose up -d

# Qdrant가 준비될 때까지 대기
echo "⏳ Qdrant 서비스 준비 중..."
sleep 10

# 헬스 체크
echo "🔍 Qdrant 서비스 상태 확인..."
for i in {1..30}; do
    if curl -s http://localhost:6333/health > /dev/null; then
        echo "✅ Qdrant 서비스가 정상적으로 시작되었습니다!"
        echo "📍 접속 주소: http://localhost:6333"
        echo "📊 대시보드: http://localhost:6333/dashboard"
        break
    else
        echo "⏳ 대기 중... ($i/30)"
        sleep 2
    fi
done

# 컨테이너 상태 확인
echo "📋 Docker 컨테이너 상태:"
docker ps | grep qdrant

echo "🎉 Qdrant 서비스가 준비되었습니다!"
echo "💡 Streamlit 앱을 실행하려면: streamlit run fast_main.py"

