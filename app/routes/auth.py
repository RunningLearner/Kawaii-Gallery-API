from fastapi import APIRouter, HTTPException, Depends, Body
from odmantic import AIOEngine
from app.database.conn import db
from app.database.models.user import User
from app.schemas.user import UserCreate
from app.utils.token import create_access_token
import requests


user_info_url_kakao = "https://kapi.kakao.com/v2/user/me"

router = APIRouter(prefix="/auth")

@router.post("/login/kakao", response_model=User)
async def kakao_login(access_token: str = Body(..., embed=True)):
    # 액세스 토큰으로 사용자 정보 요청
    user_info_response = requests.get(user_info_url_kakao, headers={
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
    })

    if user_info_response.status_code != 200:
        raise HTTPException(status_code=user_info_response.status_code, detail="Failed to get user info")

    user_info = user_info_response.json()

    # 예를 들어, 이메일 정보를 가져온다고 가정
    email = user_info.get('kakao_account', {}).get('email')
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Kakao")

    # 여기서 이메일이나 기타 사용자 정보를 바탕으로 추가 처리를 할 수 있습니다.
    return await verify(email)

async def verify(email: UserCreate):
    engine: AIOEngine = db.get_engine()
    print(f"Engine type: {type(engine)}")
    # 이메일 중복 체크
    existing_user = await engine.find_one(User, {"$or": [{"email": email}]})

    if not existing_user:
        # 유저 생성
        user = User(
            email = email,
        )
    
        await engine.save(user)
    
    # JWT 생성
    jwt_access_token = create_access_token(data={"email": str(email)})

    return {"email": email, "access_token": jwt_access_token}
