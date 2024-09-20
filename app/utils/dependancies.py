from fastapi import Request, Depends
from odmantic import AIOEngine
import redis.asyncio as aioredis

# MongoDB 엔진 의존성 주입 함수
async def get_mongo_engine(request: Request) -> AIOEngine:
    return request.app.state.mongo_engine  # FastAPI의 상태에서 MongoDB 엔진 가져오기

    
# Redis 의존성 주입 함수
async def get_redis_client(request: Request) -> aioredis.Redis:
    return request.app.state.redis_client  # FastAPI의 상태에서 Redis 클라이언트 가져오기