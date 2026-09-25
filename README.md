# Quick OTP Number — FINAL 1.0.0

Production Telegram WhatsApp OTP marketplace for Railway + PostgreSQL + GrizzlySMS.

## Architecture
- Python 3.12
- aiogram 3.x
- PostgreSQL + SQLAlchemy 2 async + asyncpg
- Alembic migrations
- HTTPX Grizzly client
- Separate Railway Bot and Worker services using the same image
- PostgreSQL is the source of truth; no financial state is kept only on disk

## Required environment
```text
BOT_TOKEN=
GRIZZLY_API_KEY=
DATABASE_URL=
PERMANENT_ADMIN_ID=7517279474
GRIZZLY_BASE_URL=https://api.grizzlysms.com/stubs/handler_api.php
LOG_LEVEL=INFO
POLL_INTERVAL=8
```
Never commit Telegram/Grizzly credentials. Any credentials previously pasted during development should be rotated before production.

## Railway
Create one PostgreSQL database and two services from this project:
- Bot: `ROLE=bot`
- Worker: `ROLE=worker`

Railway's PostgreSQL connection variable can be `postgres://` or `postgresql://`; the app normalizes both to the asyncpg SQLAlchemy driver.

## Security / permissions
- Permanent admin is `PERMANENT_ADMIN_ID` and is the only account allowed to add/remove admins and change official Group, Channel, and private Admin Log Group IDs.
- Added admins can perform normal operational administration but cannot change those infrastructure IDs or manage admins.
- All admin mutations are audited.
- Blocked users cannot perform normal financial operations but can still use Support.
- Join gate fails closed when official Group/Channel IDs are not configured.

## User features
- Registration and join gate
- Buy WhatsApp OTP
- USDT wallet
- Add Funds
- Payment receipt as photo only
- My Balance
- My Orders + order detail/event history
- Transactions with pagination
- Statistics including countries used and most-used country
- Announcements
- Support
- Help

## Deposit rules
- Minimum deposit: 3 USDT
- Payment method and exchange rate are frozen when the request is created
- Default expiry: 20 minutes
- Expiry does **not** delete payment/account details
- Expired requests remain reviewable
- Users may send a receipt after expiry
- Admin may approve or reject an expired request after verification
- Historical requests keep the original payment method/account/instruction snapshot even if the method is later changed or disabled
- Receipt duplicate detection flags both matching receipts and approval refuses a confirmed duplicate
- Every approved deposit creates a wallet ledger entry atomically
- Manual balance add/deduct requires confirmation, reason, row locking, ledger entry and audit

## OTP ordering
1. Access/join/block/maintenance checks
2. Country selection
3. Selling price calculation
4. Wallet row lock
5. Internal order creation and balance reservation
6. Grizzly number request
7. Number/activation persistence
8. OTP polling in Worker
9. Completion/refund/reconciliation
10. Order events and audit trail

A Grizzly timeout/network failure/5xx is treated as an unknown external result: the app does not blindly retry or blindly refund. Such orders enter manual reconciliation.

The Grizzly integration uses documented activation/status/balance operations and does not hard-code a guessed WhatsApp service code. Configure the current Grizzly service code in the admin country configuration.

## Pricing / countries
For each configured country/service:
- raw Grizzly cost
- percentage markup
- fixed markup
- explicit selling price override
- enabled/disabled

Users see only the final selling price. Admins can see cost/price/profit. Historical orders retain cost, selling price and profit.

## Admin dashboard
The dashboard covers:
- Dashboard metrics
- Users
- Orders
- Deposits
- Balances
- Countries/pricing
- Payment methods
- Reports
- Announcements
- Broadcast queue/history
- Scheduled messages
- Admin management
- Support/settings
- Blocked users
- Maintenance
- Audit logs

Operational command examples:
```text
/admin
/admin_add TELEGRAM_ID [username]
/admin_remove TELEGRAM_ID
/setinfra group_id CHAT_ID
/setinfra channel_id CHAT_ID
/setinfra log_group_id CHAT_ID
/setsetting support_username @support
/setsetting daily_report_time 00:00
/setsetting daily_report_timezone Africa/Lagos
/maintenance on|off [message]
/balance TELEGRAM_ID add|deduct AMOUNT reason
/payment_method add NAME | CURRENCY | RATE | MIN | DETAILS | INSTRUCTIONS
/payment_method enable ID
/payment_method disable ID
/country add CODE | NAME | FLAG | SERVICE | COST | PERCENT | FIXED | EXPLICIT
/country enable CODE
/country disable CODE
/deposit list
/deposit approve ID
/deposit reject ID reason
/announce Title | Body
/announce send ID bot_users|official_group|official_channel
/broadcast bot_users|text
/schedule Name | cron | timezone | destination | content
```

## Broadcasts and schedules
- Text/photo/document only
- Video/audio are rejected
- Bot users, official Group, and official Channel destinations
- Persistent queue and delivery counters
- Scheduled jobs persist across worker restarts
- Timezone-aware cron scheduling
- Scheduled run records and duplicate-run protection

## Reports
Daily report is persisted and can be delivered to the private Admin Log Group. It includes users, orders/statuses, numbers received, deposits, revenue, Grizzly cost, profit and top countries. Time and timezone are database settings.

## Migrations
The app runs Alembic migrations on startup. For controlled production deployments you can also run:
```text
alembic upgrade head
```

## Verification performed for FINAL 1.0.0
- `pytest -q`: **27 passed**
- `python -m compileall -q app migrations`: **passed**
- Secret scan of source tree: **no hard-coded Telegram/Grizzly credentials found**
- Fresh-migration files and migration chain reviewed
- Bot/Worker separation reviewed
- Financial row-lock/idempotency paths reviewed
- Expired-deposit snapshot behavior reviewed
- Admin permission boundaries reviewed

### Live verification limitation
A live Telegram/Grizzly/PostgreSQL transaction was not executed in this build environment because production credentials, Telegram chat membership, Grizzly account balance, and a live Railway database are not available here. Before going live, run the deployment smoke test in Railway: `/start` → join gate → deposit → receipt → admin approval → buy number → OTP polling → refund/reconciliation, plus one scheduled message and daily report.

## Important
This project handles financial balances and third-party SMS activations. Use a real PostgreSQL backup/restore plan, rotate exposed development credentials, keep the Admin Log Group private, and verify the current Grizzly service/country catalogue before enabling countries.
