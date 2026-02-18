from pydantic import BaseModel, Field


class FieldGuideItem(BaseModel):
    key: str
    title: str
    description: str
    writing_tip: str
    good_examples: list[str] = Field(default_factory=list)


class ObjectiveGuideItem(BaseModel):
    value: str
    label: str
    when_to_use: str
    primary_kpi: str


class LanguageGuideItem(BaseModel):
    code: str
    name: str
    aliases: list[str] = Field(default_factory=list)


class CopyFormGuideResponse(BaseModel):
    fields: list[FieldGuideItem]
    objectives: list[ObjectiveGuideItem]
    channels: list[str]
    language_options: list[LanguageGuideItem]
