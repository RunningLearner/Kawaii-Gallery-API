import requests
import os
import firebase_admin
from odmantic import ObjectId
from app.database.conn import db
from app.database.models.user import User
from app.database.models.token import FCMToken
from firebase_admin import credentials, initialize_app, messaging

# FCM 서버 키는 Firebase 콘솔에서 발급받아야 합니다.
SCOPES = "https://www.googleapis.com/auth/firebase.messaging"

# 현재 파일의 위치를 기준으로 프로젝트 루트 경로를 계산
project_root = os.path.dirname(os.path.abspath(__file__))

default_app = firebase_admin.initialize_app()

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
        # 메시지 생성
        message = messaging.Message(
            notification=messaging.Notification(
                title=notification_data["title"],
                body=notification_data["body"]
            ),
            token=token.fcm_token,
            data={"post_id": str(user_id)}
        )

        # 메시지 전송
        try:
            response = messaging.send(message)
            print(f"Successfully sent message: {response}")
        except Exception as e:
            print(f"Failed to send message: {e}")

def send_like_notification_test():
    print("test started!")
    # FCM 토큰 없이 서버 요청만 테스트하기 위해 임의의 문자열을 사용
    fake_token = "c2OcCu9QTJKW6JIXYJLcSr:APA91bGhBzbqqGBivXlnpn3Oa4GBpG1jGxfYhElBshN_RFAYgbESmpq65P5KoI9dUO3yW_M6gKRCJ1c5b6IYcBPHUkD5ZrXub0kHDHaqIIC6jR-qNHqan3QPA7KXyrLJGs4iE_AkQEJ0"

    # FCM 메시지 페이로드 구성
    notification_data = {
        "title": "New Like!",
        "body": f"Your post 'testpost' received a new like.",
    }

    # 메시지 생성
    message = messaging.Message(
        notification=messaging.Notification(
            title=notification_data["title"],
            body=notification_data["body"]
        ),
        token=fake_token,  # 실제 토큰 대신 임의의 값 사용
        data={"post_id": "test"}
    )

    # 메시지 전송
    try:
        response = messaging.send(message)
        print(f"Successfully sent message: {response}")
    except firebase_admin.exceptions.FirebaseError as e:
        # 여기서 서버 응답을 확인할 수 있습니다.
        print(f"Failed to send message: {e}")
