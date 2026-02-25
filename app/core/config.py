from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class DatabaseConfig(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    name: str = "postgres"
    user: str = "postgres"
    password: str = "postgres"

    @property
    def async_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        )

    @property
    def sync_url(self) -> str:
        return (
            f"postgresql+psycopg2://"
            f"{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        )


class RedisConfig(BaseSettings):
    host: str = "redis"
    port: int = 6379
    broker_db: int = 0
    result_db: int = 1

    @property
    def broker_url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.broker_db}"

    @property
    def result_backend_url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.result_db}"


class MailConfig(BaseSettings):
    username: str
    password: str
    server: str = "smtp.gmail.com"
    port: int = 465
    tls: bool = True


class JwtConfig(BaseSettings):
    secret: str
    algorithm: str = "HS256"
    access_expire_minutes: int = 15
    refresh_expire_days: int = 30


class ApiConfig(BaseSettings):
    prefix: str = "/api/v1"


class Settings(BaseSettings):
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    mail: MailConfig
    jwt: JwtConfig
    api: ApiConfig = Field(default_factory=ApiConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__"
    )


settings = Settings()
