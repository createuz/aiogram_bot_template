import os
from dataclasses import dataclass, field
from urllib.parse import urlunparse

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


@dataclass
class DatabaseConfig:
    """Database connection configuration."""

    host: str = os.getenv("PG_HOST", "localhost")
    port: int = int(os.getenv("PG_PORT", 5432))
    user: str = os.getenv("PG_USER", "postgres")
    password: str = os.getenv("PG_PASSWORD", "")
    name: str = os.getenv("PG_DATABASE", "botdb")
    driver: str = os.getenv("DRIVER", "asyncpg")
    db_system: str = os.getenv("DB_SYSTEM", "postgresql")

    def build_db_url(self) -> str:
        """Builds the database connection string."""

        return URL.create(
            drivername=f"{self.db_system}+{self.driver}",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        ).render_as_string(hide_password=False)


@dataclass
class RedisConfig:
    """Redis connection configuration."""

    db: int = int(os.getenv("REDIS_DATABASE", 0))
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", 6379))
    password: str | None = os.getenv("REDIS_PASSWORD")
    username: str | None = os.getenv("REDIS_USERNAME")
    state_ttl: int = int(os.getenv("REDIS_TTL_STATE", 3600))
    data_ttl: int = int(os.getenv("REDIS_TTL_DATA", 7200))

    def build_redis_url(self) -> str:
        """Builds the Redis connection URL."""

        credentials = (f"{self.username}:{self.password}@" if self.username and self.password else "")
        return urlunparse(("redis", f"{credentials}{self.host}:{self.port}", f"/{self.db}", "", "", ""))


@dataclass
class RedisConfig2:
    """Redis connection configuration."""

    host: str = os.getenv("FSM_HOST", "localhost")
    port: int = int(os.getenv("FSM_PORT", 6379))
    password: str | None = os.getenv("FSM_PASSWORD", None)
    db: int = int(os.getenv("REDIS_DATABASE", 0))

    def build_redis_url(self) -> str:
        """Builds the Redis connection URL."""

        credentials = (f"{self.password}@" if self.password else "")
        return urlunparse(("redis", f"{credentials}{self.host}:{self.port}", f"/{self.db}", "", "", ""))


@dataclass
class CacheConfig:
    """Cache server configuration."""

    enabled: bool = bool(os.getenv("USE_CACHE", False))
    host: str = os.getenv("CACHE_HOST", "localhost")
    port: int = int(os.getenv("CACHE_PORT", 6379))
    password: str = os.getenv("CACHE_PASSWORD", None)

    def build_cache_url(self) -> str:
        """Builds the cache server URL."""

        credentials = (f"{self.password}@" if self.password else "")
        return urlunparse(("redis", f"{credentials}{self.host}:{self.port}", "", "", "", ""))


@dataclass
class WebhookConfig:
    """Webhook configuration."""

    enabled: bool = bool(os.getenv("USE_WEBHOOK", False))
    url: str = os.getenv("WEBHOOK_URL", "")
    secret_token: str = os.getenv("WEBHOOK_SECRET_TOKEN", "")
    host: str = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    port: int = int(os.getenv("WEBHOOK_PORT", 8443))
    max_updates_in_queue: int = int(os.getenv("MAX_UPDATES_IN_QUEUE", 1000))


@dataclass
class CustomApiServerConfig:
    """Custom API server configuration."""

    enabled: bool = bool(os.getenv("USE_CUSTOM_API_SERVER", False))
    is_local: bool = bool(os.getenv("CUSTOM_API_SERVER_IS_LOCAL", False))
    base_url: str = os.getenv("CUSTOM_API_SERVER_BASE", "")
    file_url: str = os.getenv("CUSTOM_API_SERVER_FILE", "")


@dataclass
class BotConfig:
    """Telegram bot configuration."""

    token: str = os.getenv("BOT_TOKEN", "")
    logging_level: int = int(os.getenv("LOGGING_LEVEL", 10))


@dataclass
class AppConfig:
    """Unified application configuration."""

    debug: bool = bool(int(os.getenv("DEBUG", 0)))
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    webhook: WebhookConfig = field(default_factory=WebhookConfig)
    custom_api_server: CustomApiServerConfig = field(default_factory=CustomApiServerConfig)
    bot_token: BotConfig = field(default_factory=BotConfig)


ADMIN = 5383531061

# Global configuration instance
conf: AppConfig = AppConfig()
bot: Bot = Bot(token=conf.bot_token.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# print("Database URL:", conf.db.build_db_url())
