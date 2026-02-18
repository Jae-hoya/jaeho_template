# 1) 백엔드
python -m uvicorn app.main:app --reload
# 2) Vue 랜딩(dev)
cd frontend
npm install
npm run dev
# -> http://127.0.0.1:5173
# 3) CLI 대화형
python scripts/interactive_copy_chat.py --base-url http://127.0.0.1:8000
원하면 다음 단계로, Vue 화면에서 “채팅형 입력(자연어 한 줄) -> 내부 파싱 -> /copy/generate”까지 완전 챗 UI로 더 단순화 가능