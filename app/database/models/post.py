from typing import List
from odmantic import ObjectId, Model


class Post(Model):
    title: str
    content: str
    nick_name: str  # 작성자의 아이디
    user_id: ObjectId
    tags: List[str]  # 여러 문자열을 저장할 수 있는 리스트 필드
    file_url : str  # 파일 URL 필드 
    model_config = {"collection": "posts"}
