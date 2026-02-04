# Cookiecutter 템플릿 사용 가이드

이 문서는 AWS Labs MCP Server Cookiecutter 템플릿을 사용하여 새 프로젝트를 생성하는 방법을 설명합니다.

## 📋 목차

- [사전 요구사항](#사전-요구사항)
- [템플릿으로 프로젝트 생성](#템플릿으로-프로젝트-생성)
- [생성된 프로젝트 시작하기](#생성된-프로젝트-시작하기)
- [개발 워크플로우](#개발-워크플로우)
- [Docker 사용](#docker-사용)
- [문제 해결](#문제-해결)

## 🔧 사전 요구사항

### 필수 요구사항

- **Python 3.10 이상**
  ```bash
  python --version  # 3.10 이상인지 확인
  ```

- **cookiecutter**
  ```bash
  pip install cookiecutter
  ```

### 권장 사항

- **uv 패키지 매니저** (더 빠른 의존성 설치)

  Windows (PowerShell):
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

  Linux/macOS:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- **Docker** (컨테이너화된 배포를 원하는 경우)
