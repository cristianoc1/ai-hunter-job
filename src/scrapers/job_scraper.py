import os
import re
import unicodedata
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

from src.database.db import job_exists

load_dotenv()

REMOTE_WORK_PATTERN = re.compile(
    r"\b(remote|remoto|remota|teletrabajo|home office|"
    r"work from home|trabajo desde casa|trabajo remoto)\b"
)
ENGLISH_REQUIREMENT_TERMS = (
    "english required",
    "required english",
    "fluent english",
    "advanced english",
    "intermediate english",
    "conversational english",
    "english proficiency",
    "english level",
    "ingles requerido",
    "ingles avanzado",
    "ingles intermedio",
    "ingles conversacional",
    "ingles fluido",
    "nivel de ingles",
    "dominio del ingles",
    "bilingue",
    "b2 english",
    "c1 english",
    "b2 de ingles",
    "c1 de ingles",
)


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


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
            "location": "Colombia",
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
        location = str(job.get("location") or "").strip()
        normalized_location = _normalize_text(location)
        remote_text = _normalize_text(f"{title} {location} {snippet}")
        is_remote = bool(REMOTE_WORK_PATTERN.search(remote_text))
        is_in_medellin = bool(re.search(r"\bmedellin\b", normalized_location))
        if not is_remote and not is_in_medellin:
            continue
        if any(term in remote_text for term in ENGLISH_REQUIREMENT_TERMS):
            continue
        if job_exists(job_url):
            continue

        seen_urls.add(job_url)
        filtered_jobs.append(
            {
                "title": title,
                "company": str(job.get("company") or "Empresa Confidencial").strip(),
                "location": location or "Remoto desde Colombia",
                "url": job_url,
                "snippet": snippet,
            }
        )

    print(f"Ofertas nuevas y filtradas: {len(filtered_jobs)}")
    return filtered_jobs
