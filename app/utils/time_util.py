from datetime import datetime
import pytz

def get_current_time() -> datetime:
    """
    현재 타임존이 없는(naive) 시각을 반환하는 함수
    """
    return datetime.now().replace(tzinfo=None)


def convert_to_kst(dt: datetime) -> datetime:
    """
    입력받은 시간을 한국 시간(KST)으로 변환하는 함수
    """
    kst = pytz.timezone('Asia/Seoul')
    # 만약 입력된 시간이 naive(타임존 정보 없음)일 경우 UTC 기준으로 간주하고 변환
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(kst)