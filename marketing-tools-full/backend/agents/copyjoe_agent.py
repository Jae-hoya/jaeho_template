"""
Copyjoe Agent - 마케팅 카피 생성 에이전트
LangChain + Anthropic Claude
"""
import json
import asyncio
from typing import Optional, List
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field


class CopyItem(BaseModel):
    """카피 아이템 스키마"""
    copy: str = Field(description="생성된 카피 문구")
    rationale: str = Field(description="카피 작성 이유")


class CopyList(BaseModel):
    """카피 리스트 스키마"""
    copies: List[CopyItem] = Field(description="생성된 카피 목록")


class CopyjoeAgent:
    """카피조 에이전트 - 마케팅 카피 생성"""
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        self.llm = ChatAnthropic(
            model=model_name,
            temperature=0.8,
            max_tokens=2000
        )
        self.parser = JsonOutputParser(pydantic_object=CopyList)
        
        self.system_template = """당신은 마케팅 카피라이터 "카피조"입니다.

## 카피의 목적
- 브랜드를 기억하게 하기
- 제품을 클릭하게 하기
- 장바구니에 담게 하기
- 상담을 신청하게 하기

## 좋은 카피의 특징
- 고객의 언어를 쓴다
- 길지 않다
- 구체적이다
- 감정을 건드린다
- 차별점이 명확하다

## 카피 유형별 가이드
- 슬로건형: 브랜드 이미지를 각인시키는 문장. 짧고 임팩트 있게.
- 문제 해결형: 고객의 고민을 건드리는 방식. 공감에서 시작.
- 혜택 강조형: 결과를 먼저 보여주는 방식. 구체적인 숫자나 변화.
- CTA형: 행동을 직접적으로 요구. 긴박감과 혜택 결합.

{format_instructions}

반드시 JSON 형식으로만 응답하세요."""

        self.type_prompts = {
            "slogan": "슬로건형 카피를 작성하세요. 브랜드 이미지를 각인시키는 짧고 임팩트 있는 문장입니다.",
            "problem": "문제 해결형 카피를 작성하세요. 고객의 고민에 공감하고 해결책을 제시하는 방식입니다.",
            "benefit": "혜택 강조형 카피를 작성하세요. 고객이 얻을 결과와 변화를 구체적으로 보여주는 방식입니다.",
            "cta": "CTA형 카피를 작성하세요. 지금 바로 행동하게 만드는 직접적인 요구입니다."
        }

    async def generate(
        self,
        copy_type: str,
        brand: str,
        target: Optional[str] = "",
        benefit: Optional[str] = "",
        problem: Optional[str] = "",
        rag_content: Optional[str] = ""
    ) -> List[dict]:
        """카피 생성"""
        
        type_instruction = self.type_prompts.get(copy_type, self.type_prompts["slogan"])
        
        human_template = f"""{type_instruction}

## 입력 정보
- 브랜드/제품: {brand}
- 타겟 고객: {target if target else "미지정"}
- 핵심 혜택: {benefit if benefit else "미지정"}
- 고객 문제/고민: {problem if problem else "미지정"}
{f"- 참고 자료: {rag_content}" if rag_content else ""}

5개의 카피를 생성하세요. 각 카피는 서로 다른 접근 방식을 사용해야 합니다."""

        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                self.system_template,
                partial_variables={"format_instructions": self.parser.get_format_instructions()}
            ),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        
        chain = prompt | self.llm | self.parser
        
        try:
            result = await chain.ainvoke({"input": human_template})
            
            # 결과 형식 정규화
            if isinstance(result, dict) and "copies" in result:
                return result["copies"]
            elif isinstance(result, list):
                return result
            else:
                return [{"copy": str(result), "rationale": "생성 완료"}]
                
        except Exception as e:
            # JSON 파싱 실패 시 대체 처리
            fallback_chain = prompt | self.llm
            raw_result = await fallback_chain.ainvoke({"input": human_template})
            
            try:
                # 수동 JSON 추출 시도
                content = raw_result.content
                start = content.find('[')
                end = content.rfind(']') + 1
                if start != -1 and end > start:
                    parsed = json.loads(content[start:end])
                    return parsed
            except:
                pass
            
            return [{"copy": raw_result.content, "rationale": "파싱 실패 - 원본 응답"}]


# 테스트
if __name__ == "__main__":
    async def test():
        agent = CopyjoeAgent()
        result = await agent.generate(
            copy_type="slogan",
            brand="스타벅스",
            target="20-30대 직장인",
            benefit="프리미엄 커피 경험",
            problem="피로감, 집중력 저하"
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    asyncio.run(test())
