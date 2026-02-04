# 🚀 Quick Start Guide

AWS Labs MCP Server Cookiecutter Template를 5분 안에 시작하세요!

## 📦 설치

```bash
# cookiecutter 설치
pip install cookiecutter

# uv 설치 (권장)
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 🎯 프로젝트 생성

```bash
# 1. 템플릿으로 프로젝트 생성
cookiecutter cookiecutter_template/

# 2. 프롬프트에 응답
# author_email: your.email@example.com
# author_name: Your Name
# project_domain: Weather API
# description: A weather data MCP server
# instructions: This server provides weather data tools...
```

## ⚡ 3단계로 시작하기

```bash
# 1. 프로젝트 디렉토리로 이동
cd weather-api-mcp-server

# 2. 의존성 설치
uv sync

# 3. 서버 실행
uv run weather-api-mcp-server
```

## 🧪 테스트 실행

```bash
# 전체 테스트 (coverage 포함)
uv run pytest --cov

# 빠른 테스트
uv run pytest
```

## 🐳 Docker로 실행

```bash
# 이미지 빌드
docker build -t weather-api-mcp-server .

# 컨테이너 실행
docker run -it weather-api-mcp-server
```

## 📚 다음 단계

1. `awslabs/weather_api_mcp_server/server.py` 열기
2. 예제 도구 (`example_tool`, `math_tool`) 확인
3. 커스텀 도구 추가
4. 테스트 작성
5. README 업데이트

## 📖 상세 문서

- [USAGE_GUIDE.md](USAGE_GUIDE.md) - 완전한 사용 가이드
- [TEMPLATE_MAINTENANCE.md](TEMPLATE_MAINTENANCE.md) - 유지보수 가이드
- [CONTRIBUTING.md](CONTRIBUTING.md) - 기여 가이드

## 💡 예제: 커스텀 도구 추가

```python
# server.py
@mcp.tool()
def get_weather(city: str) -> dict:
    """Get current weather for a city.

    Args:
        city: City name

    Returns:
        Weather data
    """
    # 실제 API 호출 구현
    return {
        "city": city,
        "temperature": 20,
        "condition": "Sunny"
    }
```

## 🆘 도움말

문제가 발생했나요?

- [USAGE_GUIDE.md](USAGE_GUIDE.md)의 "문제 해결" 섹션 확인
- [GitHub Issues](https://github.com/your-username/aws-mcp-cookiecutter/issues) 검색
- [GitHub Discussions](https://github.com/your-username/aws-mcp-cookiecutter/discussions)에서 질문

---

Happy Coding! 🎉
