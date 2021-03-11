from pydantic import BaseSettings


class Settings(BaseSettings):
    """Settings contains the settings for checker to run"""
    # it defines the tick time in seconds
    TICK_TIME: float = 1.0

    KAFKA_BROKERS: str = 'localhost:9092'

    KAFKA_TOPIC: str = 'website.monitor'

    class Config:
        # This is set in order to let only upper case to work
        case_sensitive = True


settings = Settings()
