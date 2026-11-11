import os
import requests
from dotenv import load_dotenv
from src.database.db import job_exists, save_job

load_dotenv()

JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")


def fetch_filtered_jobs():
  """Consulta la API de Jooble, filtra por tecnologías clave de tu perfil

  y descarta las que ya estén registradas en Supabase.
  """
  print("🔍 Consultando ofertas en la API de Jooble...")

  url = f"https://jooble.org/api/{JOOBLE_API_KEY}"

  # Puedes personalizar el puesto y la ubicación según lo que busques
  payload = {
      "keywords": "Python OR React OR .NET OR Full Stack OR FastAPI OR Azure OR TypeScript OR Fullstack OR Desarrollador OR Power Platform OR Power Apps OR Power Automate OR Software",
      "location": "Colombia O Remote",  # O puedes cambiarlo a "Remote"
      "radius": "50",
  }

  try:
    response = requests.post(url, json=payload)
    if response.status_code != 200:
      print(f"Error en la API de Jooble: {response.status_code}")
      return []

    data = response.json()
    raw_jobs = data.get("jobs", [])

    print(f"Total de ofertas devueltas por la API: {len(raw_jobs)}")

    target_keywords = [
        "python",
        "react",
        "fastapi",
        ".net",
        "azure",
        "full stack",
        "fullstack",
        "typescript",
    ]
    new_filtered_jobs = []

    for job in raw_jobs:
      title = job.get("title", "")
      snippet = job.get(
          "snippet", ""
      )  # Pequeña descripción de la oferta
      job_url = job.get("link", "")
      company = job.get("company", "Empresa Confidencial")
      location = job.get("location", "Colombia")

      # Evitar procesar si falta el link
      if not job_url:
        continue

      # 1. Verificar si ya existe en Supabase (Control de Duplicados)
      if job_exists(job_url):
        continue  # Si ya fue enviada antes, la saltamos

      # 2. Filtrado inteligente por palabras clave en el título o descripción
      text_to_check = (title + " " + snippet).lower()
      if any(keyword in text_to_check for keyword in target_keywords):
        job_cleaned = {
            "title": title,
            "company": company,
            "location": location,
            "url": job_url,
        }
        new_filtered_jobs.append(job_cleaned)

        # Guardar inmediatamente en Supabase para marcarla como vista
        save_job(title=title, company=company, url=job_url)

    print(f"Ofertas nuevas y filtradas listas para enviar: {len(new_filtered_jobs)}")
    return new_filtered_jobs

  except Exception as e:
    print(f"Excepción conectando con Jooble: {e}")
    return []