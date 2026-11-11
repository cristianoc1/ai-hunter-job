import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

from src.database.db import job_exists

load_dotenv()


def fetch_filtered_jobs() -> list[dict[str, str]]:
    """Obtiene de Jooble ofertas nuevas que coinciden con el perfil."""
    api_key = os.getenv("JOOBLE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "JOOBLE_API_KEY no está configurada. "
            "Añádela como secreto de GitHub Actions o en .env."
        )

    print("Consultando ofertas en la API de Jooble...")
    response = requests.post(
        f"https://jooble.org/api/{api_key}",
        json={
            "keywords": (
                "Python OR React OR .NET OR Full Stack OR FastAPI OR Azure OR "
                "TypeScript OR Fullstack OR Desarrollador OR Power Platform OR "
                "Power Apps OR Power Automate OR Software"
            ),
            "location": "Colombia O Remote",
            "radius": "50",
        },
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    if not isinstance(data, dict) or not isinstance(data.get("jobs", []), list):
        raise ValueError("Jooble devolvió una respuesta con un formato inesperado.")

    raw_jobs = data.get("jobs", [])
    print(f"Jooble devolvió {len(raw_jobs)} ofertas.")

    target_keywords = (
        "python",
        "react",
        "fastapi",
        ".net",
        "azure",
        "full stack",
        "fullstack",
        "typescript",
    )
    filtered_jobs: list[dict[str, str]] = []
    seen_urls: set[str] = set()

    for job in raw_jobs:
        if not isinstance(job, dict):
            continue

        title = str(job.get("title") or "").strip()
        snippet = str(job.get("snippet") or "").strip()
        job_url = str(job.get("link") or "").strip()
        if not title or not job_url or job_url in seen_urls:
            continue
        parsed_url = urlparse(job_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            continue

        text_to_check = f"{title} {snippet}".casefold()
        if not any(keyword in text_to_check for keyword in target_keywords):
            continue
        if job_exists(job_url):
            continue

        seen_urls.add(job_url)
        filtered_jobs.append(
            {
                "title": title,
                "company": str(job.get("company") or "Empresa Confidencial").strip(),
                "location": str(job.get("location") or "Colombia").strip(),
                "url": job_url,
                "snippet": snippet,
            }
        )

    print(f"Ofertas nuevas y filtradas: {len(filtered_jobs)}")
    return filtered_jobs
