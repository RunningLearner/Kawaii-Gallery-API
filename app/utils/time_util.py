from datetime import datetime
import pytz

def get_current_time_kst() -> datetime:
    """
    현재 한국 시간(KST)을 반환하는 함수
    """
    kst = pytz.timezone('Asia/Seoul')
    return datetime.now(kst)
