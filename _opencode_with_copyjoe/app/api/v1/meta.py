from fastapi import APIRouter

from app.schemas.meta import (
    CopyFormGuideResponse,
    FieldGuideItem,
    LanguageGuideItem,
    ObjectiveGuideItem,
)

router = APIRouter()


@router.get("/meta/copy-form-guide", response_model=CopyFormGuideResponse)
def copy_form_guide() -> CopyFormGuideResponse:
    return CopyFormGuideResponse(
        fields=[
            FieldGuideItem(
                key="pain_point",
                title="고객 문제(pain_point)",
                description=(
                    "고객이 현재 겪는 성과 저하 문제를 적습니다. 단순 기능 불만보다 "
                    "비즈니스 지표 손실(CTR, CVR, CAC 등)이 드러나야 설득력이 올라갑니다."
                ),
                writing_tip="문제 상황 + 지표 손실 + 긴급성을 1~2문장으로 구체화하세요.",
                good_examples=[
                    "CTR 하락과 소재 피로로 CAC가 상승해, 동일 예산 대비 리드 수가 지속적으로 감소하고 있다.",
                    "A/B 테스트 주기를 줄여야 하는데 카피 제작 리드타임이 길어 캠페인 최적화 타이밍을 놓친다.",
                ],
            ),
            FieldGuideItem(
                key="differentiator",
                title="차별점(differentiator)",
                description=(
                    "경쟁 서비스 대비 우리 솔루션의 우위 근거입니다. "
                    "'무엇을 잘한다'가 아니라 '왜 성과가 나오는지'를 설명해야 합니다."
                ),
                writing_tip="핵심 기능 + 데이터/근거 + 기대 성과를 한 문장으로 연결하세요.",
                good_examples=[
                    "LangGraph 기반으로 RAG 문서 근거와 Tavily 최신 웹 근거를 결합해, 전환형 카피의 정확도와 생성 속도를 동시에 확보한다.",
                    "브랜드 내부 자료와 시장 컨텍스트를 함께 반영해, 메시지 일관성을 유지하면서도 채널별 성과형 문구를 빠르게 생성한다.",
                ],
            ),
            FieldGuideItem(
                key="objective",
                title="목표(objective)",
                description="카피가 유도해야 할 최종 행동 목표입니다.",
                writing_tip="캠페인의 1차 KPI를 기준으로 1개만 고르세요.",
                good_examples=[
                    "클릭이 1차 KPI면 click",
                    "상담 신청이 1차 KPI면 consultation",
                ],
            ),
            FieldGuideItem(
                key="channel",
                title="채널(channel)",
                description="카피가 노출될 지면/포맷을 의미합니다.",
                writing_tip="실제 매체/포맷명을 쓰면 문장 길이와 톤이 더 정확해집니다.",
                good_examples=[
                    "상세페이지",
                    "메타 광고 랜딩",
                    "인스타 피드",
                    "유튜브 쇼츠",
                    "이메일 캠페인",
                ],
            ),
            FieldGuideItem(
                key="language",
                title="언어(language)",
                description="출력 카피의 언어 코드입니다.",
                writing_tip="언어 코드는 BCP-47 스타일로 입력하세요. 예: ko, en, ja, zh-CN",
                good_examples=[
                    "ko (한국어)",
                    "en (English)",
                    "ja (Japanese)",
                    "zh-CN (중국어 간체)",
                    "pt-BR (브라질 포르투갈어)",
                ],
            ),
            FieldGuideItem(
                key="top_k",
                title="근거 개수(top_k)",
                description="RAG/웹 검색에서 참고할 근거 문서 개수입니다.",
                writing_tip="일반적으로 3~8을 권장하고, 기본값 5부터 시작하세요.",
                good_examples=["3", "5", "8"],
            ),
        ],
        objectives=[
            ObjectiveGuideItem(
                value="brand_memory",
                label="브랜드 기억",
                when_to_use="브랜드 인지도/기억을 남기고 싶을 때",
                primary_kpi="브랜드 검색량, 광고 회상",
            ),
            ObjectiveGuideItem(
                value="click",
                label="클릭 유도",
                when_to_use="광고/랜딩 진입을 늘리고 싶을 때",
                primary_kpi="CTR, 클릭수",
            ),
            ObjectiveGuideItem(
                value="add_to_cart",
                label="장바구니 추가",
                when_to_use="즉시 구매 의도 신호를 늘리고 싶을 때",
                primary_kpi="ATC 수, ATC 전환율",
            ),
            ObjectiveGuideItem(
                value="consultation",
                label="상담 신청",
                when_to_use="고관여 상품의 문의/상담 전환이 목표일 때",
                primary_kpi="리드 수, 상담 신청 전환율",
            ),
        ],
        channels=[
            "상세페이지",
            "퍼포먼스 광고 랜딩",
            "메타 광고 랜딩",
            "인스타 피드",
            "유튜브 쇼츠",
            "이메일 캠페인",
            "카카오 친구톡",
            "네이버 블로그",
        ],
        language_options=[
            LanguageGuideItem(code="ko", name="Korean", aliases=["한국어", "korean", "ko-kr", "kr"]),
            LanguageGuideItem(code="en", name="English", aliases=["영어", "english", "en-us", "en-gb"]),
            LanguageGuideItem(code="ja", name="Japanese", aliases=["일본어", "japanese", "ja-jp", "jp"]),
            LanguageGuideItem(code="zh-CN", name="Chinese (Simplified)", aliases=["중국어", "zh", "zh-hans"]),
            LanguageGuideItem(code="zh-TW", name="Chinese (Traditional)", aliases=["zh-tw", "zh-hant"]),
            LanguageGuideItem(code="es", name="Spanish", aliases=["spanish", "es-es"]),
            LanguageGuideItem(code="fr", name="French", aliases=["french", "fr-fr"]),
            LanguageGuideItem(code="de", name="German", aliases=["german", "de-de"]),
            LanguageGuideItem(code="pt-BR", name="Portuguese (Brazil)", aliases=["portuguese", "pt", "pt-br"]),
            LanguageGuideItem(code="vi", name="Vietnamese", aliases=["vietnamese"]),
            LanguageGuideItem(code="id", name="Indonesian", aliases=["indonesian"]),
            LanguageGuideItem(code="th", name="Thai", aliases=["thai"]),
        ],
    )
