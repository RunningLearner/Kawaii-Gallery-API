import os
from fastapi import APIRouter, File, HTTPException, Depends, Body, UploadFile
from odmantic import AIOEngine, ObjectId
from app.database.models.user import User
from app.dtos.user import (
    DeleteUserResponseModel,
    UpdateProfileImageResponseModel,
    UpdateUserResponseModel,
    UserListResponseModel,
    UserResponseModel,
    UserUpdate,
)
from app.utils.dependancies import get_mongo_engine
from app.utils.token_utils import get_current_user_id

import logging

# 로거 설정
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user")


# Read - 모든 사용자 조회
@router.get("/", response_model=UserListResponseModel)
async def get_user(
    engine: AIOEngine = Depends(get_mongo_engine),
):
    """
    이 엔드포인트는 아이템을 path parameter를 통해 사용자를 조회합니다.

    - **user_id**: 조회할 사용자의 ObjectId
    """
    try:
        users = await engine.find(User)
        if not users:
            raise HTTPException(status_code=404, detail=f"사용자가 존재하지 않습니다.")

        # ODMantic User 객체를 Pydantic UserResponseModel로 변환 후 반환
        return {"users": [UserResponseModel.from_odmantic(user) for user in users]}
    except HTTPException as http_ex:
        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(f"사용자 조회 실패", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


# Update - 사용자 정보 수정 (닉네임 변경)
@router.put("/nickname", response_model=UpdateUserResponseModel)
async def update_user(
    user_update: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    engine: AIOEngine = Depends(get_mongo_engine),
):
    """
    이 엔드포인트는 사용자의 닉네임을 수정합니다.
    """
    try:
        user = await engine.find_one(User, User.id == user_id)
        if not user:
            raise HTTPException(
                status_code=404, detail="해당 사용자를 찾을 수 없습니다."
            )

        # 닉네임 중복 체크
        if user_update.nick_name:
            existing_user = await engine.find_one(
                User, User.nick_name == user_update.nick_name
            )
            if existing_user and existing_user.id != user_id:
                raise HTTPException(status_code=400, detail="중복된 닉네임입니다.")

            user.nick_name = user_update.nick_name

        await engine.save(user)

        logger.info(f"사용자 업데이트 완료: {user.nick_name} ({user.email})")

        return {"msg": "사용자 정보가 업데이트되었습니다.", "nick_name": user.nick_name}
    except HTTPException as http_ex:
        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(
            f"사용자 업데이트 실패: {user_id} ({user.email if user.email else '이메일 정보 찾을 수 없음'})",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


# Delete - 사용자 삭제
@router.delete("/{user_id}", response_model=DeleteUserResponseModel)
async def delete_user(
    user_id: ObjectId,
    engine: AIOEngine = Depends(get_mongo_engine),
):
    """
    이 엔드포인트는 특정 사용자를 삭제합니다.

    - **user_id**: 삭제할 사용자의 ObjectId
    """
    try:
        user = await engine.find_one(User, User.id == user_id)
        if not user:
            raise HTTPException(
                status_code=404, detail="해당 사용자를 찾을 수 없습니다."
            )

        await engine.delete(user)

        logger.info(f"사용자 삭제 완료: {user.nick_name} ({user.email})")

        return {"msg": "사용자가 삭제되었습니다."}
    except HTTPException as http_ex:
        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(
            f"사용자 삭제 실패: {user_id} ({user.email if user.email else '이메일 정보 찾을 수 없음'})",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


# Update - 사용자 프로필 이미지 수정
@router.put("/profile_image", response_model=UpdateProfileImageResponseModel)
async def update_user_profile_image(
    file: UploadFile = File(..., description="업로드할 이미지 또는 비디오 파일들"),
    user_id: str = Depends(get_current_user_id),
    engine: AIOEngine = Depends(get_mongo_engine),
):
    """
    이 엔드포인트는 사용자의 프로필 이미지를 수정합니다.

    - **file**: 업로드할 이미지 파일 (.png, .jpg, .jpeg, .gif 허용)
    """
    try:
        user = await engine.find_one(User, User.id == user_id)
        if not user:
            raise HTTPException(
                status_code=404, detail="해당 사용자를 찾을 수 없습니다."
            )

        # 파일 확장자 체크 (이미지 파일만 허용)
        if not file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            raise HTTPException(
                status_code=400, detail="이미지 파일만 업로드 가능합니다."
            )

        # 저장할 경로 설정
        upload_directory = "uploads/profile_images"
        os.makedirs(upload_directory, exist_ok=True)  # 디렉터리가 없으면 생성

        file_path = os.path.join(upload_directory, f"{user_id}_{file.filename}")

        # 파일 저장
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # 기존 프로필 이미지 삭제 (선택사항)
        if user.profile_image_url:
            if os.path.exists(user.profile_image_url):
                os.remove(user.profile_image_url)

        # 사용자 프로필 이미지 경로 업데이트
        user.profile_image_url = file_path
        await engine.save(user)

        logger.info(
            f"사용자 프로필 이미지 업데이트 완료: {user.nick_name} ({user.email})"
        )

        return {
            "msg": "프로필 이미지가 업데이트되었습니다.",
            "profile_image_url": file_path,
        }
    except HTTPException as http_ex:
        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(
            f"사용자 프로필 이미지 수정 실패: {user_id} ({user.email if user.email else '이메일 정보 찾을 수 없음'})",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )


# Read - 사용자 조회
@router.get("/{user_id}", response_model=UserResponseModel)
async def get_user_by_id(
    user_id: ObjectId,
    engine: AIOEngine = Depends(get_mongo_engine),
):
    """
    이 엔드포인트는 아이템을 path parameter를 통해 사용자를 조회합니다.

    - **user_id**: 조회할 사용자의 ObjectId
    """
    try:
        user = await engine.find_one(User, User.id == user_id)
        if not user:
            raise HTTPException(
                status_code=404, detail=f"ID가 '{user_id}'인 사용자를 찾을 수 없습니다."
            )
        # Pydantic 모델로 변환
        # user_response = UserResponseModel(user)

        # 변환된 데이터 로깅
        # logger.info(f"변환된 사용자 데이터: {user_response}")

        # 변환된 사용자 데이터를 반환
        return user
    except HTTPException as http_ex:
        # http 에러는 다시 raise해서 그대로 클라이언트에 전달
        raise http_ex
    except Exception as ex:
        logger.error(
            f"사용자 조회 실패: {user_id} ({user.email if user.email else '이메일 정보 찾을 수 없음'})",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다.",
        )
