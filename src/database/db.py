import os
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializar el cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def job_exists(job_url: str) -> bool:
  """Verifica si una oferta ya fue enviada previamente consultando su URL."""
  try:
    response = (
        supabase.table("jobs_sent").select("id").eq("url", job_url).execute()
    )
    return len(response.data) > 0
  except Exception as e:
    print(f"Error consultando Supabase: {e}")
    return False


def save_job(title: str, company: str, url: str):
  """Guarda una oferta enviada para evitar futuros duplicados."""
  try:
    supabase.table("jobs_sent").insert(
        {"title": title, "company": company, "url": url}
    ).execute()
  except Exception as e:
    print(f"Error guardando oferta en Supabase: {e}")