import logging
import json
import os
import tempfile
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from src.utils.paths import PROJECT_ROOT


# config.json 호출
class EndPointConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    LOGIN: str
    LOGOUT: str
    MAIL: str
    INDEX: str
    MAIL_LIST: str


class SessionConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    AUTO_REFRESH_INTERVAL_SEC: int
    TOAST_MAIL_DURATION_SEC: int
    TOAST_SUCCESS_DURATION_SEC: int
    TOAST_WARN_DURATION_SEC: int
    QUIT_APP_HOUR: int
    QUIT_APP_MINUTE: int


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    URL: str
    END_POINT: EndPointConfig
    SESSION_CONFIG: SessionConfig


CONFIG_PATH = PROJECT_ROOT / "data" / "config.json"


def load_config(path: str | Path = CONFIG_PATH) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return AppConfig(**data)


def save_config_data(data: dict) -> None:
    """Validate and atomically persist settings, then update the shared config object."""
    validated = AppConfig.model_validate(data)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix="config-", suffix=".json", dir=CONFIG_PATH.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(temp_path, CONFIG_PATH)
    except Exception:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise

    # Keep references imported by services and UI modules current.
    config.URL = validated.URL
    for section in ("END_POINT", "SESSION_CONFIG"):
        target = getattr(config, section)
        source = getattr(validated, section)
        for key, value in source.model_dump().items():
            setattr(target, key, value)


config = load_config()
