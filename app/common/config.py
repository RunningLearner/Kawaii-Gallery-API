from dataclasses import dataclass, asdict
from os import path, environ

base_dir = path.dirname(path.dirname(path.abspath(__file__)))


@dataclass
class Config:
    """
    기본 설정
    """

    BASE_DIR = base_dir

    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def redis_url(self) -> str:
        """
        Redis URL을 반환하는 프로퍼티
        :return: str (Redis URL)
        """
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

@dataclass
class LocalConfig(Config):
    PROJ_RELOAD: bool = True
    DB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "kawaii_gallery_test"


@dataclass
class ProdConfig(Config):
    PROJ_RELOAD: bool = False
    DB_URL: str = "mongodb://mongodb:27017"
    DB_NAME: str = "kawaii_gallery"
    REDIS_HOST: str = "redis"  # 운영 환경에 맞는 Redis 설정

def conf():
    """
    환경 불러오기
    :return:
    """
    config = dict(prod=ProdConfig(), local=LocalConfig())
    env = environ.get("API_ENV", "local")
    print(f"환경변수 : {env}")
    return config.get(env, LocalConfig())
