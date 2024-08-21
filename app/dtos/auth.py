from pydantic import BaseModel

class FCMTokenCreate(BaseModel):
    fcm_token: str
    device_type: str  # "android" 또는 "ios"