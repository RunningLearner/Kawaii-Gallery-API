from pydantic import BaseModel, Field

class FCMTokenCreate(BaseModel):
    """
    FCM(푸시 알림) 토큰을 등록할 때 필요한 데이터 모델입니다.
    """
    fcm_token: str = Field(..., description="Firebase Cloud Messaging(FCM) 토큰", example="example_fcm_token")
