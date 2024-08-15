from odmantic import Model

class User(Model):
    email: str
    model_config = {"collection": "users"}
