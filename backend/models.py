from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FieldAnalysis(BaseModel):
    field_name: str
    field_type: str
    suggested_value: Optional[str] = None
    instructions: str
    warning: Optional[str] = None
    position: Optional[dict] = None  # {x: float, y: float} as percentages


class AnalysisResult(BaseModel):
    id: int
    image_path: str
    user_context: str
    fields: list[FieldAnalysis]
    summary: Optional[str] = None
    created_at: datetime
    is_mock: bool = False


class AnalysisListItem(BaseModel):
    id: int
    user_context: str
    field_count: int
    created_at: datetime
    thumbnail_path: Optional[str] = None


class AnalyzeRequest(BaseModel):
    user_context: str
