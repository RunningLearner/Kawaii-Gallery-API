from datetime import datetime
from odmantic import Field, Model, ObjectId

from app.utils.time_util import get_current_time

class FCMToken(Model):
    user_id: ObjectId
    fcm_token: str
    created_at: datetime = Field(default_factory=get_current_time) # 생성 시간
 
    model_config = {"collection": "fcm_tokens"}
