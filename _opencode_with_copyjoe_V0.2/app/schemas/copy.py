from enum import Enum
from difflib import get_close_matches

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import SourceItem


class Objective(str, Enum):
    brand_memory = "brand_memory"
    click = "click"
    add_to_cart = "add_to_cart"
    consultation = "consultation"


OBJECTIVE_DESCRIPTIONS: dict[Objective, str] = {
    Objective.brand_memory: "브랜드 인지/기억 강화. 슬로건, 반복 노출형 문구에 적합.",
    Objective.click: "광고/랜딩 클릭 유도. 짧고 즉시 반응하는 CTA 중심.",
    Objective.add_to_cart: "장바구니 담기 유도. 혜택/가격/리스크 완화 문구 중심.",
    Objective.consultation: "상담/문의 전환 유도. 신뢰성과 전문성 강조.",
}


class Style(str, Enum):
    head = "head"
    body = "body"
    cta = "cta"
    slogan = "slogan"
    sns = "sns"
    description = "description"


ALL_STYLES = [
    Style.head,
    Style.body,
    Style.cta,
    Style.slogan,
    Style.sns,
    Style.description,
]


SUPPORTED_LANGUAGE_CODES: tuple[str, ...] = (
    "ko",
    "en",
    "ja",
    "zh-CN",
    "zh-TW",
    "es",
    "fr",
    "de",
    "pt-BR",
    "vi",
    "id",
    "th",
)

LANGUAGE_ALIASES: dict[str, str] = {
    "korean": "ko",
    "ko-kr": "ko",
    "kr": "ko",
    "한국어": "ko",
    "english": "en",
    "en-us": "en",
    "en-gb": "en",
    "영어": "en",
    "japanese": "ja",
    "ja-jp": "ja",
    "jp": "ja",
    "일본어": "ja",
    "chinese": "zh-CN",
    "zh": "zh-CN",
    "zh-hans": "zh-CN",
    "중국어": "zh-CN",
    "중국어-간체": "zh-CN",
    "zh-tw": "zh-TW",
    "zh-hant": "zh-TW",
    "중국어-번체": "zh-TW",
    "spanish": "es",
    "es-es": "es",
    "french": "fr",
    "fr-fr": "fr",
    "german": "de",
    "de-de": "de",
    "portuguese": "pt-BR",
    "pt": "pt-BR",
    "pt-br": "pt-BR",
    "vietnamese": "vi",
    "indonesian": "id",
    "thai": "th",
}


def normalize_language_code(value: str) -> str:
    raw = value.strip()
    lowered = raw.lower()

    if lowered in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[lowered]

    canonical_map = {code.lower(): code for code in SUPPORTED_LANGUAGE_CODES}
    if lowered in canonical_map:
        return canonical_map[lowered]

    compact = _compact_language_key(raw)
    if compact in _LANGUAGE_LOOKUP:
        return _LANGUAGE_LOOKUP[compact]

    candidates = list(_LANGUAGE_LOOKUP.keys())
    close_match = get_close_matches(compact, candidates, n=1, cutoff=0.84)
    if close_match:
        return _LANGUAGE_LOOKUP[close_match[0]]

    raise ValueError(
        "Unsupported language. Use one of: "
        + ", ".join(SUPPORTED_LANGUAGE_CODES)
        + ". You can also use aliases like 'english', 'korean', 'ja-jp'."
    )


def _compact_language_key(value: str) -> str:
    return value.strip().lower().replace("-", "").replace("_", "").replace(" ", "")


def _build_language_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}

    for code in SUPPORTED_LANGUAGE_CODES:
        lookup[_compact_language_key(code)] = code

    for alias, mapped in LANGUAGE_ALIASES.items():
        lookup[_compact_language_key(alias)] = mapped

    return lookup


_LANGUAGE_LOOKUP = _build_language_lookup()


class CopyGenerateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_name": "Copyjoe",
                "target_audience": "퍼포먼스 마케터",
                "pain_point": "카피 작성 속도가 느리고 A/B 테스트 문구를 빨리 만들기 어렵다",
                "differentiator": "LangGraph 기반 RAG+Tavily 결합으로 근거 중심 카피를 빠르게 생성한다",
                "tone": "신뢰형",
                "objective": "click",
                "styles": ["head", "body", "cta", "slogan", "sns", "description"],
                "channel": "상세페이지",
                "language": "ko",
                "web_search_mode": False,
                "use_rag": True,
                "top_k": 5,
            }
        }
    )

    product_name: str = Field(min_length=1, max_length=200, description="제품/서비스명")
    target_audience: str = Field(min_length=1, max_length=200, description="핵심 타깃 고객군")
    pain_point: str = Field(
        min_length=1,
        max_length=500,
        description=(
            "고객이 겪는 핵심 문제를 구체적으로 입력하세요. "
            "증상 + 손실 + 감정을 함께 적으면 카피 품질이 좋아집니다."
        ),
    )
    differentiator: str = Field(
        min_length=1,
        max_length=500,
        description=(
            "경쟁 대비 차별점. 기능/근거/결과를 함께 적으세요. "
            "예: 'RAG+웹근거로 최신성과 신뢰를 동시에 확보'"
        ),
    )
    tone: str = Field(default="신뢰형", min_length=1, max_length=100, description="문체/톤")
    objective: Objective = Field(
        description=(
            "카피 목표. brand_memory(인지), click(클릭), "
            "add_to_cart(장바구니), consultation(상담)"
        )
    )
    styles: list[Style] = Field(default_factory=lambda: list(ALL_STYLES))
    channel: str = Field(
        default="상세페이지",
        min_length=1,
        max_length=100,
        description=(
            "노출 채널. 예: 상세페이지, 퍼포먼스 광고 랜딩, 인스타 피드, 유튜브 쇼츠, 이메일 캠페인"
        ),
    )
    language: str = Field(
        default="ko",
        min_length=2,
        max_length=20,
        description=(
            "출력 언어 코드(BCP-47 스타일). 지원: "
            "ko, en, ja, zh-CN, zh-TW, es, fr, de, pt-BR, vi, id, th"
        ),
    )
    web_search_mode: bool = False
    use_rag: bool = True
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("styles")
    @classmethod
    def deduplicate_styles(cls, value: list[Style]) -> list[Style]:
        deduped = list(dict.fromkeys(value))
        if not deduped:
            return list(ALL_STYLES)
        return deduped

    @field_validator("language")
    @classmethod
    def normalize_language_code(cls, value: str) -> str:
        return normalize_language_code(value)


class CopyGenerateResponse(BaseModel):
    head: str = ""
    body: str = ""
    cta: str = ""
    slogan: str = ""
    sns: str = ""
    description: str = ""
    storyboard_outline: list[str] = Field(default_factory=list)
    rationale: str = ""
    sources: list[SourceItem] = Field(default_factory=list)


class CopyLiteRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "광고 클릭률이 떨어져서 빠르게 고품질 카피가 필요해요. 핵심은 신뢰성과 속도입니다.",
                "styles": ["head", "cta", "sns"],
                "language": "ko",
                "objective": "click",
                "channel": "메타 광고 랜딩",
                "landing_url": "https://example.com",
                "web_search_mode": False,
                "use_rag": True,
                "top_k": 5,
            }
        }
    )

    prompt: str = Field(
        min_length=5,
        max_length=8000,
        description="자유 서술형 brief. 제품/고객/문제/강점을 자연어로 짧게 입력",
    )
    styles: list[Style] = Field(default_factory=lambda: [Style.head, Style.body, Style.cta])
    language: str = Field(default="ko", min_length=2, max_length=20)
    objective: Objective | None = Field(default=None, description="비워두면 click으로 자동 설정")
    channel: str | None = Field(default=None, max_length=100, description="비워두면 '상세페이지' 기본값")
    landing_url: str | None = Field(
        default=None,
        max_length=2000,
        description="입력 시 Playwright 렌더링 기반 랜딩 컨텍스트를 카피 생성에 반영",
    )
    landing_query: str | None = Field(
        default=None,
        max_length=500,
        description="landing_url이 없을 때 검색어로 후보 랜딩을 찾은 뒤 렌더링 분석",
    )
    web_search_mode: bool = False
    use_rag: bool = True
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("styles")
    @classmethod
    def deduplicate_styles(cls, value: list[Style]) -> list[Style]:
        deduped = list(dict.fromkeys(value))
        if not deduped:
            return [Style.head, Style.body, Style.cta]
        return deduped

    @field_validator("language")
    @classmethod
    def normalize_language_code(cls, value: str) -> str:
        return normalize_language_code(value)


class CopyLiteParsedInput(BaseModel):
    product_name: str = Field(default="")
    target_audience: str = Field(default="")
    pain_point: str = Field(default="")
    differentiator: str = Field(default="")
    tone: str = Field(default="신뢰형")


class CopyLiteResponse(BaseModel):
    assistant_message: str
    assumptions: list[str] = Field(default_factory=list)
    normalized_request: CopyGenerateRequest
    result: CopyGenerateResponse


class CopyStructuredOutput(BaseModel):
    head: str = Field(description="광고 헤드라인 1개")
    body: str = Field(description="핵심 설득 본문")
    cta: str = Field(description="행동 유도 문구")
    slogan: str = Field(description="짧은 슬로건")
    sns: str = Field(description="SNS 포스트용 짧은 카피")
    description: str = Field(description="채널 설명용 카피")
    storyboard_outline: list[str] = Field(description="스토리보드 콘티 초안")
    rationale: str = Field(description="카피 선택 근거")
