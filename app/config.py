import os
from dataclasses import dataclass
from decimal import Decimal
@dataclass(frozen=True)
class Settings:
    bot_token:str=os.getenv('BOT_TOKEN','')
    database_url:str=os.getenv('DATABASE_URL','postgresql+asyncpg://postgres:postgres@localhost:5432/quickotp')
    grizzly_api_key:str=os.getenv('GRIZZLY_API_KEY','')
    grizzly_base_url:str=os.getenv('GRIZZLY_BASE_URL','https://api.grizzlysms.com/stubs/handler_api.php')
    permanent_admin_id:int=int(os.getenv('PERMANENT_ADMIN_ID','7517279474'))
    log_level:str=os.getenv('LOG_LEVEL','INFO')
    poll_interval:int=int(os.getenv('POLL_INTERVAL','8'))
    report_poll_interval:int=int(os.getenv('REPORT_POLL_INTERVAL','30'))
settings=Settings()
if settings.database_url.startswith('postgres://'):
    object.__setattr__(settings,'database_url',settings.database_url.replace('postgres://','postgresql+asyncpg://',1))
elif settings.database_url.startswith('postgresql://'):
    object.__setattr__(settings,'database_url',settings.database_url.replace('postgresql://','postgresql+asyncpg://',1))
MIN_DEPOSIT=Decimal('3')
