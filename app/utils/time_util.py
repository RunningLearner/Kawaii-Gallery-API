from datetime import datetime, timedelta
import pytz


# 한국 시간대(KST)
KST = pytz.timezone("Asia/Seoul")


def get_current_time() -> datetime:
    """
    현재 타임존이 없는(naive) 시각을 반환하는 함수
    """
    return datetime.now().replace(tzinfo=None)


def convert_to_kst(dt: datetime) -> datetime:
    """
    입력받은 시간을 한국 시간(KST)으로 변환하는 함수
    """
    # 만약 입력된 시간이 naive(타임존 정보 없음)일 경우 UTC 기준으로 간주하고 변환
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    # 한국 시간(KST)으로 변환
    return dt.astimezone(KST)


# 한국 시간대(KST)를 기준으로 다음 00시(자정)까지 남은 시간을 계산하는 함수
def get_seconds_until_midnight_kst():
    """
    한국 시간대(KST)를 기준으로 현재 시각에서 다음 자정까지 남은 시간을 초 단위로 반환하는 함수
    """
    # 현재 한국 시간
    now = datetime.now(KST)

    # 다음 자정 계산
    next_midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # 다음 자정까지 남은 시간을 초로 계산
    return int((next_midnight - now).total_seconds())
