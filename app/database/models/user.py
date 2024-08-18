from odmantic import Model


class User(Model):
    nick_name: str
    email: str
    model_config = {"collection": "users"}
