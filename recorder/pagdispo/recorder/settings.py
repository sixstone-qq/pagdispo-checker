from pydantic import BaseSettings


class Settings(BaseSettings):
    """Settings contains the settings for checker to run"""
    KAFKA_BROKERS: str = 'localhost:9092'

    KAFKA_TOPIC: str = 'website.monitor'

    class Config:
        # This is set in order to let only upper case to work
        case_sensitive = True


settings = Settings()
