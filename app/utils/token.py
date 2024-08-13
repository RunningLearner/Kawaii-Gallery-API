from datetime import datetime, timedelta
from jose import JWTError, jwt
import pytz

SECRET_KEY = "your-secret-key"  # 실제 운영에서는 환경 변수로 관리하세요
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 한국 표준시(KST) 타임존 정보 가져오기
kst = pytz.timezone('Asia/Seoul')

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(kst) + expires_delta
    else:
        expire = datetime.now(kst) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt
