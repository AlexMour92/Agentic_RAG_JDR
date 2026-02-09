from pydantic import BaseModel
from typing import Optional, List

class QuestionRequest(BaseModel):
    question: str

class ToolStep(BaseModel):
    tool_name: str
    arguments: dict
    result_preview: str

class AnswerResponse(BaseModel):
    answer: str
    steps: List[ToolStep]
    elapsed: float
    original_question: Optional[str] = None
    corrected_question: Optional[str] = None