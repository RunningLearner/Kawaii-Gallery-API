from odmantic import ObjectId, Model

class Post(Model):
    title: str
    content: str
    nick_name: str # 작성자의 아이디
    user_id: ObjectId  
    image_url: str # 이미지 URL 필드 추가
    model_config = {"collection": "posts"}