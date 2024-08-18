from fastapi import APIRouter, HTTPException, Depends, Body
from odmantic import AIOEngine
from app.database.conn import db
from app.database.models.user import User
from app.schemas.user import UserCreate
from app.utils.token_utils import create_access_token
import requests


user_info_url_kakao = "https://kapi.kakao.com/v2/user/me"

router = APIRouter(prefix="/auth")


@router.post("/login/kakao")
async def kakao_login(
    access_token: str = Body(..., embed=True),
    engine: AIOEngine = Depends(db.get_engine),
):
    # 이메일 정보
    email = get_user_email(access_token)

    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Kakao")

    # 이메일 중복 체크
    existing_user = await engine.find_one(User, {"$or": [{"email": email}]})

    if not existing_user:
        return {"message": "회원가입이 필요합니다. 닉네임을 입력해주세요.", "access_token": access_token}

    # JWT 생성
    jwt_access_token = create_access_token(data={"email": str(email)})

    # 회원인지 확인 후 토큰 발급
    return {"access_token": jwt_access_token}

@router.post("/register")
async def register(
    access_token: str = Body(..., embed=True),
    nick_name: str = Body(..., embed=True),
    engine: AIOEngine = Depends(db.get_engine),
):
    email = get_user_email(access_token)

    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Kakao")

    # 유저 생성
    user = User(
        nick_name=nick_name,
        email=email,
    )

    await engine.save(user)

    # JWT 생성
    jwt_access_token = create_access_token(data={"email": str(email)})

    return {"access_token": jwt_access_token}

def get_user_email(access_token: str) -> str:
    # 액세스 토큰으로 사용자 정보 요청
    user_info_response = requests.get(
        user_info_url_kakao,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        },
    )

    if user_info_response.status_code != 200:
        raise HTTPException(
            status_code=user_info_response.status_code, detail="Failed to get user info"
        )

    user_info = user_info_response.json()

    # 이메일 정보
    email = user_info.get("kakao_account", {}).get("email")

    return email
