from pydantic import BaseModel


class UserCreate(BaseModel):
    nick_name: str
    access_token: str
