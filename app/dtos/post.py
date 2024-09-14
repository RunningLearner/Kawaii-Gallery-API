from typing import List
from pydantic import BaseModel


# 요청 바디 모델 정의
class PostUpdate(BaseModel):
    title: str
    content: str
    tags: List[str]

# 댓글 생성 dto
class CreateComment(BaseModel):
    content: str  # 댓글 내용