"""
Enhanced MCP RAG Server V2
==========================

확장 기능:
1. Query Expansion: LLM을 사용한 쿼리 확장
2. Temperature Control: 쿼리 확장 시 LLM 창의성 조절
3. Multiple Retriever Modes: Basic / Compression (Reranking)

Port: 8103 (기존 버전과 충돌 방지)
"""

from retriever import FAISSRetrieverFactory, QdrantRetrieverFactory
from mcp.server.fastmcp import FastMCP
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Literal

from dotenv import load_dotenv
load_dotenv(override=True)

mcp = FastMCP(
    "Enhanced_Retriever_V2",
    instructions="An Enhanced Retriever V2 with query expansion, temperature control, and multiple retrieval modes. Database is for SPRI AI Brief",
    host="0.0.0.0",
    port=8103,  # 기존 버전(8102)과 다른 포트 사용
)

# Query expansion을 위한 LLM 및 프롬프트 설정
def expand_query(original_query: str, temperature: float = 0.7) -> list[str]:
    """
    원본 쿼리를 LLM을 사용해 확장하여 다양한 검색 쿼리를 생성합니다.
    
    Args:
        original_query: 원본 검색 쿼리
        temperature: LLM의 창의성 수준 (0.0~1.0)
        
    Returns:
        list[str]: 확장된 쿼리 리스트 (원본 포함)
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
    
    expansion_prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 검색 쿼리 확장 전문가입니다. 
        주어진 쿼리를 분석하여 관련된 3가지 다른 표현/관점의 검색 쿼리를 생성하세요.
        각 쿼리는 원본의 의도를 유지하면서도 다른 각도에서 정보를 찾을 수 있도록 작성해야 합니다.
        
        다음 형식으로만 답변하세요:
        1. [첫 번째 확장 쿼리]
        2. [두 번째 확장 쿼리]
        3. [세 번째 확장 쿼리]"""),
        ("user", "원본 쿼리: {query}")
    ])
    
    chain = expansion_prompt | llm
    response = chain.invoke({"query": original_query})
    
    # 응답 파싱
    expanded_queries = [original_query]  # 원본 쿼리 포함
    for line in response.content.split('\n'):
        line = line.strip()
        if line and any(line.startswith(f"{i}.") for i in range(1, 4)):
            # "1. ", "2. ", "3. " 제거
            query = line.split('.', 1)[1].strip()
            expanded_queries.append(query)
    
    return expanded_queries


