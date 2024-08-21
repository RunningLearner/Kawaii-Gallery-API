import requests
from odmantic import ObjectId
from app.database.conn import db
from app.database.models.user import FCMToken, User

# FCM 서버 키는 Firebase 콘솔에서 발급받아야 합니다.
FCM_SERVER_KEY = "your_fcm_server_key_here"
FCM_URL = "https://fcm.googleapis.com/fcm/send"

async def send_like_notification(user_id: ObjectId, post_title: str):
    # 해당 사용자에게 등록된 모든 FCM 토큰 가져오기
    tokens = await db.engine.find(FCMToken, FCMToken.user_id == user_id)

    if not tokens:
        print("No FCM tokens found for user")
        return

    # FCM 메시지 페이로드 구성
    notification_data = {
        "title": "New Like!",
        "body": f"Your post '{post_title}' received a new like.",
    }

    # 각 FCM 토큰에 대해 알림 전송
    for token in tokens:
        payload = {
            "to": token.fcm_token,
            "notification": notification_data,
            "data": {"post_id": str(user_id)},
        }

        headers = {
            "Authorization": f"key={FCM_SERVER_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(FCM_URL, json=payload, headers=headers)

        if response.status_code == 200:
            print(f"Notification sent to {token.device_type} device successfully.")
        else:
            print(f"Failed to send notification: {response.status_code}, {response.text}")
