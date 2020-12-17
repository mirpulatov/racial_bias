"""
The module contains application.
"""

from starlette.config import Config


config = Config(".env")

# Logger config
LOG_CONFIG = config("DEV_LOG_PATH", cast=str, default="logger.conf")
DEV_LOG_NAME = config("DEV_LOG_NAME", cast=str, default="dev")

# Application config
APP_NAME = config("APP_NAME", cast=str, default="Web")
DEBUG = config("DEBUG", cast=bool, default=False)
TESTING = config("TESTING", cast=bool, default=False)
SECRET_TTL = config("SECRET_TTL", cast=int, default=60)  # Время валидности секретов в секундах
FILE_CHUNK_SIZE = config("FILE_CHUNK_SIZE", cast=int, default=4096)