@mcp.tool()
async def retrieve(
    query: str,
    use_expansion: bool = False,
    temperature: float = 0.7,
    retriever_mode: Literal["basic", "compression"] = "basic",
    fetch_k: int = 3,
    top_n: int = 3,
    auto_optimize_temperature: bool = False
) -> str:
    """
    향상된 검색 기능으로 문서 데이터베이스에서 정보를 검색합니다.

    Args:
        query (str): 검색 쿼리
        use_expansion (bool): 쿼리 확장 사용 여부 (기본값: False)
        temperature (float): LLM temperature (0.0~1.0, 기본값: 0.7). 쿼리 확장 시 사용
        retriever_mode (str): retriever 모드 - "basic" 또는 "compression" (기본값: "basic")
        fetch_k (int): 검색할 문서 개수 (basic 모드) 또는 초기 검색 개수 (compression 모드) (기본값: 3)
        top_n (int): compression 모드에서 최종 반환할 문서 개수 (기본값: 3)
        auto_optimize_temperature (bool): MCP가 자동으로 최적 temperature 선택 (기본값: False)

    Returns:
        str: 검색된 모든 문서의 내용을 연결한 텍스트
        
    Examples:
        # 기본 검색
        await retrieve(query="AI 트렌드")
        
        # 쿼리 확장 사용
        await retrieve(query="AI 윤리", use_expansion=True, temperature=0.7)
        
        # 🆕 MCP가 자동으로 최적 temperature 선택
        await retrieve(
            query="딥러닝 활용",
            use_expansion=True,
            auto_optimize_temperature=True,
            retriever_mode="compression"
        )
        
        # 고품질 검색 (압축 + 쿼리 확장)
        await retrieve(
            query="딥러닝 활용",
            use_expansion=True,
            temperature=0.5,
            retriever_mode="compression",
            fetch_k=20,
            top_n=5
        )
    """
    
    # 자동 최적화 모드
    if auto_optimize_temperature and use_expansion:
        print(f"[V2] Auto-optimize 모드 활성화")
        return await retrieve_auto_optimized(
            query=query,
            retriever_mode=retriever_mode,
            fetch_k=fetch_k,
            top_n=top_n,
            show_process=False
        )
    
    qs = QdrantRetrieverFactory()
    
    # Retriever 모드에 따라 다른 retriever 생성
    if retriever_mode == "compression":
        qs_retriever = qs.compression_retriever(
            collection_name="RAG_Example(RAG_strategies)", 
            fetch_k=fetch_k if fetch_k >= top_n else 20,
            top_n=top_n
        )
    else:
        qs_retriever = qs.retriever(
            collection_name="RAG_Example(RAG_strategies)", 
            fetch_k=fetch_k
        )
    
    # Query expansion 사용 여부
    if use_expansion:
        queries = expand_query(query, temperature)
        print(f"\n[V2] 확장된 쿼리들:")
        for i, q in enumerate(queries):
            print(f"  {i+1}. {q}")
        
        # 모든 확장 쿼리로 검색 수행
        all_docs = []
        seen_contents = set()  # 중복 제거용
        
        for q in queries:
            docs = qs_retriever.invoke(q)
            for doc in docs:
                # 중복 제거: 같은 내용은 한 번만 포함
                if doc.page_content not in seen_contents:
                    seen_contents.add(doc.page_content)
                    all_docs.append(doc)
        
        retrieved_docs = all_docs
        print(f"[V2] 총 {len(retrieved_docs)}개 문서 검색됨 (중복 제거 후)")
    else:
        # 기본 단일 쿼리 검색
        retrieved_docs = qs_retriever.invoke(query)
        print(f"[V2] {len(retrieved_docs)}개 문서 검색됨")

    # 검색된 문서들을 구분자와 함께 반환
    result = []
    result.append(f"[Enhanced Retriever V2] 검색 모드: {retriever_mode}")
    result.append(f"쿼리 확장: {'사용' if use_expansion else '미사용'}")
    if use_expansion:
        result.append(f"Temperature: {temperature}")
    result.append(f"검색 결과: {len(retrieved_docs)}개 문서\n")
    result.append("=" * 60)
    
    for i, doc in enumerate(retrieved_docs, 1):
        result.append(f"\n=== Document {i} ===")
        result.append(doc.page_content)
        result.append("")  # 문서 간 빈 줄
    
    return "\n".join(result)


@mcp.tool()
async def retrieve_basic(query: str, fetch_k: int = 3) -> str:
    """
    기본 검색 (호환성을 위한 간단한 인터페이스)
    
    Args:
        query: 검색 쿼리
        fetch_k: 검색할 문서 개수
        
    Returns:
        str: 검색된 문서들
    """
    return await retrieve(query=query, use_expansion=False, fetch_k=fetch_k)


@mcp.tool()
async def retrieve_advanced(
    query: str,
    use_expansion: bool = True,
    temperature: float = 0.7,
    fetch_k: int = 20,
    top_n: int = 5
) -> str:
    """
    고급 검색 (쿼리 확장 + Reranking)
    
    Args:
        query: 검색 쿼리
        use_expansion: 쿼리 확장 사용 여부
        temperature: LLM temperature
        fetch_k: 초기 검색 개수
        top_n: 최종 반환 개수
        
    Returns:
        str: 검색된 문서들
    """
    return await retrieve(
        query=query,
        use_expansion=use_expansion,
        temperature=temperature,
        retriever_mode="compression",
        fetch_k=fetch_k,
        top_n=top_n
    )


