from fastapi import APIRouter, HTTPException, Depends, Body
from odmantic import AIOEngine, ObjectId
from app.database.conn import db
from app.database.models.user import User
from app.dtos.user import UserUpdate
from app.utils.token_utils import get_current_user_id

import logging

# 로거 설정
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user")


# Read - 사용자 조회
@router.get("/{user_id}")
async def get_user_by_id(
    user_id: str,
    engine: AIOEngine = Depends(db.get_engine),
):
    user = await engine.find_one(User, User.id == user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail=f"ID가 '{user_id}'인 사용자를 찾을 수 없습니다."
        )

    return user


# Read - 모든 사용자 조회
@router.get("/")
async def get_user(
    engine: AIOEngine = Depends(db.get_engine),
):
    users = await engine.find(User)
    if not users:
        raise HTTPException(status_code=404, detail=f"사용자가 존재하지 않습니다.")

    return users


# Update - 사용자 정보 수정 (닉네임 변경)
@router.put("/")
async def update_user(
    user_update: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    engine: AIOEngine = Depends(db.get_engine),
):
    user = await engine.find_one(User, User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")

    # 닉네임 중복 체크
    if user_update.nick_name:
        existing_user = await engine.find_one(
            User, User.nick_name == user_update.nick_name
        )
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400, detail="중복된 닉네임입니다.")

        user.nick_name = user_update.nick_name

    await engine.save(user)

    logger.info(f"유저 업데이트 완료: {user.nick_name} ({user.email})")

    return {"msg": "유저 정보가 업데이트되었습니다."}


# Delete - 사용자 삭제
@router.delete("/{user_id}")
async def delete_user(
    user_id: ObjectId,
    engine: AIOEngine = Depends(db.get_engine),
):
    user = await engine.find_one(User, User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")

    await engine.delete(user)

    logger.info(f"유저 삭제 완료: {user.nick_name} ({user.email})")

    return {"msg": "유저가 삭제되었습니다."}
