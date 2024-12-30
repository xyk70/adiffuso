from typing import Any #, List, Tuple
from environ import Env

AMBIENTE = {
    "ALLOWED_HOSTS": (list, ["127.0.0.1", "localhost"]),
    "CACHE_DEFAULT": (str, "dummycache://"),
    "DEBUG": (bool, False),
    "DATABASE_URL": (str, "sqlite://:memory:"),
    "SECRET_KEY": (str, "very-insecure-"),
    "MEDIA_ROOT": (str, "/tmp/media/"),
    "MEDIA_URL": (str, "/media/"),
    "STATIC_ROOT": (str, "/tmp/static/"),
    "STATIC_URL": (str, "/static/"),
    "SOCIAL_AUTH_REDIRECT_IS_HTTPS": (bool, True),
    "GOOGLE_CLIENT_ID": (str, ""),
    "GOOGLE_CLIENT_SECRET": (str, ""),
    "SOCIAL_AUTH_GITHUB_KEY": (str, ""),
    "SOCIAL_AUTH_GITHUB_SECRET": (str, ""),
    "SOCIAL_AUTH_GITHUB_REDIRECT_URI": (str, "")
}

class MioEnv(Env):
    def __init__(self, prefix: str, **scheme: Any) -> None:
        values = {f"{prefix}_{k}": v for k, v in scheme.items()}

        super().__init__(**values)
        self.prefix = f"{prefix}_"

env: MioEnv = MioEnv("PEGASUS", **AMBIENTE)
