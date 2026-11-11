import asyncio
import logging
import os

from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

from src.database.db import (
    mark_job_failed,
    mark_job_sent,
    prepare_job,
    validate_database,
)
from src.scrapers.job_scraper import fetch_filtered_jobs

load_dotenv()
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Falta configurar la variable de entorno {name}.")
    return value


async def _send_jobs(bot: Bot, chat_id: str, jobs: list[dict[str, str]]) -> int:
    sent_count = 0
    for job in jobs:
        job_id = prepare_job(job)
        if job_id is None:
            continue

        message = (
            "🚨 Nueva oferta detectada\n\n"
            f"Puesto: {job['title']}\n"
            f"Empresa: {job['company']}\n"
            f"Ubicación: {job['location']}\n\n"
            f"Descripción: {job['snippet'][:900] or 'No disponible'}\n\n"
            f"Enlace para postularte:\n{job['url']}"
        )

        try:
            await bot.send_message(chat_id=chat_id, text=message[:4000])
        except TelegramError:
            mark_job_failed(job_id)
            raise

        mark_job_sent(job_id)
        sent_count += 1
        logger.info("Oferta enviada: %s", job["title"])
        await asyncio.sleep(1)
    return sent_count


async def run_job_hunter() -> None:
    """Busca ofertas nuevas y envía a Telegram los datos y el enlace directo."""
    telegram_token = _required_env("TELEGRAM_TOKEN")
    chat_id = _required_env("CHAT_ID")
    validate_database()

    logger.info("Iniciando búsqueda de ofertas.")
    jobs = fetch_filtered_jobs()
    if not jobs:
        logger.info("No se encontraron ofertas nuevas.")
        return

    async with Bot(token=telegram_token) as bot:
        sent_count = await _send_jobs(bot, chat_id, jobs)
    logger.info("Ofertas enviadas: %d", sent_count)


if __name__ == "__main__":
    asyncio.run(run_job_hunter())
