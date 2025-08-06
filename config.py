from pydantic import BaseModel

# config.json 호출
class EndPointConfig(BaseModel):
    LOGIN: str
    LOGOUT: str
    MAIL: str
    INDEX: str
    MAIL_LIST: str


class AppConfig(BaseModel):
    URL: str
    END_POINT: EndPointConfig

def load_config(path: str = "config.json") -> AppConfig:
    import json
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return AppConfig(**data)


config = load_config()