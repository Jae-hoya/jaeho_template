from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
from datetime import datetime
import json
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI(title="RAG Template API", version="1.0.0")

# 피드백 데이터 모델
class FeedbackData(BaseModel):
    thread_id: str
    question_count: int
    feedback_scores: Dict[str, int]
    comment: Optional[str] = None
    timestamp: Optional[str] = None

# 대화 데이터 모델
class ConversationData(BaseModel):
    thread_id: str
    question_count: int
    user_message: str
    ai_response: str
    timestamp: Optional[str] = None

# 배치 대화 데이터 모델
class BatchConversationData(BaseModel):
    conversations: List[ConversationData]
    batch_timestamp: Optional[str] = None

# 세션 요약 데이터 모델
class SessionSummaryData(BaseModel):
    thread_id: str
    total_questions: int
    session_duration: int
    conversation_count: int
    remaining_conversations: Optional[List[ConversationData]] = None
    timestamp: Optional[str] = None

# 피드백 데이터를 저장할 리스트 (실제로는 데이터베이스를 사용해야 함)
feedback_storage = []
conversation_storage = []

# 비동기 처리를 위한 스레드 풀
executor = ThreadPoolExecutor(max_workers=10)

@app.get("/")
async def root():
    return {"message": "LangGraph Feedback API is running"}

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackData, background_tasks: BackgroundTasks):
    try:
        # 타임스탬프 추가
        if not feedback.timestamp:
            feedback.timestamp = datetime.now().isoformat()
        
        # 피드백 데이터 저장 (비동기)
        background_tasks.add_task(save_feedback_async, feedback.dict())
        
        return {
            "status": "success",
            "message": "피드백이 성공적으로 제출되었습니다.",
            "data": feedback.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"피드백 제출 중 오류가 발생했습니다: {str(e)}")

