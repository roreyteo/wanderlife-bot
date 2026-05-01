import logging
import os
import asyncio
import tempfile
import replicate
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN, REPLICATE_API_TOKEN

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Bienvenido a WanderLife Bot!\n\n"
        "Escribe /video y luego sube una foto para generar tu video animado."
    )

async def video_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["esperando_foto"] = True
    await update.message.reply_text("📸 Perfecto, ahora sube tu foto:")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("FOTO RECIBIDA")
    if not context.user_data.get("esperando_foto"):
        await update.message.reply_text("Escribe /video primero.")
        return

    context.user_data["esperando_foto"] = False
    tmp_path = None

    try:
        await update.message.reply_text("⬇️ Descargando tu foto...")
        
        # 1. Descargar foto de Telegram a archivo temporal
        foto = update.message.photo[-1]
        foto_file = await context.bot.get_file(foto.file_id)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            await foto_file.download_to_drive(tmp.name)
            tmp_path = tmp.name

        await update.message.reply_text("⬆️ Preparando imagen para Replicate...")

        # 2. Subir a Replicate para obtener URL pública (necesario porque Telegram no permite acceso externo)
        loop = asyncio.get_event_loop()
        public_url = await loop.run_in_executor(None, lambda: replicate.files.upload(tmp_path))
        logger.info(f"URL PÚBLICA: {public_url}")

        await update.message.reply_text("⏳ Generando video, espera 1-3 minutos... (esto usa GPU)")

        # 3. Generar video
        video_url = await loop.run_in_executor(None, lambda: generar_video(public_url))
        logger.info(f"VIDEO URL: {video_url}")

        await update.message.reply_video(
            video=video_url,
            caption="🎬 ¡Tu video está listo!"
        )

    except Exception as e:
        logger.error(f"Error en photo_handler: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error al generar el video: {str(e)}")
    finally:
        # 4. Limpiar archivo temporal
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

def generar_video(foto_url):
    output = replicate.run(
        "cjwbw/sadtalker:3aa3dac9353cc4d6bd62a4a9b33baa574c549d376",
        input={
            "source_image": foto_url,
            "driven_audio": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
            "preprocess": "full",
            "still_mode": False,
            "use_enhancer": True,
            "batch_size": 1,
            "size": 256,
            "pose_style": 0,
            "facerender": "facevid2vid",
            "exp_scale": 1.0
        }
    )
    return output

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Error no controlado", exc_info=context.error)
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ Ocurrió un error interno. Intenta de nuevo.")

def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("Falta TELEGRAM_TOKEN en el entorno (.env).")
        
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("video", video_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_error_handler(error_handler)
    
    print("🤖 Bot corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()
