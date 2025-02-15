from pydantic import BaseModel, conlist
from typing import List

class Memory(BaseModel):
    title: str
    description: str

class QAPair(BaseModel):
    question: str
    answer: str

class StoryCreate(BaseModel):
    memories: conlist(Memory, min_length=3, max_length=3)
    personal_qa: conlist(QAPair, min_length=3, max_length=3)

class GeneratedContent(BaseModel):
    title: str
    scenes: List[dict]
    bloopers: List[str]