"""
Brief Reader Agent - 클라이언트 브리프 분석 에이전트
브리프 문서를 분석하여 핵심 정보 추출
"""
import json
import asyncio
from typing import Optional, List
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field


class BriefSummary(BaseModel):
    """브리프 요약 스키마"""
    company: Optional[str] = Field(default=None, description="회사명")
    product: Optional[str] = Field(default=None, description="제품/서비스명")
    target: Optional[str] = Field(default=None, description="타겟 고객")
    problem: Optional[str] = Field(default=None, description="해결하려는 문제")
    usp: Optional[str] = Field(default=None, description="차별점/USP")
    tone: Optional[str] = Field(default=None, description="원하는 톤앤매너")
    goals: List[str] = Field(default=[], description="마케팅 목표")
    keywords: List[str] = Field(default=[], description="핵심 키워드")
    insights: Optional[str] = Field(default=None, description="전략적 인사이트")


class BriefReaderAgent:
    """Brief Reader 에이전트 - 브리프 문서 분석"""
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        self.llm = ChatAnthropic(
            model=model_name,
            temperature=0.2,  # 정확한 분석을 위해 낮은 temperature
            max_tokens=2000
        )
        self.parser = JsonOutputParser(pydantic_object=BriefSummary)
        
        self.system_template = """당신은 마케팅 전략가입니다. 
클라이언트 브리프를 분석하여 핵심 정보를 추출하고 전략적 인사이트를 제공합니다.

## 분석 가이드라인

### 추출할 정보
1. **회사명 (company)**: 클라이언트 회사/브랜드명
2. **제품/서비스 (product)**: 마케팅 대상 제품이나 서비스
3. **타겟 고객 (target)**: 주요 타겟 고객층 (인구통계, 심리 특성)
4. **해결 문제 (problem)**: 고객이 겪는 문제나 니즈
5. **차별점 (usp)**: 경쟁사 대비 독특한 가치 제안
6. **톤앤매너 (tone)**: 원하는 커뮤니케이션 스타일
7. **목표 (goals)**: 구체적인 마케팅/비즈니스 목표
8. **키워드 (keywords)**: 브랜드/캠페인 핵심 키워드

### 인사이트 제공
- 브리프에서 놓친 부분 지적
- 잠재적 기회 포인트
- 주의해야 할 리스크
- 추천 마케팅 방향

{format_instructions}

반드시 JSON 형식으로만 응답하세요. 정보가 없는 필드는 null로 처리하세요."""

        self.human_template = """다음 클라이언트 브리프를 분석해주세요:

---
{brief_content}
---

위 브리프를 분석하여 핵심 정보를 추출하고, 마케팅 전략가로서의 인사이트를 제공해주세요."""

    async def analyze(self, content: str) -> dict:
        """브리프 분석"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_template),
            ("human", self.human_template)
        ])
        
        chain = prompt | self.llm | self.parser
        
        try:
            result = await chain.ainvoke({
                "format_instructions": self.parser.get_format_instructions(),
                "brief_content": content
            })
            
            # 결과 정규화
            if isinstance(result, dict):
                return result
            else:
                return {"insights": str(result)}
                
        except Exception as e:
            # JSON 파싱 실패 시 대체 처리
            fallback_prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_template),
                ("human", self.human_template)
            ])
            fallback_chain = fallback_prompt | self.llm
            
            raw_result = await fallback_chain.ainvoke({
                "format_instructions": self.parser.get_format_instructions(),
                "brief_content": content
            })
            
            try:
                # 수동 JSON 추출 시도
                response_content = raw_result.content
                start = response_content.find('{')
                end = response_content.rfind('}') + 1
                if start != -1 and end > start:
                    parsed = json.loads(response_content[start:end])
                    return parsed
            except:
                pass
            
            return {"insights": raw_result.content}

    async def analyze_with_questions(self, content: str) -> dict:
        """브리프 분석 + 추가 질문 생성"""
        
        base_result = await self.analyze(content)
        
        # 빈 필드에 대한 질문 생성
        questions = []
        field_questions = {
            "company": "클라이언트 회사/브랜드명이 무엇인가요?",
            "product": "마케팅할 제품이나 서비스는 무엇인가요?",
            "target": "주요 타겟 고객층은 누구인가요?",
            "problem": "고객이 겪는 문제나 니즈는 무엇인가요?",
            "usp": "경쟁사 대비 차별점은 무엇인가요?",
            "goals": "구체적인 마케팅 목표는 무엇인가요?"
        }
        
        for field, question in field_questions.items():
            value = base_result.get(field)
            if not value or (isinstance(value, list) and len(value) == 0):
                questions.append(question)
        
        base_result["follow_up_questions"] = questions
        return base_result


# 테스트
if __name__ == "__main__":
    async def test():
        agent = BriefReaderAgent()
        
        sample_brief = """
        [클라이언트 브리프]
        
        회사: ABC 헬스케어
        제품: 프리미엄 수면 보조제 "딥슬립"
        
        배경:
        현대인의 수면 문제가 심각해지고 있습니다. 특히 30-40대 직장인들의 
        불면증 비율이 높아지고 있어, 자연 성분 기반의 수면 보조제 시장이 
        성장하고 있습니다.
        
        타겟:
        - 30-45세 직장인
        - 스트레스로 인한 수면 장애 경험자
        - 건강에 관심이 많고 자연 성분 선호
        
        차별점:
        - 100% 천연 식물 추출물
        - 습관성 없음
        - 다음날 피로감 없음
        
        목표:
        - 브랜드 인지도 구축
        - 온라인 판매 월 1억 달성
        - 건강기능식품 카테고리 Top 10 진입
        
        톤앤매너:
        신뢰감 있고 전문적이면서도 친근한 느낌
        """
        
        result = await agent.analyze(sample_brief)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    asyncio.run(test())
