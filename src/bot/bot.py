import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler
from dotenv import load_dotenv

from src.scrapers.job_scraper import fetch_filtered_jobs
from src.ai.gemini_ai import optimize_cv_for_job, generate_cover_letter
from src.pdf.pdf_generator import create_cv_pdf

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)


async def run_job_hunter(context: ContextTypes.DEFAULT_TYPE = None):
    """Función principal que ejecuta el buscador de ofertas y notifica a Telegram."""
    print("🚀 Ejecutando ciclo de búsqueda de empleo...")
    jobs = fetch_filtered_jobs()

    if not jobs:
        print("No se encontraron nuevas ofertas en este ciclo.")
        if context:
            await context.bot.send_message(chat_id=CHAT_ID, text="🔍 No se encontraron nuevas ofertas en esta ejecución.")
        return

    for job in jobs:
        title = job["title"]
        company = job["company"]
        location = job["location"]
        url = job["url"]

        # Creamos botones interactivos en Telegram para cada oferta
        # Usamos callback_data cortos codificados o simplificados para la demo
        keyboard = [
            [
                InlineKeyboardButton("🎯 Adaptar CV (ATS)", callback_data="adapt_cv"),
                InlineKeyboardButton("✉️ Cover Letter", callback_data="cover_letter")
            ],
            [
                InlineKeyboardButton("🔗 Ver Oferta Original", url=url)
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = (
            f"🚨 *¡Nueva Oferta Detectada!*\n\n"
            f"• *Puesto:* {title}\n"
            f"• *Empresa:* {company}\n"
            f"• *Ubicación:* {location}\n\n"
            f"¿Qué deseas hacer con esta vacante?"
        )

        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        # Pequeña pausa entre mensajes si hay varias ofertas
        await asyncio.sleep(1)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja las acciones cuando presionas los botones interactivos en Telegram."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    # Extraemos el texto del mensaje anterior para saber de qué oferta se habla
    original_message = query.message.text

    if data == "adapt_cv":
        await query.message.reply_text("⏳ Analizando la oferta y adaptando tu CV con Gemini (ATS)... por favor espera unos segundos.")
        
        # Simulamos extracción de datos del mensaje (puedes estructurarlo mejor según tus necesidades)
        optimized_cv = optimize_cv_for_job("Desarrollador Full Stack", "Empresa Tech", original_message)
        pdf_path = create_cv_pdf(optimized_cv)
        
        if pdf_path and os.path.exists(pdf_path):
            await query.message.reply_document(
                document=open(pdf_path, "rb"),
                filename="CV_Cristian_Morales_Optimizado.pdf",
                caption="✅ ¡Aquí tienes tu CV optimizado y adaptado para pasar los filtros ATS de esta vacante!"
            )
        else:
            await query.message.reply_text("Hubo un error generando el PDF.")

    elif data == "cover_letter":
        await query.message.reply_text("⏳ Redactando tu carta de presentación personalizada...")
        cover_text = generate_cover_letter("Desarrollador Full Stack", "Empresa Tech")
        
        await query.message.reply_text(
            f"✉️ *Carta de Presentación Sugerida:*\n\n{cover_text}",
            parse_mode="Markdown"
        )


async def manual_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /buscar en Telegram para forzar una búsqueda manual."""
    await update.message.reply_text("🔍 Iniciando búsqueda manual de empleo...")
    await run_job_hunter(context)


def main():
    """Inicia el bot de Telegram en modo escucha para los botones."""
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Comando para buscar manualmente desde el chat
    application.add_handler(CommandHandler("buscar", manual_search))
    # Manejador de los botones interactivos
    application.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot de Telegram iniciado y escuchando interacciones...")
    application.run_polling()


if __name__ == "__main__":
    # Si se ejecuta directamente el script sin argumentos, hace una ejecución del buscador y sale
    # (Ideal para GitHub Actions). Si quieres dejar el bot corriendo con polling, puedes descomentar main()
    # Por defecto, para GitHub Actions ejecutaremos directamente la función de búsqueda:
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "bot":
        main()
    else:
        asyncio.run(run_job_hunter())