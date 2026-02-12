import json
from dataclasses import dataclass, asdict

from src.utils.paths import PROJECT_ROOT

USER_INFO = PROJECT_ROOT / "data/user.json"


@dataclass(frozen=True)
class User:
    username: str = ""
    password: str = ""

    def save(self):
        with open(USER_INFO, "w") as f:
            json.dump(asdict(self), f)

    @classmethod
    def load(cls) -> "User":
        if USER_INFO.exists():
            with open(USER_INFO) as f:
                return cls(**json.load(f))

        return cls()
