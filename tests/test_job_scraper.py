import os
import unittest
from unittest.mock import Mock, patch

import requests

from src.scrapers.job_scraper import fetch_filtered_jobs


class FetchFilteredJobsTests(unittest.TestCase):
    @patch.dict(os.environ, {"JOOBLE_API_KEY": "test-key"})
    @patch("src.scrapers.job_scraper.job_exists", return_value=False)
    @patch("src.scrapers.job_scraper.requests.post")
    def test_filters_jobs_and_deduplicates_urls(
        self, post: Mock, _job_exists: Mock
    ) -> None:
        response = Mock()
        response.json.return_value = {
            "jobs": [
                {
                    "title": "Python Developer",
                    "company": "Example",
                    "location": "Remote",
                    "link": "https://jobs.example/1",
                    "snippet": "Build APIs",
                },
                {
                    "title": "Python Developer",
                    "link": "https://jobs.example/1",
                },
                {
                    "title": "Accountant",
                    "link": "https://jobs.example/2",
                },
            ]
        }
        post.return_value = response

        jobs = fetch_filtered_jobs()

        _job_exists.assert_called_once_with("https://jobs.example/1")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["url"], "https://jobs.example/1")
        self.assertEqual(jobs[0]["snippet"], "Build APIs")
        response.raise_for_status.assert_called_once_with()
        post.assert_called_once()

    @patch.dict(os.environ, {"JOOBLE_API_KEY": "test-key"})
    @patch("src.scrapers.job_scraper.job_exists", return_value=False)
    @patch("src.scrapers.job_scraper.requests.post")
    def test_keeps_remote_or_medellin_jobs_without_explicit_english_requirements(
        self, post: Mock, job_exists: Mock
    ) -> None:
        response = Mock()
        response.json.return_value = {
            "jobs": [
                {
                    "title": "Desarrollador Python",
                    "location": "Colombia",
                    "link": "https://jobs.example/remote",
                    "snippet": "Trabajo remoto. Desarrollo de APIs.",
                },
                {
                    "title": "Desarrollador Python",
                    "location": "Medellín, Colombia",
                    "link": "https://jobs.example/medellin",
                    "snippet": "Trabajo presencial en oficina.",
                },
                {
                    "title": "Desarrollador Python",
                    "location": "Bogotá, Colombia",
                    "link": "https://jobs.example/onsite",
                    "snippet": "Trabajo presencial en oficina.",
                },
                {
                    "title": "Desarrollador Python",
                    "location": "Cali, Colombia",
                    "link": "https://jobs.example/cali",
                    "snippet": "Trabajo presencial en oficina.",
                },
                {
                    "title": "Python Developer",
                    "location": "Remote",
                    "link": "https://jobs.example/english",
                    "snippet": "Fluent English required.",
                },
            ]
        }
        post.return_value = response

        jobs = fetch_filtered_jobs()

        self.assertEqual(
            [job["url"] for job in jobs],
            ["https://jobs.example/remote", "https://jobs.example/medellin"],
        )
        self.assertEqual(
            [call.args[0] for call in job_exists.call_args_list],
            ["https://jobs.example/remote", "https://jobs.example/medellin"],
        )
        self.assertEqual(post.call_args.kwargs["json"]["location"], "Colombia")

    @patch.dict(os.environ, {"JOOBLE_API_KEY": ""})
    @patch("src.scrapers.job_scraper.requests.post")
    def test_requires_api_key(self, post: Mock) -> None:
        with self.assertRaisesRegex(RuntimeError, "JOOBLE_API_KEY"):
            fetch_filtered_jobs()
        post.assert_not_called()

    @patch.dict(os.environ, {"JOOBLE_API_KEY": "test-key"})
    @patch("src.scrapers.job_scraper.requests.post")
    def test_propagates_jooble_http_errors(self, post: Mock) -> None:
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("service error")
        post.return_value = response

        with self.assertRaises(requests.HTTPError):
            fetch_filtered_jobs()


if __name__ == "__main__":
    unittest.main()