@mcp.tool()
async def retrieve_with_temperature_comparison(
    query: str,
    temperatures: list[float] = None,
    retriever_mode: Literal["basic", "compression"] = "compression",
    fetch_k: int = 20,
    top_n: int = 5
) -> str:
    """
    여러 temperature 값으로 쿼리를 확장하고 검색 결과를 비교합니다.
    MCP가 자동으로 최적의 temperature를 찾아줍니다!
    
    Args:
        query: 검색 쿼리
        temperatures: 비교할 temperature 리스트 (기본값: [0.3, 0.7, 0.9])
        retriever_mode: retriever 모드 - "basic" 또는 "compression"
        fetch_k: 초기 검색 개수
        top_n: 최종 반환 개수
        
    Returns:
        str: 각 temperature별 확장된 쿼리 및 검색 결과 비교
        
    Examples:
        # 기본 3가지 temperature로 비교
        await retrieve_with_temperature_comparison(query="AI 윤리")
        
        # 커스텀 temperature로 비교
        await retrieve_with_temperature_comparison(
            query="딥러닝",
            temperatures=[0.2, 0.5, 0.8],
            retriever_mode="compression"
        )
    """
    if temperatures is None:
        temperatures = [0.3, 0.7, 0.9]  # 보수적, 균형, 창의적
    
    temp_names = {
        0.1: "매우 보수적", 0.2: "매우 보수적", 0.3: "보수적",
        0.4: "약간 보수적", 0.5: "중립적", 0.6: "약간 창의적",
        0.7: "균형잡힌", 0.8: "창의적", 0.9: "매우 창의적", 1.0: "최대 창의적"
    }
    
    result = []
    result.append("=" * 80)
    result.append("🌡️  Temperature 비교 검색")
    result.append("=" * 80)
    result.append(f"\n원본 쿼리: {query}")
    result.append(f"비교할 Temperature: {temperatures}")
    result.append(f"검색 모드: {retriever_mode}\n")
    result.append("=" * 80)
    
    # 각 temperature별 쿼리 확장 비교
    all_expansions = {}
    for temp in temperatures:
        expanded = expand_query(query, temperature=temp)
        all_expansions[temp] = expanded
        
        temp_label = temp_names.get(temp, f"Temperature {temp}")
        result.append(f"\n🌡️  Temperature {temp} ({temp_label})")
        result.append("-" * 60)
        for i, q in enumerate(expanded):
            if i == 0:
                result.append(f"  원본: {q}")
            else:
                result.append(f"  확장{i}: {q}")
    
    result.append("\n" + "=" * 80)
    result.append("📊 각 Temperature별 검색 결과")
    result.append("=" * 80)
    
    # 각 temperature별 검색 수행
    qs = QdrantRetrieverFactory()
    
    if retriever_mode == "compression":
        retriever = qs.compression_retriever(
            collection_name="RAG_Example(RAG_strategies)",
            fetch_k=fetch_k,
            top_n=top_n
        )
    else:
        retriever = qs.retriever(
            collection_name="RAG_Example(RAG_strategies)",
            fetch_k=fetch_k
        )
    
    temp_results = {}
    for temp in temperatures:
        queries = all_expansions[temp]
        all_docs = []
        seen_contents = set()
        
        for q in queries:
            docs = retriever.invoke(q)
            for doc in docs:
                if doc.page_content not in seen_contents:
                    seen_contents.add(doc.page_content)
                    all_docs.append(doc)
        
        temp_results[temp] = all_docs
        
        temp_label = temp_names.get(temp, f"Temperature {temp}")
        result.append(f"\n🌡️  Temperature {temp} ({temp_label})")
        result.append(f"   검색 결과: {len(all_docs)}개 문서")
        result.append("-" * 60)
        
        # 각 temperature의 검색 결과 일부만 보여주기
        for i, doc in enumerate(all_docs[:3], 1):  # 상위 3개만
            result.append(f"\n   [Document {i}]")
            preview = doc.page_content[:150].replace('\n', ' ')
            result.append(f"   {preview}...")
        
        if len(all_docs) > 3:
            result.append(f"\n   ... 외 {len(all_docs) - 3}개 문서")
    
    # 결과 분석 및 추천
    result.append("\n" + "=" * 80)
    result.append("🎯 분석 및 추천")
    result.append("=" * 80)
    
    doc_counts = {temp: len(docs) for temp, docs in temp_results.items()}
    max_docs_temp = max(doc_counts, key=doc_counts.get)
    min_docs_temp = min(doc_counts, key=doc_counts.get)
    
    result.append(f"\n📈 문서 개수:")
    for temp in sorted(temperatures):
        count = doc_counts[temp]
        bar = "█" * (count // 2) if count > 0 else ""
        temp_label = temp_names.get(temp, f"Temp {temp}")
        result.append(f"   {temp} ({temp_label:15s}): {count:2d}개 {bar}")
    
    result.append(f"\n💡 추천:")
    result.append(f"   • 가장 많은 결과: Temperature {max_docs_temp} ({doc_counts[max_docs_temp]}개)")
    result.append(f"   • 가장 집중된 결과: Temperature {min_docs_temp} ({doc_counts[min_docs_temp]}개)")
    
    # 중복 분석
    all_unique_contents = set()
    for docs in temp_results.values():
        for doc in docs:
            all_unique_contents.add(doc.page_content)
    
    result.append(f"\n   • 전체 고유 문서 수: {len(all_unique_contents)}개")
    result.append(f"   • 평균 문서 수: {sum(doc_counts.values()) / len(doc_counts):.1f}개")
    
    if doc_counts[max_docs_temp] - doc_counts[min_docs_temp] > 5:
        result.append(f"\n   ⚠️  Temperature에 따라 결과가 크게 달라집니다!")
        result.append(f"      다양한 관점이 필요하면 높은 temperature를 추천합니다.")
    else:
        result.append(f"\n   ✅ Temperature에 따른 결과 차이가 크지 않습니다.")
        result.append(f"      기본값(0.7)을 사용해도 충분합니다.")
    
    result.append("\n" + "=" * 80)
    
    return "\n".join(result)


@mcp.tool()
async def retrieve_auto_optimized(
    query: str,
    retriever_mode: Literal["basic", "compression"] = "compression",
    fetch_k: int = 20,
    top_n: int = 5,
    show_process: bool = False
) -> str:
    """
    MCP가 자동으로 최적의 temperature를 선택하여 검색합니다.
    내부적으로 여러 temperature를 테스트하고 가장 좋은 결과만 반환합니다.
    
    Args:
        query: 검색 쿼리
        retriever_mode: retriever 모드
        fetch_k: 초기 검색 개수
        top_n: 최종 반환 개수
        show_process: 최적화 과정을 보여줄지 여부 (기본값: False)
        
    Returns:
        str: 자동 최적화된 검색 결과 (과정 없이 결과만)
        
    Example:
        # MCP가 알아서 최적의 temperature를 찾아서 결과만 반환
        await retrieve_auto_optimized(query="인공지능 윤리")
    """
    # 3가지 temperature로 조용히 테스트
    test_temps = [0.3, 0.7, 0.9]
    
    print(f"[V2 Auto] 쿼리: {query}")
    print(f"[V2 Auto] Temperature 자동 최적화 중... ({test_temps})")
    
    # 각 temperature로 검색 수행
    qs = QdrantRetrieverFactory()
    
    if retriever_mode == "compression":
        retriever = qs.compression_retriever(
            collection_name="RAG_Example(RAG_strategies)",
            fetch_k=fetch_k,
            top_n=top_n
        )
    else:
        retriever = qs.retriever(
            collection_name="RAG_Example(RAG_strategies)",
            fetch_k=fetch_k
        )
    
    temp_results = {}
    for temp in test_temps:
        queries = expand_query(query, temperature=temp)
        all_docs = []
        seen_contents = set()
        
        for q in queries:
            docs = retriever.invoke(q)
            for doc in docs:
                if doc.page_content not in seen_contents:
                    seen_contents.add(doc.page_content)
                    all_docs.append(doc)
        
        temp_results[temp] = all_docs
        print(f"[V2 Auto] Temperature {temp}: {len(all_docs)}개")
    
    # 최적 temperature 선택 (중간 정도의 문서 수를 선호)
    doc_counts = {temp: len(docs) for temp, docs in temp_results.items()}
    avg_count = sum(doc_counts.values()) / len(doc_counts)
    
    # 평균에 가장 가까운 temperature 선택
    optimal_temp = min(doc_counts.keys(), key=lambda t: abs(doc_counts[t] - avg_count))
    optimal_docs = temp_results[optimal_temp]
    
    print(f"[V2 Auto] 최적 Temperature 선택: {optimal_temp} ({len(optimal_docs)}개 문서)")
    
    # 결과만 깔끔하게 반환
    result = []
    
    if show_process:
        # 과정을 보여주는 경우 (옵션)
        result.append("[Enhanced Retriever V2 - Auto Optimized]")
        result.append(f"최적 Temperature: {optimal_temp} (자동 선택)")
        result.append(f"검색 결과: {len(optimal_docs)}개 문서\n")
        result.append("=" * 60)
    
    for i, doc in enumerate(optimal_docs, 1):
        result.append(f"\n=== Document {i} ===")
        result.append(doc.page_content)
        result.append("")
    
    return "\n".join(result)


if __name__ == "__main__":
    print("=" * 60)
    print("Enhanced MCP RAG Server V2")
    print("=" * 60)
    print("Port: 8103")
    print("\nFeatures:")
    print("  - Query Expansion")
    print("  - Temperature Control")
    print("  - Multiple Retriever Modes (basic/compression)")
    print("  - 🆕 Auto Temperature Comparison")
    print("  - 🆕 Auto-Optimized Search")
    print("\nAvailable Tools (5개):")
    print("  1. retrieve - 메인 검색 (모든 파라미터 제어)")
    print("  2. retrieve_basic - 간단한 기본 검색")
    print("  3. retrieve_advanced - 고급 검색 (확장 + Reranking)")
    print("  4. retrieve_with_temperature_comparison - 🆕 Temperature 비교")
    print("  5. retrieve_auto_optimized - 🆕 자동 최적화 검색")
    print("=" * 60)
    print("\nStarting server...")
    
    # Run the MCP server with SSE transport for integration with MCP clients
    mcp.run(transport="sse")

