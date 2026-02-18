from pydantic import BaseModel, Field, model_validator


class WebSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    max_results: int = Field(default=5, ge=1, le=10)


class WebSearchResult(BaseModel):
    title: str
    url: str
    content: str


class WebSearchResponse(BaseModel):
    query: str
    results: list[WebSearchResult] = Field(default_factory=list)


class LandingAnalyzeRequest(BaseModel):
    url: str | None = None
    query: str | None = None
    max_results: int = Field(default=5, ge=1, le=10)

    @model_validator(mode="after")
    def validate_input(self) -> "LandingAnalyzeRequest":
        if not self.url and not self.query:
            raise ValueError("url or query is required")
        return self


class LandingAnalyzeResponse(BaseModel):
    url: str
    title: str
    h1: list[str] = Field(default_factory=list)
    h2: list[str] = Field(default_factory=list)
    cta_buttons: list[str] = Field(default_factory=list)
    body: str = ""
    from_tavily: bool = False
