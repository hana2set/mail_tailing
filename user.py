import json
from pathlib import Path
from dataclasses import dataclass, asdict

USER_INFO = Path("user.json")

@dataclass(frozen=True)
class User:
    username:str = ""
    password:str = ""

    @staticmethod
    def set_default_user(user: 'User'):
        with open(USER_INFO, 'w') as f:
            json.dump(asdict(user), f)


    @staticmethod
    def get_default_user() -> 'User':
        if USER_INFO.exists():
            with open(USER_INFO) as f:
                return User(**json.load(f))

        return User()


