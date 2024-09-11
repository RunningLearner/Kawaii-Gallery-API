from fastapi import HTTPException
from odmantic import AIOEngine
from app.database.conn import db
from app.database.models.user import User


# id를 이용해 사용자를 가져오는 함수
async def get_user_by_object_id(user_id: str) -> User:
    user = await db.engine.find_one(User, User.id == user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"ID가 '{user_id}'인 사용자를 찾을 수 없습니다.")
    return user
