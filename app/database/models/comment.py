from typing import List, Optional
from odmantic import ObjectId, Model


class Comment(Model):
    user_id: ObjectId  # 댓글 작성자의 ID
    post_id: ObjectId  # 댓글 작성자의 ID
    content: str  # 댓글 내용
    nick_name: str  # 댓글 작성자의 닉네임
    liked_by: List[ObjectId] = []  # 댓글에 좋아요를 누른 사용자들의 ID 리스트
    # 대댓기능은 보류
    # replies: Optional[List["Comment"]] = []  # 댓글에 대한 댓글 리스트

    model_config = {"collection": "comments"}
