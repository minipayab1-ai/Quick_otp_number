import asyncio
import os
from aiogram import Bot, Dispatcher
from app.config import settings
from app.logging import setup_logging
from app.bot.router import router as user_router
from app.admin.router import router as admin_router
from app.db.session import engine, SessionLocal
from app.db.seed import seed

async def migrate_and_seed() -> None:
    from alembic import command
    from alembic.config import Config
    cfg = Config('alembic.ini')
    cfg.set_main_option('sqlalchemy.url', settings.database_url.replace('%', '%%'))
    await asyncio.to_thread(command.upgrade, cfg, 'head')
    async with SessionLocal() as session:
        await seed(session)
        await session.commit()

async def run_bot() -> None:
    if not settings.bot_token:
        raise RuntimeError('BOT_TOKEN is required')
    await migrate_and_seed()
    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(user_router)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await engine.dispose()

async def run_worker() -> None:
    if not settings.bot_token:
        raise RuntimeError('BOT_TOKEN is required')
    await migrate_and_seed()
    bot = Bot(settings.bot_token)
    from app.worker import poll_orders, expire_deposits, scheduled_messages, daily_reports, process_broadcasts
    tasks = [
        asyncio.create_task(poll_orders(bot)),
        asyncio.create_task(expire_deposits()),
        asyncio.create_task(scheduled_messages(bot)),
        asyncio.create_task(daily_reports(bot)),
        asyncio.create_task(process_broadcasts(bot)),
    ]
    try:
        await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            task.cancel()
        await bot.session.close()
        await engine.dispose()

async def main() -> None:
    setup_logging(settings.log_level)
    role = os.getenv('ROLE', 'bot').lower()
    if role == 'worker':
        await run_worker()
    elif role == 'bot':
        await run_bot()
    else:
        raise RuntimeError('ROLE must be bot or worker')

if __name__ == '__main__':
    asyncio.run(main())
