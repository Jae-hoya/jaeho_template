"""
Marketing Tools Backend - FastAPI + LangChain
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from agents.copyjoe_agent import CopyjoeAgent
from agents.chenius_chat_agent import CheniusChatAgent
from agents.brief_reader_agent import BriefReaderAgent

app = FastAPI(
    title="Marketing Tools API",
    description="카피조, Chenius Chat, Brief Reader API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent 인스턴스
copyjoe = CopyjoeAgent()
chenius = CheniusChatAgent()
brief_reader = BriefReaderAgent()


# ============ Request/Response Models ============

class CopyRequest(BaseModel):
    copy_type: str  # slogan, problem, benefit, cta
    brand: str
    target: Optional[str] = ""
    benefit: Optional[str] = ""
    problem: Optional[str] = ""
    rag_content: Optional[str] = ""


class CopyResponse(BaseModel):
    copies: List[dict]


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []


class ChatResponse(BaseModel):
    creative: str
    practical: str


class BriefRequest(BaseModel):
    content: str


class BriefResponse(BaseModel):
    company: Optional[str] = None
    product: Optional[str] = None
    target: Optional[str] = None
    problem: Optional[str] = None
    usp: Optional[str] = None
    tone: Optional[str] = None
    goals: Optional[List[str]] = []
    keywords: Optional[List[str]] = []
    insights: Optional[str] = None


# ============ API Endpoints ============

@app.get("/")
async def root():
    return {"message": "Marketing Tools API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ------------ Copyjoe Endpoints ------------

@app.post("/api/copyjoe/generate", response_model=CopyResponse)
async def generate_copy(request: CopyRequest):
    """카피 생성 API"""
    try:
        result = await copyjoe.generate(
            copy_type=request.copy_type,
            brand=request.brand,
            target=request.target,
            benefit=request.benefit,
            problem=request.problem,
            rag_content=request.rag_content
        )
        return CopyResponse(copies=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/copyjoe/upload-rag")
async def upload_rag_file(file: UploadFile = File(...)):
    """RAG 파일 업로드"""
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        return {"filename": file.filename, "content": text_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------ Chenius Chat Endpoints ------------

@app.post("/api/chenius/chat", response_model=ChatResponse)
async def chenius_chat(request: ChatRequest):
    """듀얼 AI 채팅 API"""
    try:
        creative, practical = await chenius.chat(
            message=request.message,
            history=request.history
        )
        return ChatResponse(creative=creative, practical=practical)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------ Brief Reader Endpoints ------------

@app.post("/api/brief/analyze", response_model=BriefResponse)
async def analyze_brief(request: BriefRequest):
    """브리프 분석 API"""
    try:
        result = await brief_reader.analyze(request.content)
        return BriefResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/brief/upload")
async def upload_brief_file(file: UploadFile = File(...)):
    """브리프 파일 업로드"""
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        return {"filename": file.filename, "content": text_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
