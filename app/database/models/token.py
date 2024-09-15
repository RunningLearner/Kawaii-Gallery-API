from datetime import datetime
from odmantic import Field, Model, ObjectId

from app.utils.time_util import get_current_time_kst

class FCMToken(Model):
    user_id: ObjectId
    fcm_token: str
    device_type: str  # 기기 유형 (예: "android", "ios")
    created_at: datetime = Field(get_current_time_kst) # 생성 시간
 
    model_config = {"collection": "fcm_tokens"}
