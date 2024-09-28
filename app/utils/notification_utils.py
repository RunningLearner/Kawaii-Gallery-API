import requests
import os
import firebase_admin
from odmantic import AIOEngine, ObjectId
from app.database.models.post import Post
from app.database.models.user import User
from app.database.models.token import FCMToken
from firebase_admin import messaging

from app.utils.user_utils import get_user_by_object_id

# FCM 서버 키는 Firebase 콘솔에서 발급받아야 합니다.
SCOPES = "https://www.googleapis.com/auth/firebase.messaging"

# 현재 파일의 위치를 기준으로 프로젝트 루트 경로를 계산
project_root = os.path.dirname(os.path.abspath(__file__))

default_app = firebase_admin.initialize_app()

async def send_fcm_notification(engine: AIOEngine, user_id: ObjectId, post_id: ObjectId, title: str, body_template: str):
    # 게시글 데이터 가져오기
    post = await engine.find_one(Post, Post.id == post_id)

    if not post:
        print(f"Post not found for post_id: {post_id}")
        return

    # 작성자에게 등록된 FCM 토큰 가져오기
    token = await engine.find_one(FCMToken, FCMToken.user_id == post.user_id)

    if not token:
        print("No FCM tokens found for user")
        return
    
    user: User = await get_user_by_object_id(engine, user_id)

    # FCM 메시지 페이로드 구성
    notification_data = {
        "title": title,
        "body": body_template.format(user.nick_name, post.title),
    }

    # 각 FCM 토큰으로 알림 전송
    # 메시지 생성
    message = messaging.Message(
        notification=messaging.Notification(
            title=notification_data["title"],
            body=notification_data["body"]
        ),
        token=token.fcm_token,
        data={"post_id": str(post_id)}
    )

    # 메시지 전송
    response = messaging.send(message)
    print(f"알림 전송 성공 : {response}")


# 좋아요 알림 전송 함수
async def send_like_notification(engine: AIOEngine, user_id: ObjectId, post_id: ObjectId):
    title = "좋아요!"
    body_template = "'{}'님이 당신의 게시글 '{}'을(를) 좋아합니다."
    await send_fcm_notification(engine, user_id, post_id, title, body_template)


# 댓글 알림 전송 함수
async def send_comment_notification(engine: AIOEngine, user_id: ObjectId, post_id: ObjectId):
    title = "댓글!"
    body_template = "'{}'님이 당신의 게시글 '{}'에 댓글을 달았습니다."
    await send_fcm_notification(engine, user_id, post_id, title, body_template)
