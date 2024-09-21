from fastapi import HTTPException
from odmantic import AIOEngine, ObjectId
from app.utils.dependancies import get_mongo_engine
from app.database.models.user import User


# id를 이용해 사용자를 가져오는 함수
async def get_user_by_object_id(engine: AIOEngine, user_id: ObjectId) -> User:
    user = await engine.find_one(User, User.id == user_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"ID가 '{user_id}'인 사용자를 찾을 수 없습니다."
        )
    return user


# 게시글 작성 시 깃털 증가 함수
async def increment_feather(
    engine: AIOEngine, user_id: ObjectId, amount: int = 1
) -> User:
    user = await get_user_by_object_id(engine, user_id)
    user.feather += amount  # 기본적으로 1만큼 증가
    await engine.save(user)
    return user


# 댓글 생성/수정 시 깃털 감소 함수
async def decrement_feather(
    engine: AIOEngine, user_id: ObjectId, amount: int = 1
) -> User:
    user = await get_user_by_object_id(engine, user_id)
    # 깃털이 부족한 경우
    if user.feather < amount:
        raise HTTPException(
            status_code=400,
            detail="깃털이 부족하여 댓글을 작성하거나 수정할 수 없습니다.",
        )

    # 깃털 감소
    user.feather -= amount
    await engine.save(user)
    return user
