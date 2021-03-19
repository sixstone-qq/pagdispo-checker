import pathlib
import os

from pydantic import BaseSettings, PostgresDsn


def proj_root() -> pathlib.Path:
    """Define the project root file system path"""
    return pathlib.Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Settings contains the settings for checker to run"""
    KAFKA_BROKERS: str = 'localhost:9092'

    KAFKA_SSL_CAFILE: str = None

    KAFKA_SSL_CERTFILE: str = None

    KAFKA_SSL_KEYFILE: str = None

    KAFKA_TOPIC: str = 'website.monitor'

    POSTGRESQL_DSN: PostgresDsn = 'postgres://postgres@localhost/monitor_check'

    PROJ_ROOT: pathlib.Path = proj_root()

    class Config:
        # This is set in order to let only upper case to work
        case_sensitive = True


env = os.getenv('PAGDISPO_ENV', 'development')
env_file = proj_root() / "{}.env".format(env)
if not env_file.is_file():
    env_file = None

settings = Settings(_env_file=env_file)
