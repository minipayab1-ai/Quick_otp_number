import os
from dataclasses import dataclass
from decimal import Decimal
from urllib.parse import quote


def build_database_url() -> str:
    raw = os.getenv("DATABASE_URL", "").strip()

    # Railway PostgreSQL variables
    host = os.getenv("PGHOST", "").strip()
    port = os.getenv("PGPORT", "5432").strip()
    user = os.getenv("PGUSER", "").strip()
    password = os.getenv("PGPASSWORD", "").strip()
    database = os.getenv("PGDATABASE", "").strip()

    # If Railway provides the individual PG variables, construct
    # a clean asyncpg URL from them.
    if host and user and password and database:
        return (
            "postgresql+asyncpg://"
            f"{quote(user, safe='')}:{quote(password, safe='')}"
            f"@{host}:{port}/{quote(database, safe='')}"
        )

    # Otherwise use DATABASE_URL.
    if raw:
        if raw.startswith("postgres://"):
            raw = raw.replace(
                "postgres://",
                "postgresql+asyncpg://",
                1,
            )
        elif raw.startswith("postgresql://"):
            raw = raw.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )

        return raw

    # Local development fallback only.
    return "postgresql+asyncpg://postgres:postgres@localhost:5432/quickotp"


@dataclass(frozen=True)
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "").strip()

    database_url: str = build_database_url()

    grizzly_api_key: str = os.getenv(
        "GRIZZLY_API_KEY",
        "",
    ).strip()

    grizzly_base_url: str = os.getenv(
        "GRIZZLY_BASE_URL",
        "https://api.grizzlysms.com/stubs/handler_api.php",
    ).strip()

    permanent_admin_id: int = int(
        os.getenv("PERMANENT_ADMIN_ID", "7517279474")
    )

    log_level: str = os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).strip()

    poll_interval: int = int(
        os.getenv("POLL_INTERVAL", "8")
    )

    report_poll_interval: int = int(
        os.getenv("REPORT_POLL_INTERVAL", "30")
    )


settings = Settings()

MIN_DEPOSIT = Decimal("3")
