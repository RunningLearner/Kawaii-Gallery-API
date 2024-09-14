from odmantic import Model


class User(Model):
    nick_name: str
    email: str
    feather: int = 0  # 사용자의 깃털 개수

    model_config = {"collection": "users"}
