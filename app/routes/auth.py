from fastapi import APIRouter, HTTPException, Depends
from odmantic import AIOEngine
from app.database.conn import db
from app.database.models.user import User, UserCreate
from app.utils.password_hash import get_password_hash

router = APIRouter(prefix="/auth")

@router.post("/register", response_model=User)
async def register(user_create: UserCreate, engine: AIOEngine = Depends(db.get_engine)):
    # 이메일 또는 유저네임 중복 체크
    existing_user = await engine.find_one(User, {"$or": [{"email": user_create.email}, {"username": user_create.username}]})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    # 유저 생성
    user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password)
    )
    
    await engine.save(user)
    return user
