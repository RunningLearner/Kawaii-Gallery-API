from typing import List
from odmantic import ObjectId, Model


class Post(Model):
    title: str
    content: str
    nick_name: str  # 작성자의 아이디
    user_id: ObjectId
    tags: List[str]  # 여러 문자열을 저장할 수 있는 리스트 필드
    file_url : str  # 파일 URL 필드 
    likes_count: int = 0  # 좋아요 수
    liked_by: List[ObjectId] = []  # 좋아요를 누른 사용자들의 ID 리스트
    model_config = {"collection": "posts"}
