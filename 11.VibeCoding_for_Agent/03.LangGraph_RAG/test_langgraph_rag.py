"""Test script for LangGraph RAG system"""

import sys
import os

from langgraph_rag import LangGraphRAG


def test_direct_question():
    """Test direct question (no search needed)"""
    print("\n" + "=" * 80)
    print("Test 1: Direct Question (No Search)")
    print("=" * 80)

    rag = LangGraphRAG(debug=True)
    try:
        question = "안녕하세요"
        answer = rag.run(question)
        print(f"\nQuestion: {question}")
        print(f"Answer: {answer}")
        assert answer, "Answer should not be empty"
        print("\n✓ Test 1 PASSED")
    finally:
        rag.close()


def test_search_question():
    """Test search question (requires search)"""
    print("\n" + "=" * 80)
    print("Test 2: Search Question")
    print("=" * 80)

    rag = LangGraphRAG(debug=True)
    try:
        question = "의사 전용 대출 상품 추천해줘"
        answer = rag.run(question)
        print(f"\nQuestion: {question}")
        print(f"Answer: {answer}")
        assert answer, "Answer should not be empty"
        print("\n✓ Test 2 PASSED")
    finally:
        rag.close()


def test_low_interest_search():
    """Test low interest rate search"""
    print("\n" + "=" * 80)
    print("Test 3: Low Interest Rate Search")
    print("=" * 80)

    rag = LangGraphRAG(debug=True)
    try:
        question = "저금리 대출 상품을 찾고 있어요"
        answer = rag.run(question)
        print(f"\nQuestion: {question}")
        print(f"Answer: {answer}")
        assert answer, "Answer should not be empty"
        print("\n✓ Test 3 PASSED")
    finally:
        rag.close()


if __name__ == "__main__":
    # Handle Windows UTF-8 encoding
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    print("Starting LangGraph RAG Tests...")

    try:
        test_direct_question()
        test_search_question()
        test_low_interest_search()

        print("\n" + "=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
