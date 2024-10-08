from datetime import datetime
import pytz
from fastapi import APIRouter
from starlette.responses import Response
from starlette.requests import Request
from inspect import currentframe as frame

router = APIRouter()

# 한국 표준시(KST) 타임존 정보 가져오기
kst = pytz.timezone("Asia/Seoul")

# 한국 시간으로 현재 시간 가져오기
current_time = datetime.now(kst)


@router.get("/")
async def index():
    """
    서버 상태 체크용 API
    :return:
    """

    return Response(
        f"Notification API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})"
    )
