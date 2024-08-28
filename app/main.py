from dataclasses import asdict

import uvicorn
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.utils.settings import UPLOAD_DIRECTORY
from app.database.conn import db
from app.common.config import conf
from app.routes import index, auth, posts
from contextlib import asynccontextmanager
from app.utils.like_notification import send_like_notification_test

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 애플리케이션의 수명 주기를 관리하는 lifespan 이벤트 핸들러
    """
    c = conf()
    conf_dict = asdict(c)

    # 데이터 베이스 이니셜라이즈
    db.init_app(app, **conf_dict)  # 먼저 init_app을 호출하여 설정 값을 초기화

    await db.connect()

    # 미들웨어 정의

    # 라우터 정의

    app.include_router(index.router)
    app.include_router(auth.router, tags=["Authentication"], prefix="/api")
    app.include_router(posts.router, tags=["Post"], prefix="/api")
    
    # 정적 파일 제공 경로 매핑
    app.mount("/static", StaticFiles(directory=UPLOAD_DIRECTORY), name="static")
    yield
    await db.close()


def create_app():
    """
    앱 함수 실행
    :return:
    """
    app = FastAPI(lifespan=lifespan)

    return app

app = create_app()
# send_like_notification_test()
@app.get("/test-notification")
def test_notification_endpoint():
    try:
        # 테스트 알림 함수 실행
        send_like_notification_test()
        return {"status": "Notification sent successfully"}
    except Exception as e:
        # 예외 발생 시 에러 메시지 반환
        print(status_code=500, detail=str(e))