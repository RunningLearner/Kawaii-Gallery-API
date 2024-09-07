from dataclasses import asdict
import logging

import redis.asyncio as aioredis
from fastapi import FastAPI, Request
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
    logging.basicConfig(
        level=logging.INFO,  # 로그 레벨 설정
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    c = conf()
    conf_dict = asdict(c)
    logging.info(conf_dict)
    print(conf_dict)
    # 데이터 베이스 이니셜라이즈
    db.init_app(app, **conf_dict)  # 먼저 init_app을 호출하여 설정 값을 초기화
    await db.connect()

    # Redis 클라이언트 초기화
    redis_client = aioredis.Redis(host="localhost", port=6379, db=0)
    app.state.redis = redis_client  # 애플리케이션의 상태에 Redis 클라이언트 저장

    # 미들웨어 정의

    # 라우터 정의

    app.include_router(index.router)
    app.include_router(auth.router, tags=["Authentication"], prefix="/api")
    app.include_router(posts.router, tags=["Post"], prefix="/api")

    # 정적 파일 제공 경로 매핑
    app.mount("/static", StaticFiles(directory=UPLOAD_DIRECTORY), name="static")

    yield

    await redis_client.close()
    await db.close()


def create_app():
    """
    앱 함수 실행
    :return:
    """
    app = FastAPI(lifespan=lifespan)

    return app


app = create_app()


# test endpoints
@app.get("/test-notification")
def test_notification_endpoint():
    try:
        # 테스트 알림 함수 실행
        send_like_notification_test()
        return {"status": "Notification sent successfully"}
    except Exception as e:
        # 예외 발생 시 에러 메시지 반환
        print(status_code=500, detail=str(e))

@app.post("/test_set_redis")
async def set_redis_data(request: Request):
    data = await request.json()
    key = data.get("key")
    value = data.get("value")
    print(key)
    await app.state.redis.set(key, value)
    return {"message": "Data set successfully", "key": key, "value": value}

@app.get("/test_get_redis")
async def get_redis_data(key: str):
    print(key)
    value = await app.state.redis.get(key)
    print(value)
    if value:
        return {"key": key, "value": value.decode("utf-8")}
    else:
        return {"message": "Key not found"}
