from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
import pytz


SECRET_KEY = "your-secret-key"  # 실제 운영에서는 환경 변수로 관리하세요
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 한국 표준시(KST) 타임존 정보 가져오기
kst = pytz.timezone("Asia/Seoul")


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(kst) + expires_delta
    else:
        expire = datetime.now(kst) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# JWT에서 이메일을 추출하는 함수
async def get_current_user_email(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = auth_header.split(" ")[1] if " " in auth_header else auth_header

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        user_email: str = payload.get("email")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        print(user_email)
        return user_email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
