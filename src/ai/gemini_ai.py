import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configurar la API de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


def load_base_cv():
  """Carga el CV maestro desde la plantilla Markdown."""
  cv_path = os.path.join(
      os.path.dirname(__file__), "../../templates/cv_base.md"
  )
  try:
    with open(cv_path, "r", encoding="utf-8") as f:
      return f.read()
  except Exception as e:
    print(f"Error cargando el CV base: {e}")
    return ""


def optimize_cv_for_job(job_title: str, company: str, job_snippet: str) -> str:
  """Usa Gemini para adaptar el CV base a una oferta específica,

  optimizándolo para filtros ATS y destacando las tecnologías clave.
  """
  base_cv = load_base_cv()
  if not base_cv:
    return "No se pudo cargar el CV base."

  # Usamos un modelo rápido y eficiente como gemini-1.5-flash
  model = genai.GenerativeModel("gemini-1.5-flash")

  prompt = f"""
    Actúa como un experto reclutador tecnológico y especialista en optimización de currículums para sistemas ATS (Applicant Tracking Systems).
    Tengo el siguiente CV base en Markdown:
    
    {base_cv}
    
    Y quiero postularme a la siguiente oferta de empleo:
    - Puesto: {job_title}
    - Empresa: {company}
    - Descripción / Detalles: {job_snippet}
    
    Tu tarea:
    Adapta y reescribe mi CV base en formato Markdown para esta oferta en específico. 
    1. Asegúrate de destacar y rellenar estratégicamente con las tecnologías, habilidades y palabras clave (keywords) exactas que pide la oferta, sin inventar empleos falsos ni mentir sobre mi experiencia real (Ecopetrol, XM, ITM, tecnologías como Python, React, .NET, Azure, etc.).
    2. Mantén el tono profesional, técnico y orientado a resultados.
    3. Devuelve únicamente el contenido del CV optimizado en formato Markdown limpio.
    """

  try:
    response = model.generate_content(prompt)
    return response.text
  except Exception as e:
    print(f"Error generando CV optimizado con Gemini: {e}")
    return "Error al procesar la IA."


def generate_cover_letter(job_title: str, company: str) -> str:
  """Genera una carta de presentación ejecutiva y directa para la vacante."""
  base_cv = load_base_cv()
  model = genai.GenerativeModel("gemini-1.5-flash")

  prompt = f"""
    Basándote en este perfil profesional:
    {base_cv}
    
    Redacta una carta de presentación corta, moderna y persuasiva (en español) dirigida al equipo de selección de la empresa '{company}' para el puesto de '{job_title}'. 
    La carta debe resaltar por qué mi experiencia como Desarrollador Full Stack (Python, React, Azure, .NET) encaja perfecto con lo que buscan. Sé directo, profesional y evita formalismos excesivos o clichés aburridos.
    """

  try:
    response = model.generate_content(prompt)
    return response.text
  except Exception as e:
    print(f"Error generando Cover Letter con Gemini: {e}")
    return "Error al procesar la Cover Letter."