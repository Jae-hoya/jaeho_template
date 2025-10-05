"""
LangGraph PDF RAG 시스템 사용 예시
"""

import os
from langgraph_pdf_rag_ensemble_tavily import create_rag_graph, PDFRAGSystem

# def setup_environment():
#     """환경 설정"""
#     # API 키 설정 (실제 키로 변경하세요)
#     os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
#     os.environ["TAVILY_API_KEY"] = "your-tavily-api-key"

def example_basic_usage():
    """기본 사용 예시"""
    print("=== 기본 사용 예시 ===")
    
    # 그래프 생성
    app = create_rag_graph()
    
    # 질문 처리
    questions = [
        "문서에서 AI에 대해 설명해주세요",
        "최신 AI 기술 동향은 어떻게 되나요?",
        "이 문서의 주요 내용을 요약해주세요"
    ]
    
    for question in questions:
        print(f"\n질문: {question}")
        
        initial_state = {
            "messages": [],
            "documents": [],
            "query": question,
            "answer": "",
            "search_needed": True
        }
        
        try:
            result = app.invoke(initial_state)
            print(f"답변: {result['answer'][:200]}...")
        except Exception as e:
            print(f"오류: {e}")

def example_pdf_only_search():
    """PDF 전용 검색 예시"""
    print("\n=== PDF 전용 검색 예시 ===")
    
    # PDF RAG 시스템 직접 사용
    rag_system = PDFRAGSystem("data/SPRi AI Brief_8월호_산업동향_F.pdf")
    
    query = "문서에서 중요한 내용을 찾아주세요"
    documents = rag_system.retrieve_documents(query)
    
    print(f"검색된 문서 수: {len(documents)}")
    for i, doc in enumerate(documents[:2], 1):
        print(f"문서 {i}: {doc['content'][:100]}...")

def example_web_search():
    """웹 검색 예시"""
    print("\n=== 웹 검색 예시 ===")
    
    rag_system = PDFRAGSystem("data/SPRi AI Brief_8월호_산업동향_F.pdf")
    
    query = "최신 AI 기술 동향"
    web_results = rag_system.search_web(query)
    
    print(f"웹 검색 결과 수: {len(web_results)}")
    for i, result in enumerate(web_results[:2], 1):
        print(f"결과 {i}: {result['content'][:100]}...")

def example_custom_questions():
    """커스텀 질문 예시"""
    print("\n=== 커스텀 질문 예시 ===")
    
    app = create_rag_graph()
    
    # 다양한 유형의 질문들
    custom_questions = [
        {
            "question": "이 문서의 저자는 누구인가요?",
            "type": "PDF 검색"
        },
        {
            "question": "오늘 날씨는 어떤가요?",
            "type": "웹 검색"
        },
        {
            "question": "문서에서 언급된 기술들의 장단점을 분석해주세요",
            "type": "PDF 검색 + 분석"
        }
    ]
    
    for q in custom_questions:
        print(f"\n질문 유형: {q['type']}")
        print(f"질문: {q['question']}")
        
        initial_state = {
            "messages": [],
            "documents": [],
            "query": q['question'],
            "answer": "",
            "search_needed": True
        }
        
        try:
            result = app.invoke(initial_state)
            print(f"답변: {result['answer'][:150]}...")
        except Exception as e:
            print(f"오류: {e}")

def example_streaming():
    """스트리밍 예시"""
    print("\n=== 스트리밍 예시 ===")
    
    app = create_rag_graph()
    
    initial_state = {
        "messages": [],
        "documents": [],
        "query": "AI의 미래에 대해 설명해주세요",
        "answer": "",
        "search_needed": True
    }
    
    print("스트리밍 결과:")
    try:
        for chunk in app.stream(initial_state):
            print(f"Chunk: {chunk}")
    except Exception as e:
        print(f"스트리밍 오류: {e}")

def example_batch_processing():
    """배치 처리 예시"""
    print("\n=== 배치 처리 예시 ===")
    
    app = create_rag_graph()
    
    # 여러 질문을 한 번에 처리
    batch_questions = [
        "문서의 주요 키워드는 무엇인가요?",
        "이 문서의 결론은 무엇인가요?",
        "문서에서 제시된 해결책은 무엇인가요?"
    ]
    
    results = []
    for question in batch_questions:
        initial_state = {
            "messages": [],
            "documents": [],
            "query": question,
            "answer": "",
            "search_needed": True
        }
        
        try:
            result = app.invoke(initial_state)
            results.append({
                "question": question,
                "answer": result['answer'][:100] + "...",
                "documents_count": len(result.get('documents', []))
            })
        except Exception as e:
            results.append({
                "question": question,
                "answer": f"오류: {e}",
                "documents_count": 0
            })
    
    # 결과 출력
    for i, result in enumerate(results, 1):
        print(f"\n결과 {i}:")
        print(f"질문: {result['question']}")
        print(f"답변: {result['answer']}")
        print(f"참조 문서 수: {result['documents_count']}")

def main():
    """메인 실행 함수"""
    print("LangGraph PDF RAG 시스템 예시 실행")
    
    # 환경 설정
    # setup_environment()
    
    try:
        # 기본 사용 예시
        example_basic_usage()
        
        # PDF 전용 검색 예시
        example_pdf_only_search()
        
        # 웹 검색 예시
        example_web_search()
        
        # 커스텀 질문 예시
        example_custom_questions()
        
        # 스트리밍 예시
        example_streaming()
        
        # 배치 처리 예시
        example_batch_processing()
        
    except Exception as e:
        print(f"전체 실행 오류: {e}")
        print("API 키와 PDF 파일 경로를 확인해주세요.")

if __name__ == "__main__":
    main()