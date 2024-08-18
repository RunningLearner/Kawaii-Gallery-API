from fastapi import FastAPI
from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
import logging


class MongoDB:
    def __init__(self, app: FastAPI = None, **kwargs):
        self._client = None
        self._engine = None
        if app is not None:
            self.init_app(app=app, **kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        """
        FastAPI 앱과 MongoDB를 초기화하는 함수
        :param app: FastAPI 인스턴스
        :param kwargs: 추가 설정 값
        """
        self.database_url = kwargs.get("DB_URL")
        self.pool_recycle = kwargs.setdefault("DB_POOL_RECYCLE", 900)
        self.is_testing = kwargs.setdefault("TEST_MODE", False)
        self.echo = kwargs.setdefault("DB_ECHO", True)
        self.db_name = kwargs.get("DB_NAME")

    async def connect(self):
        """
        MongoDB 연결 함수
        """
        self._client = AsyncIOMotorClient(self.database_url)
        self._engine = AIOEngine(client=self._client, database=self.db_name)
        logging.info("MongoDB connected.")
        print(f"MongoDB connected.{self.db_name}")

    async def close(self):
        """
        MongoDB 연결 종료 함수
        """
        if self._client:
            self._client.close()
            logging.info("MongoDB disconnected.")

    def get_engine(self) -> AIOEngine:
        """
        Odmantic 엔진을 가져오는 함수
        :return:
        """
        if self._engine is None:
            raise Exception("Must call 'connect' before using the engine.")
        return self._engine

    @property
    def engine(self):
        return self.get_engine()


db = MongoDB()  # MongoDB 인스턴스 생성
