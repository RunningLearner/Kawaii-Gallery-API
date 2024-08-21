from odmantic import Model, ObjectId

class FCMToken(Model):
    user_id: ObjectId
    fcm_token: str
    device_type: str  # 기기 유형 (예: "android", "ios")
 
    model_config = {"collection": "fcm_tokens"}
