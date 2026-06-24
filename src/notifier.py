import asyncio
import logging
import time
from datetime import datetime, timezone

from telegram import Bot

from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


def send_new_jobs(jobs):
    for job in jobs:
        message = format_job_message(job)
        try:
            asyncio.run(send_telegram_async(message))
        except Exception as ex:
            logger.warning("Telegram send failed (%s); message was:\n%s", ex, message)
        time.sleep(3)


def format_job_message(job):
    posted = "N/A"
    if job.get("time"):
        posted = datetime.fromtimestamp(job["time"], tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"🔔 *New YC/HN Job Found!*\n"
        f"💼 *Title:* {job['title']}\n"
        f"👤 *Posted by:* {job.get('by') or 'N/A'}\n"
        f"🕒 *Posted at:* {posted}\n"
        f"🔗 [View posting]({job['link']})\n"
    )


async def send_telegram_async(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message,
        parse_mode="Markdown",
    )
