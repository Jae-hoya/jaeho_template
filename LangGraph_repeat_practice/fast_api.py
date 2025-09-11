from fastapi import FastAPI

from langserve import add_route

from langchain_api import chain


app = FastAPI()

# uvicorn rag_api:app --reload --port=8000
# reload는 파일의 내용이 변하면 다시 api를 load한다는 뜻

@app.get("/") 
async def root(): #하나의 함수 생성
    return {"message": "Hello World!"}