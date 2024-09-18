from datetime import datetime
from odmantic import Field, Model

from app.utils.time_util import get_current_time


class User(Model):
    nick_name: str
    email: str
    feather: int = 0  # 사용자의 깃털 개수
    is_admin: bool = False  # 관리자 여부, 기본값 False
    created_at: datetime = Field(default_factory=get_current_time) # 생성 시간
    profile_image_url: str  # 파일 url 저장 필드

    model_config = {"collection": "users"}
