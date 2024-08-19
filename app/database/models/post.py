from odmantic import ObjectId, Model


class Post(Model):
    title: str
    content: str
    nick_name: str  # 작성자의 아이디
    user_id: ObjectId
    file_url : str  # 파일 URL 필드 
    model_config = {"collection": "posts"}
