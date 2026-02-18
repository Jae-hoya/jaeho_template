"""
Chenius Chat Agent - 듀얼 AI 채팅 에이전트
두 가지 관점(창의적/실용적)에서 동시에 응답 생성
"""
import asyncio
from typing import List, Tuple, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory


class CheniusChatAgent:
    """Chenius Chat 에이전트 - 듀얼 관점 채팅"""
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        # 두 가지 성격의 LLM 설정
        self.creative_llm = ChatAnthropic(
            model=model_name,
            temperature=0.9,  # 더 창의적
            max_tokens=1500
        )
        
        self.practical_llm = ChatAnthropic(
            model=model_name,
            temperature=0.3,  # 더 보수적
            max_tokens=1500
        )
        
        # 시스템 프롬프트
        self.creative_system = """당신은 창의적이고 대담한 마케팅 전문가입니다.

## 당신의 특성
- 틀을 깨는 아이디어 제시
- 트렌드를 앞서가는 제안
- 감성적이고 임팩트 있는 접근
- 리스크를 감수하더라도 차별화된 전략
- "왜 안 돼?"라는 마인드셋

## 응답 스타일
- 새로운 관점 제시
- 영감을 주는 표현
- 구체적인 창의적 예시 포함
- 업계의 상식에 도전"""

        self.practical_system = """당신은 실용적이고 안정적인 마케팅 전문가입니다.

## 당신의 특성
- 검증된 방법론 기반
- 데이터와 사례 중심
- ROI와 실행 가능성 고려
- 리스크 최소화 전략
- "어떻게 실행할까?"라는 마인드셋

## 응답 스타일
- 단계별 실행 방안
- 구체적인 수치와 근거
- 업계 best practice 참조
- 현실적인 제약 고려"""

        # 프롬프트 템플릿
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

    def _convert_history(self, history: List[dict]) -> List:
        """대화 히스토리를 LangChain 메시지 형식으로 변환"""
        messages = []
        for msg in history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg.get("content", "")))
        return messages

    async def _generate_response(
        self,
        llm: ChatAnthropic,
        system_prompt: str,
        message: str,
        history: List[dict]
    ) -> str:
        """단일 LLM 응답 생성"""
        chain = self.prompt_template | llm
        
        result = await chain.ainvoke({
            "system_prompt": system_prompt,
            "history": self._convert_history(history),
            "input": message
        })
        
        return result.content

    async def chat(
        self,
        message: str,
        history: Optional[List[dict]] = None
    ) -> Tuple[str, str]:
        """
        듀얼 관점 채팅 - 두 가지 응답 동시 생성
        
        Returns:
            Tuple[str, str]: (창의적 응답, 실용적 응답)
        """
        if history is None:
            history = []
        
        # 두 LLM 동시 호출
        creative_task = self._generate_response(
            self.creative_llm,
            self.creative_system,
            message,
            history
        )
        
        practical_task = self._generate_response(
            self.practical_llm,
            self.practical_system,
            message,
            history
        )
        
        # 병렬 실행
        creative_response, practical_response = await asyncio.gather(
            creative_task,
            practical_task
        )
        
        return creative_response, practical_response

    async def chat_with_selected(
        self,
        message: str,
        history: List[dict],
        selected_perspective: str = "creative"
    ) -> Tuple[str, str]:
        """
        이전에 선택된 관점을 고려한 채팅
        선택된 관점의 응답이 히스토리에 포함됨
        """
        return await self.chat(message, history)


# 테스트
if __name__ == "__main__":
    async def test():
        agent = CheniusChatAgent()
        
        creative, practical = await agent.chat(
            message="새로운 건강 음료 브랜드를 런칭하려고 합니다. 어떤 마케팅 전략이 좋을까요?",
            history=[]
        )
        
        print("=== 창의적 관점 ===")
        print(creative)
        print("\n=== 실용적 관점 ===")
        print(practical)
    
    asyncio.run(test())
