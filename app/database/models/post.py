from datetime import datetime
from typing import List, Optional
from odmantic import Field, ObjectId, Model

from app.utils.time_util import get_current_time_kst

class Post(Model):
    user_id: ObjectId
    title: str
    content: str
    nick_name: str  # 작성자의 닉네임
    tags: List[str]  # 여러 문자열을 저장할 수 있는 리스트 필드
    file_urls: List[str] = []  # 여러 파일 URL을 저장할 수 있는 리스트 필드
    likes_count: int = 0  # 좋아요 수
    liked_users_id: List[ObjectId] = []  # 좋아요를 누른 사용자들의 ID 리스트
    created_at: datetime = Field(default_factory=get_current_time_kst) # 생성 시간

    model_config = {"collection": "posts"}
