from fastapi import APIRouter, HTTPException, Depends, Body
from odmantic import AIOEngine
from app.database.conn import db
from app.database.models.token import FCMToken
from app.database.models.user import User
from app.dtos.auth import FCMTokenCreate
from app.dtos.user import UserCreate
from app.utils.token_utils import create_access_token, get_current_user_email
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

    # 기존 회원 체크
    existing_user = await engine.find_one(User, {"$or": [{"email": email}]})

    if not existing_user:
        raise HTTPException(status_code=404, detail="회원가입이 필요합니다. 닉네임을 입력해주세요.")

    # JWT 생성
    jwt_access_token = create_access_token(data={"email": str(email)})

    # 회원인지 확인 후 토큰 발급
    return {"access_token": jwt_access_token}


@router.post("/register")
async def register(
    user_info: UserCreate,
    engine: AIOEngine = Depends(db.get_engine),
):
    email = get_user_email(user_info.access_token)

    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Kakao")

    # 닉네임 중복 확인
    user = await db.engine.find_one(User, User.nick_name == user_info.nick_name)
    if user:
        raise HTTPException(status_code=400, detail="중복된 닉네임입니다.")

    # 유저 생성
    user = User(
        nick_name=user_info.nick_name,
        email=email,
    )

    await engine.save(user)

    # JWT 생성
    jwt_access_token = create_access_token(data={"email": str(email)})

    return {"access_token": jwt_access_token}


@router.post("/fcmtoken")
async def create_fcm_token(
    token_info: FCMTokenCreate,
    engine: AIOEngine = Depends(db.get_engine),
    user_email: str = Depends(get_current_user_email),
):
    # 사용자 조회
    user = await engine.find_one(User, User.email == user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 기존 FCM 토큰 확인 
    existing_token = await engine.find_one(
        FCMToken,
        FCMToken.user_id == user.id,
        FCMToken.device_type == token_info.device_type,
    )
    # 있다면 토큰 정보만 업데이트
    if existing_token:
        existing_token.fcm_token = token_info.fcm_token
        await engine.save(existing_token)
    else:
        # 새로운 FCM 토큰 생성
        new_token = FCMToken(
            user_id=user.id,
            fcm_token=token_info.fcm_token,
            device_type=token_info.device_type,
        )
        await engine.save(new_token)

    return {"message": "FCM token saved successfully"}


def get_user_email(access_token: str) -> str:
    # 액세스 토큰으로 사용자 정보 요청
    user_info_response = requests.get(
        user_info_url_kakao,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        },
    )
    print(f"status code from kakao :{user_info_response.status_code}")
    if user_info_response.status_code != 200:
        raise HTTPException(
            status_code=user_info_response.status_code, detail="Failed to get user info"
        )

    user_info = user_info_response.json()

    # 이메일 정보
    email = user_info.get("kakao_account", {}).get("email")

    return email
