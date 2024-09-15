from datetime import datetime
from typing import List, Optional
from odmantic import Field, ObjectId, Model

from app.utils.time_util import get_current_time


class Comment(Model):
    user_id: ObjectId  # 댓글 작성자의 ID
    post_id: ObjectId  # 댓글 작성자의 ID
    content: str  # 댓글 내용
    nick_name: str  # 댓글 작성자의 닉네임
    liked_by: List[ObjectId] = []  # 댓글에 좋아요를 누른 사용자들의 ID 리스트
    created_at: datetime = Field(default_factory=get_current_time) # 생성 시간
    # 대댓기능은 보류
    # replies: Optional[List["Comment"]] = []  # 댓글에 대한 댓글 리스트

    model_config = {"collection": "comments"}
