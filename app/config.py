import os
from dataclasses import dataclass
from decimal import Decimal
from urllib.parse import urlparse


@dataclass(frozen=True)
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "").strip()

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/quickotp",
    ).strip()

    grizzly_api_key: str = os.getenv("GRIZZLY_API_KEY", "").strip()

    grizzly_base_url: str = os.getenv(
        "GRIZZLY_BASE_URL",
        "https://api.grizzlysms.com/stubs/handler_api.php",
    ).strip()

    permanent_admin_id: int = int(
        os.getenv("PERMANENT_ADMIN_ID", "7517279474")
    )

    log_level: str = os.getenv("LOG_LEVEL", "INFO").strip()

    poll_interval: int = int(
        os.getenv("POLL_INTERVAL", "8")
    )

    report_poll_interval: int = int(
        os.getenv("REPORT_POLL_INTERVAL", "30")
    )


settings = Settings()


# Railway may provide postgres:// or postgresql://.
# SQLAlchemy async requires the asyncpg driver.
if settings.database_url.startswith("postgres://"):
    object.__setattr__(
        settings,
        "database_url",
        settings.database_url.replace(
            "postgres://",
            "postgresql+asyncpg://",
            1,
        ),
    )

elif settings.database_url.startswith("postgresql://"):
    object.__setattr__(
        settings,
        "database_url",
        settings.database_url.replace(
            "postgresql://",
            "postgresql+asyncpg://",
            1,
        ),
    )


# Fail early with a clear error instead of a confusing SQLAlchemy error.
if settings.database_url:
    parsed = urlparse(settings.database_url)

    if parsed.scheme != "postgresql+asyncpg":
        raise RuntimeError(
            "DATABASE_URL must use postgresql+asyncpg://"
        )

    if not parsed.hostname:
        raise RuntimeError(
            "DATABASE_URL has no valid database hostname. "
            "Check the Railway PostgreSQL DATABASE_URL reference."
        )

    if any(
        placeholder in settings.database_url
        for placeholder in (
            "USER",
            "PASSWORD",
            "HOST",
        )
    ):
        raise RuntimeError(
            "DATABASE_URL still contains placeholder values. "
            "Use the real Railway PostgreSQL DATABASE_URL."
        )


MIN_DEPOSIT = Decimal("3")