@app.post("/conversation")
async def submit_conversation(conversation: ConversationData, background_tasks: BackgroundTasks):
    """단일 대화 내용을 저장하는 엔드포인트"""
    try:
        # 타임스탬프 추가
        if not conversation.timestamp:
            conversation.timestamp = datetime.now().isoformat()
        
        # 대화 데이터 저장 (비동기)
        background_tasks.add_task(save_conversation_async, conversation.dict())
        
        return {
            "status": "success",
            "message": "대화가 성공적으로 저장되었습니다.",
            "data": conversation.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대화 저장 중 오류가 발생했습니다: {str(e)}")

@app.post("/conversation/thread")
async def submit_conversation_by_thread(conversation: ConversationData, background_tasks: BackgroundTasks):
    """thread_id별로 같은 파일에 대화를 저장하는 엔드포인트"""
    try:
        # 타임스탬프 추가
        if not conversation.timestamp:
            conversation.timestamp = datetime.now().isoformat()
        
        # thread_id별로 같은 파일에 저장 (비동기)
        background_tasks.add_task(save_conversation_by_thread_async, conversation.dict())
        
        return {
            "status": "success",
            "message": "대화가 thread_id별로 성공적으로 저장되었습니다.",
            "data": conversation.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"thread_id별 대화 저장 중 오류가 발생했습니다: {str(e)}")

@app.post("/conversation/batch")
async def submit_conversation_batch(batch_data: BatchConversationData, background_tasks: BackgroundTasks):
    """배치 대화 내용을 저장하는 엔드포인트"""
    try:
        # 타임스탬프 추가
        if not batch_data.batch_timestamp:
            batch_data.batch_timestamp = datetime.now().isoformat()
        
        # 각 대화에 타임스탬프 추가
        for conversation in batch_data.conversations:
            if not conversation.timestamp:
                conversation.timestamp = datetime.now().isoformat()
        
        # 배치 대화 데이터 저장 (비동기)
        background_tasks.add_task(save_conversation_batch_async, batch_data.dict())
        
        return {
            "status": "success",
            "message": f"{len(batch_data.conversations)}개의 대화가 성공적으로 저장되었습니다.",
            "batch_size": len(batch_data.conversations),
            "batch_timestamp": batch_data.batch_timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 대화 저장 중 오류가 발생했습니다: {str(e)}")

@app.post("/session/summary")
async def submit_session_summary(summary: SessionSummaryData, background_tasks: BackgroundTasks):
    """세션 요약을 저장하는 엔드포인트"""
    try:
        # 타임스탬프 추가
        if not summary.timestamp:
            summary.timestamp = datetime.now().isoformat()
        
        # 세션 요약 데이터 저장 (비동기)
        background_tasks.add_task(save_session_summary_async, summary.dict())
        
        return {
            "status": "success",
            "message": "세션 요약이 성공적으로 저장되었습니다.",
            "data": {
                "thread_id": summary.thread_id,
                "total_questions": summary.total_questions,
                "session_duration": summary.session_duration,
                "conversation_count": summary.conversation_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 요약 저장 중 오류가 발생했습니다: {str(e)}")

@app.get("/feedback")
async def get_feedback():
    """모든 피드백 데이터 조회"""
    return {
        "status": "success",
        "count": len(feedback_storage),
        "data": feedback_storage
    }

@app.get("/conversation")
async def get_conversations():
    """모든 대화 데이터 조회"""
    return {
        "status": "success",
        "count": len(conversation_storage),
        "data": conversation_storage
    }

@app.get("/feedback/{thread_id}")
async def get_feedback_by_thread(thread_id: str):
    """특정 스레드의 피드백 데이터 조회"""
    thread_feedback = [f for f in feedback_storage if f["thread_id"] == thread_id]
    return {
        "status": "success",
        "thread_id": thread_id,
        "count": len(thread_feedback),
        "data": thread_feedback
    }

@app.get("/conversation/{thread_id}")
async def get_conversation_by_thread(thread_id: str):
    """특정 스레드의 대화 데이터 조회"""
    thread_conversations = [c for c in conversation_storage if c["thread_id"] == thread_id]
    return {
        "status": "success",
        "thread_id": thread_id,
        "count": len(thread_conversations),
        "data": thread_conversations
    }

async def save_feedback_async(feedback_data: Dict[str, Any]):
    """비동기로 피드백 데이터 저장"""
    try:
        # 메모리에 저장
        feedback_storage.append(feedback_data)
        
        # 파일로 저장 (비동기)
        await asyncio.get_event_loop().run_in_executor(
            executor, save_feedback_to_file, feedback_data
        )
    except Exception as e:
        print(f"피드백 저장 오류: {e}")

async def save_conversation_async(conversation_data: Dict[str, Any]):
    """비동기로 대화 데이터 저장"""
    try:
        # 메모리에 저장
        conversation_storage.append(conversation_data)
        
        # 파일로 저장 (비동기)
        await asyncio.get_event_loop().run_in_executor(
            executor, save_conversation_to_file, conversation_data
        )
    except Exception as e:
        print(f"대화 저장 오류: {e}")

async def save_conversation_by_thread_async(conversation_data: Dict[str, Any]):
    """비동기로 thread_id별로 같은 파일에 대화 데이터 저장"""
    try:
        # 메모리에 저장
        conversation_storage.append(conversation_data)
        
        # thread_id별로 같은 파일에 저장 (비동기)
        await asyncio.get_event_loop().run_in_executor(
            executor, save_conversation_by_thread_to_file, conversation_data
        )
    except Exception as e:
        print(f"thread_id별 대화 저장 오류: {e}")

def save_feedback_to_file(feedback_data: Dict[str, Any]):
    """피드백 데이터를 JSON 파일로 저장"""
    feedback_dir = "feedback_data"
    if not os.path.exists(feedback_dir):
        os.makedirs(feedback_dir)
    
    filename = f"{feedback_dir}/feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(feedback_data, f, ensure_ascii=False, indent=2)

def save_conversation_to_file(conversation_data: Dict[str, Any]):
    """대화 데이터를 JSON 파일로 저장"""
    conversation_dir = "conversation_data"
    if not os.path.exists(conversation_dir):
        os.makedirs(conversation_dir)
    
    filename = f"{conversation_dir}/conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, ensure_ascii=False, indent=2)

def save_conversation_by_thread_to_file(conversation_data: Dict[str, Any]):
    """thread_id별로 같은 파일에 대화 데이터를 저장"""
    conversation_dir = "conversation_data"
    if not os.path.exists(conversation_dir):
        os.makedirs(conversation_dir)
    
    thread_id = conversation_data["thread_id"]
    thread_short = thread_id[:8]  # 8자리로 하면 더 구별하기 쉬움
    
    # 기존 파일이 있는지 확인 (thread_id로 시작하는 파일들 중에서)
    existing_files = [f for f in os.listdir(conversation_dir) if f.startswith(f"thread_{thread_short}_")]
    
    if existing_files:
        # 기존 파일이 있으면 그 파일 사용
        filename = f"{conversation_dir}/{existing_files[0]}"
    else:
        # 첫 번째 대화일 때만 시간 추가
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{conversation_dir}/thread_{thread_short}_{current_time}.json"
    
    # 기존 파일이 있으면 읽어오기
    existing_conversations = []
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if isinstance(existing_data, dict) and "conversations" in existing_data:
                    existing_conversations = existing_data["conversations"]
                elif isinstance(existing_data, list):
                    existing_conversations = existing_data
        except Exception as e:
            print(f"기존 파일 읽기 오류: {e}")
            existing_conversations = []
    
    # 새로운 대화 추가
    existing_conversations.append(conversation_data)
    
    # 파일에 저장
    thread_data = {
        "thread_id": thread_id,
        "conversations": existing_conversations,
        "last_updated": datetime.now().isoformat()
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(thread_data, f, ensure_ascii=False, indent=2)

async def save_conversation_batch_async(batch_data: Dict[str, Any]):
    """비동기로 배치 대화 데이터 저장"""
    try:
        # 각 대화를 메모리에 저장
        for conversation in batch_data["conversations"]:
            conversation_storage.append(conversation)
        
        # 배치 파일로 저장 (비동기)
        await asyncio.get_event_loop().run_in_executor(
            executor, save_conversation_batch_to_file, batch_data
        )
    except Exception as e:
        print(f"배치 대화 저장 오류: {e}")

async def save_session_summary_async(summary_data: Dict[str, Any]):
    """비동기로 세션 요약 데이터 저장"""
    try:
        # 세션 요약을 메모리에 저장
        conversation_storage.append(summary_data)
        
        # 세션 요약 파일로 저장 (비동기)
        await asyncio.get_event_loop().run_in_executor(
            executor, save_session_summary_to_file, summary_data
        )
    except Exception as e:
        print(f"세션 요약 저장 오류: {e}")

def save_conversation_batch_to_file(batch_data: Dict[str, Any]):
    """배치 대화 데이터를 JSON 파일로 저장"""
    conversation_dir = "conversation_data"
    if not os.path.exists(conversation_dir):
        os.makedirs(conversation_dir)
    
    filename = f"{conversation_dir}/batch_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(batch_data, f, ensure_ascii=False, indent=2)

def save_session_summary_to_file(summary_data: Dict[str, Any]):
    """세션 요약 데이터를 JSON 파일로 저장"""
    conversation_dir = "conversation_data"
    if not os.path.exists(conversation_dir):
        os.makedirs(conversation_dir)
    
    filename = f"{conversation_dir}/session_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
