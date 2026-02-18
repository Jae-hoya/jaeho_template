from pydantic import BaseModel, Field

from app.schemas.copy import CopyGenerateResponse


class ExportDocxRequest(BaseModel):
    file_name: str = Field(default="copyjoe_output.docx", max_length=120)
    result: CopyGenerateResponse


class ExportMarkdownRequest(BaseModel):
    file_name: str = Field(default="copyjoe_output.md", max_length=120)
    result: CopyGenerateResponse


class ExportDocRequest(BaseModel):
    file_name: str = Field(default="copyjoe_output.doc", max_length=120)
    result: CopyGenerateResponse
