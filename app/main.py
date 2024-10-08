from dataclasses import asdict
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis.asyncio as aioredis
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from app.utils.settings import UPLOAD_DIRECTORY
from app.database.conn import init_mongo, close_mongo,init_redis,close_redis
from app.common.config import conf
from app.routes import index, auth, posts, user
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 애플리케이션의 수명 주기를 관리하는 lifespan 이벤트 핸들러
    """
    logging.basicConfig(
        level=logging.INFO,  # 로그 레벨 설정
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),  # 콘솔 출력
            logging.FileHandler("app.log", mode="a", encoding="utf-8"),  # 파일 출력
        ],
    )

    c = conf()
    print(c)
    # 데이터 베이스 이니셜라이즈
    # db.init_app(app, **conf_dict)  # 먼저 init_app을 호출하여 설정 값을 초기화
    # await db.connect()
    app.state.mongo_engine = await init_mongo(db_url=c.DB_URL, db_name=c.DB_NAME)

    # Redis 클라이언트 초기화
    app.state.redis_client = await init_redis(redis_url=c.redis_url)

    # 미들웨어 정의

    # 정적 파일 제공 경로 매핑
    app.mount("/static", StaticFiles(directory=UPLOAD_DIRECTORY), name="static")

    yield

    # await redis_client.close()
    # await db.close()
    await close_mongo(app.state.mongo_engine)
    await close_redis(app.state.redis)


def create_app():
    """
    앱 함수 실행
    :return:
    """
    app = FastAPI(lifespan=lifespan)

    return app


app = create_app()


# 미들웨어 추가
class CharsetMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        # 모든 응답에 charset=utf-8 추가
        response.headers["Content-Type"] = (
            response.headers.get("Content-Type", "application/json") + "; charset=utf-8"
        )
        return response


# 미들웨어 등록
app.add_middleware(CharsetMiddleware)

# 라우터 정의
app.include_router(index.router)
app.include_router(auth.router, tags=["Authentication"], prefix="/api")
app.include_router(posts.router, tags=["Post"], prefix="/api")
app.include_router(user.router, tags=["User"], prefix="/api")


# test endpoints
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
