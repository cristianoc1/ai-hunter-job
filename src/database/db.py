import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

_supabase: Client | None = None


def _get_supabase() -> Client:
    global _supabase
    if _supabase is not None:
        return _supabase

    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    parsed_url = urlparse(supabase_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise RuntimeError(
            "SUPABASE_URL no está configurada o no es una URL válida. "
            "Configura el secreto SUPABASE_URL en GitHub Actions o en .env."
        )
    if not supabase_key:
        raise RuntimeError(
            "SUPABASE_KEY no está configurada. "
            "Configura el secreto SUPABASE_KEY en GitHub Actions o en .env."
        )

    _supabase = create_client(supabase_url, supabase_key)
    return _supabase


def validate_database() -> None:
    """Comprueba credenciales, permisos y columnas requeridas antes de buscar."""
    client = _get_supabase()
    try:
        (
            client.table("jobs_sent")
            .select("id,status,location,snippet")
            .limit(1)
            .execute()
        )
    except Exception as error:
        raise RuntimeError(
            "No se pudo validar public.jobs_sent. Comprueba SUPABASE_KEY y "
            "ejecuta la migración de columnas indicada en el README."
        ) from error


def job_exists(job_url: str) -> bool:
    """Indica si la oferta ya fue enviada correctamente."""
    response = (
        _get_supabase()
        .table("jobs_sent")
        .select("id")
        .eq("url", job_url)
        .eq("status", "sent")
        .limit(1)
        .execute()
    )
    return bool(response.data)


def prepare_job(job: dict[str, str]) -> int | None:
    """Crea o reutiliza el registro pendiente que identifica una oferta."""
    client = _get_supabase()
    existing = (
        client.table("jobs_sent")
        .select("id,status")
        .eq("url", job["url"])
        .limit(1)
        .execute()
        .data
    )

    job_data = {
        "title": job["title"],
        "company": job["company"],
        "url": job["url"],
        "location": job["location"],
        "snippet": job["snippet"],
        "status": "pending",
    }

    if existing:
        row = existing[0]
        if row["status"] == "sent":
            return None
        response = (
            client.table("jobs_sent")
            .update(job_data)
            .eq("id", row["id"])
            .select("id")
            .execute()
        )
    else:
        response = (
            client.table("jobs_sent")
            .insert(job_data)
            .select("id")
            .execute()
        )

    if not response.data:
        raise RuntimeError("Supabase no devolvió el identificador de la oferta.")
    job_id = response.data[0].get("id")
    if not isinstance(job_id, int):
        raise RuntimeError("El identificador de la oferta en Supabase no es válido.")
    return job_id


def mark_job_sent(job_id: int) -> None:
    response = (
        _get_supabase()
        .table("jobs_sent")
        .update({"status": "sent"})
        .eq("id", job_id)
        .select("id")
        .execute()
    )
    if not response.data:
        raise RuntimeError(f"No se pudo marcar como enviada la oferta {job_id}.")


def mark_job_failed(job_id: int) -> None:
    response = (
        _get_supabase()
        .table("jobs_sent")
        .update({"status": "failed"})
        .eq("id", job_id)
        .select("id")
        .execute()
    )
    if not response.data:
        raise RuntimeError(f"No se pudo marcar como fallida la oferta {job_id}.")
