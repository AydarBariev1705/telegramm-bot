import os

from dotenv import load_dotenv
from pydantic import SecretStr, StrictStr
from pydantic.v1 import BaseSettings

load_dotenv()


class SiteSettings(BaseSettings):
    api_key: SecretStr = os.getenv("SITE_API", None)
    tg_key: SecretStr = os.getenv('TG_API', None)
    host_api: StrictStr = os.getenv("HOST_API", None)
