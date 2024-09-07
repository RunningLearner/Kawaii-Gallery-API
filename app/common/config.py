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


@dataclass
class LocalConfig(Config):
    PROJ_RELOAD: bool = True
    DB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "kawaii_gallery"


@dataclass
class ProdConfig(Config):
    PROJ_RELOAD: bool = False
    DB_URL: str = "mongodb://mongodb:27017"
    DB_NAME: str = "kawaii_gallery"


def conf():
    """
    환경 불러오기
    :return:
    """
    config = dict(prod=ProdConfig(), local=LocalConfig())
    return config.get(environ.get("API_ENC", "local"))
