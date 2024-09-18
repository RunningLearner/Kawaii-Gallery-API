from typing import List
from odmantic import ObjectId
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """
    새로운 사용자를 생성할 때 필요한 데이터 모델입니다.
    """

    nick_name: str = Field(
        ..., description="생성할 사용자의 닉네임", example="john_doe"
    )
    access_token: str = Field(
        ..., description="사용자의 액세스 토큰", example="example_access_token"
    )


class UserUpdate(BaseModel):
    """
    기존 사용자의 닉네임을 수정할 때 필요한 데이터 모델입니다.
    """

    nick_name: str = Field(
        ..., description="수정할 사용자의 닉네임", example="new_nick_name"
    )


# 사용자 조회 시 반환되는 모델
class UserResponseModel(BaseModel):
    id: str = Field(..., description="사용자의 고유 ID")
    nick_name: str = Field(..., description="사용자의 닉네임")
    email: str = Field(..., description="사용자의 이메일")
    profile_image_url: str = Field(None, description="사용자의 프로필 이미지 URL")

    class Config:
        from_attributes = True

    @classmethod
    def model_modify(cls, obj):
        # ObjectId를 문자열로 변환
        if isinstance(obj.id, ObjectId):
            obj.id = str(obj.id)
        return obj


# 모든 사용자 조회 시 반환되는 모델
class UserListResponseModel(BaseModel):
    users: List[UserResponseModel] = Field(..., description="사용자 목록")


# 닉네임 수정 후 반환되는 모델
class UpdateUserResponseModel(BaseModel):
    msg: str = Field(..., description="유저 정보가 업데이트된 결과 메시지")
    nick_name: str = Field(..., description="수정된 사용자의 닉네임")


# 사용자 삭제 후 반환되는 모델
class DeleteUserResponseModel(BaseModel):
    msg: str = Field(..., description="유저가 삭제된 결과 메시지")


# 프로필 이미지 수정 후 반환되는 모델
class UpdateProfileImageResponseModel(BaseModel):
    msg: str = Field(..., description="프로필 이미지가 업데이트된 결과 메시지")
    profile_image_url: str = Field(..., description="업데이트된 프로필 이미지의 URL")
