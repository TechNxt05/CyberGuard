from typing import List

from pydantic import BaseModel, Field


class DoubtRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    # Anonymous /resolve sessions aren't stored server-side, so the client sends the plan context.
    context: str = Field("", max_length=4000)


class DoubtResponse(BaseModel):
    answer: str


class FormAssistRequest(BaseModel):
    action_item: str = Field(..., min_length=1, max_length=1000)
    context: str = Field("", max_length=4000)


class FormAssistResponse(BaseModel):
    guidance: str
    checklist: List[str]
