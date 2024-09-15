from datetime import datetime
from odmantic import Field, Model

from app.utils.time_util import get_current_time_kst


class User(Model):
    nick_name: str
    email: str
    feather: int = 0  # 사용자의 깃털 개수
    created_at: datetime = Field(default_factory=get_current_time_kst) # 생성 시간

    model_config = {"collection": "users"}
