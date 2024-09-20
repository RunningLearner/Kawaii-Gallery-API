from fastapi import FastAPI
from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis
import logging

# 로거 설정
logger = logging.getLogger(__name__)


# class MongoDB:
#     def __init__(self, app: FastAPI = None, **kwargs):
#         self._client = None
#         self._engine = None
#         if app is not None:
#             self.init_app(app=app, **kwargs)

#     def init_app(self, app: FastAPI, **kwargs):
#         """
#         FastAPI 앱과 MongoDB를 초기화하는 함수
#         :param app: FastAPI 인스턴스
#         :param kwargs: 추가 설정 값
#         """
#         self.database_url = kwargs.get("DB_URL")
#         self.pool_recycle = kwargs.setdefault("DB_POOL_RECYCLE", 900)
#         self.is_testing = kwargs.setdefault("TEST_MODE", False)
#         self.echo = kwargs.setdefault("DB_ECHO", True)
#         self.db_name = kwargs.get("DB_NAME")

#     async def connect(self):
#         """
#         MongoDB 연결 함수
#         """
#         self._client = AsyncIOMotorClient(self.database_url)
#         self._engine = AIOEngine(client=self._client, database=self.db_name)
#         logger.info(f"MongoDB connected.{self.database_url}")
#         print(f"MongoDB connected.{self.db_name} {self.database_url}")

#     async def close(self):
#         """
#         MongoDB 연결 종료 함수
#         """
#         if self._client:
#             self._client.close()
#             logger.info("MongoDB disconnected.")

#     def get_engine(self) -> AIOEngine:
#         """
#         Odmantic 엔진을 가져오는 함수
#         :return:
#         """
#         if self._engine is None:
#             raise Exception("Must call 'connect' before using the engine.")
#         return self._engine

#     @property
#     def engine(self):
#         return self.get_engine()


# db = MongoDB()  # MongoDB 인스턴스 생성


# MongoDB 초기화 함수
async def init_mongo(db_url: str, db_name: str) -> AIOEngine:
    """
    MongoDB 클라이언트 및 엔진을 초기화하는 함수.
    :param db_url: MongoDB URL
    :param db_name: 데이터베이스 이름
    :return: AIOEngine instance
    """
    client = AsyncIOMotorClient(db_url)
    engine = AIOEngine(client=client, database=db_name)
    return engine


# MongoDB 클라이언트 종료 함수
async def close_mongo(engine: AIOEngine):
    """
    MongoDB 연결을 종료하는 함수.
    :param engine: AIOEngine instance
    """
    if engine.client:
        engine.client.close()


# Redis 초기화 함수
async def init_redis(redis_url: str) -> aioredis.Redis:
    """
    Redis 클라이언트를 초기화하는 함수.
    :param redis_url: Redis URL
    :return: aioredis.Redis instance
    """
    redis_client = await aioredis.from_url(redis_url, decode_responses=True)
    return redis_client


# Redis 클라이언트 종료 함수
async def close_redis(redis_client: aioredis.Redis):
    """
    Redis 연결을 종료하는 함수.
    :param redis_client: aioredis.Redis instance
    """
    if redis_client:
        await redis_client.close()
