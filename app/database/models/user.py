from odmantic import Model

class User(Model):
    username: str
    email: str
    hashed_password: str
    model_config = {"collection": "users"}
