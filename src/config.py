from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheNameSpace(BaseModel):
    hotels_list: str = "hotels"


class RedisDB(BaseModel):
    cache: int = 0


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: RedisDB = RedisDB()

    @property
    def REDIS_URL(self):
        return f"redis://{self.host}:{self.port}"


class CacheConfig(BaseModel):
    prefix: str = "fastapi-cache"
    namespace: CacheNameSpace = CacheNameSpace()


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    HOTELS_API_KEY: str
    API_URL: str
    TG_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env")

    redis: RedisConfig = RedisConfig()
    cache: CacheConfig = CacheConfig()

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
