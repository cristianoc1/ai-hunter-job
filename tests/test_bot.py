import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from telegram.error import TelegramError

from src.bot.bot import _send_jobs


JOB = {
    "title": "Python Developer",
    "company": "Example Ltd",
    "location": "Remote",
    "url": "https://jobs.example/1",
    "snippet": "Build APIs",
}


class SendJobsTests(unittest.IsolatedAsyncioTestCase):
    async def test_message_includes_job_details_and_direct_link(self) -> None:
        bot = MagicMock()
        bot.send_message = AsyncMock()
        with (
            patch("src.bot.bot.prepare_job", return_value=417),
            patch("src.bot.bot.mark_job_sent") as mark_job_sent,
            patch("src.bot.bot.asyncio.sleep", new_callable=AsyncMock),
        ):
            sent = await _send_jobs(bot, "12345", [JOB])

        self.assertEqual(sent, 1)
        kwargs = bot.send_message.await_args.kwargs
        self.assertEqual(kwargs["chat_id"], "12345")
        self.assertIn("Python Developer", kwargs["text"])
        self.assertIn("Example Ltd", kwargs["text"])
        self.assertIn("Remote", kwargs["text"])
        self.assertIn("https://jobs.example/1", kwargs["text"])
        self.assertNotIn("reply_markup", kwargs)
        mark_job_sent.assert_called_once_with(417)

    async def test_failed_telegram_send_is_not_marked_sent(self) -> None:
        bot = MagicMock()
        bot.send_message = AsyncMock(side_effect=TelegramError("send failed"))
        with (
            patch("src.bot.bot.prepare_job", return_value=417),
            patch("src.bot.bot.mark_job_sent") as mark_job_sent,
            patch("src.bot.bot.mark_job_failed") as mark_job_failed,
        ):
            with self.assertRaises(TelegramError):
                await _send_jobs(bot, "12345", [JOB])

        mark_job_failed.assert_called_once_with(417)
        mark_job_sent.assert_not_called()


if __name__ == "__main__":
    unittest.main()
