from fastapi import HTTPException
from odmantic import AIOEngine
from app.database.conn import db
from app.database.models.user import User

# 이메일을 이용해 사용자를 가져오는 함수
async def get_user_by_object_id(email: str) -> User:
    user = await db.engine.find_one(User, User.email == email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user