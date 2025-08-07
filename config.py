from pydantic import BaseModel

# config.json 호출
class EndPointConfig(BaseModel):
    LOGIN: str
    LOGOUT: str
    MAIL: str
    INDEX: str
    MAIL_LIST: str

class SessionConfig(BaseModel):
    AUTO_REFRESH_INTERVAL_SEC: int
    TOAST_MAIL_DURATION_SEC: int
    TOAST_SUCCESS_DURATION_SEC: int
    TOAST_WARN_DURATION_SEC: int

class AppConfig(BaseModel):
    URL: str
    END_POINT: EndPointConfig
    SESSION_CONFIG: SessionConfig



def load_config(path: str = "config.json") -> AppConfig:
    import json
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return AppConfig(**data)


config = load_config()