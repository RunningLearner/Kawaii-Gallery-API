from typing import List
from pydantic import BaseModel, Field


# 요청 바디 모델 정의
class PostUpdate(BaseModel):
    title: str = Field(..., description="게시글의 제목", example="업데이트된 게시글 제목")
    content: str = Field(..., description="게시글의 내용", example="업데이트된 게시글 내용입니다.")
    tags: List[str] = Field(..., description="게시글에 포함할 태그 목록", example=["Python", "FastAPI"])

# 댓글 생성 dto
class CreateComment(BaseModel):
    content: str = Field(..., description="생성할 댓글의 내용", example="이 게시글 정말 유익하네요!")

# 댓글 수정 dto
class UpdateComment(BaseModel):
    content: str = Field(..., description="수정할 댓글의 내용", example="이 댓글을 수정했습니다.")
