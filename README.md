# AI Job Hunter

Busca ofertas de empleo tecnológico en Colombia con la API de Jooble y envía a
Telegram alertas de vacantes remotas o ubicadas en Medellín, sin requisitos
explícitos de inglés, junto con el enlace directo para postularte. Así, las
ofertas presenciales fuera de Medellín se descartan.
Esta versión **no adapta el CV ni genera cartas o PDF**.

Jooble agrega ofertas de distintas fuentes; este proyecto consulta Jooble y no
integra directamente LinkedIn, Computrabajo, Indeed ni Magneto. Los filtros de
modalidad e inglés se basan en el texto que Jooble devuelve y pueden omitir una
oferta remota o no detectar un requisito redactado de otra forma.

## Flujo automático

GitHub Actions ejecuta la búsqueda diariamente a las 8:00 a. m. de Colombia
(13:00 UTC). El workflow funciona en los servidores de GitHub: tu computadora
no necesita estar encendida. También puedes iniciar una ejecución manual desde
**Actions → Daily Job Hunter → Run workflow**.

El schedule debe estar en la rama predeterminada del repositorio y Actions debe
estar habilitado. GitHub puede retrasar los schedules, así que la hora es
orientativa. El uso gratuito depende del plan y de los límites de Actions,
Jooble y Supabase.

## Configuración

### GitHub Actions

En **Settings → Secrets and variables → Actions**, configura estos *repository
secrets*:

| Secreto | Uso |
| --- | --- |
| `JOOBLE_API_KEY` | Consultar ofertas en Jooble |
| `TELEGRAM_TOKEN` | Enviar alertas con el bot |
| `CHAT_ID` | Chat que recibirá las alertas |
| `SUPABASE_URL` | URL del proyecto Supabase |
| `SUPABASE_KEY` | Clave de Supabase con acceso a `jobs_sent` |

El workflow está en
[`job_hunter.yml`](./.github/workflows/job_hunter.yml).

### Supabase

La tabla inicial `jobs_sent` debe tener `id`, `title`, `company`, `url` y
`created_at`. Ejecuta una sola vez en el SQL Editor de Supabase la
[migración](./supabase/migrations/20261105_add_job_delivery_details.sql). Añade
los campos de ubicación, descripción y estado que el scraper utiliza para
controlar los envíos y deja las ofertas existentes marcadas como enviadas.

La clave configurada en `SUPABASE_KEY` debe tener permisos de lectura,
inserción y actualización sobre `jobs_sent`. No publiques esa clave.

## Prueba local

Copia `.env.example` a `.env` y completa sus variables. No subas `.env` al
repositorio. En PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.bot.bot
```

## Más adelante: adaptar el CV

La plantilla `templates/cv_base.md` se conserva como referencia, pero el scraper
y este workflow no la leen ni la envían a ningún servicio. La automatización
para entregar un CV adaptado se diseñará aparte.

## Tecnologías

Python, Jooble API, Supabase, Telegram Bot API y GitHub Actions.
