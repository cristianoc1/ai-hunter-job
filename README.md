# 🤖 AI Job Hunter & ATS Optimizer

Agente automatizado para la búsqueda de ofertas laborales tecnológicas (Python, React, .NET, Azure), diseñado para ejecutarse de forma gratuita mediante GitHub Actions y notificar a Telegram con opciones interactivas para adaptar el currículum (ATS) usando inteligencia artificial (Google Gemini).

## 🚀 Características
- **Búsqueda Automatizada:** Conectado a la API de Jooble para filtrar vacantes de valor.
- **Control de Duplicados:** Almacenamiento y validación en Supabase para evitar alertas repetidas.
- **Optimización ATS con IA:** Utiliza Google Gemini para adaptar tu CV maestro a cada oferta específica.
- **Generación de PDF:** Convierte el CV optimizado en un documento formal y estilizado listo para postularte.
- **Notificaciones Interactivas:** Alertas directas a Telegram con botones de acción rápida.

## 🛠️ Tecnologías
- Python, Requests, BeautifulSoup
- Supabase (Database)
- Google Generative AI (Gemini)
- WeasyPrint (Generación de PDF)
- Telegram Bot API
- GitHub Actions (Infraestructura Serverless gratuita)
