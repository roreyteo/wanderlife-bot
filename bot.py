import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import Conflict
from config import TELEGRAM_TOKEN
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    await update.message.reply_text(
        "👋 ¡Hola! Bienvenido a WanderLife Bot\n\n"
        "Pronto podrás:\n"
        "🌍 Elegir una ciudad del mundo\n"
        "📸 Subir tu foto\n"
        "🎬 Recibir un video animado hablando\n\n"
        "Por ahora escríbeme algo para probar 😊"
    )

# Responde mensajes de texto
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return
    texto = update.message.text
    await update.message.reply_text(f"Recibí tu mensaje: {texto}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Error no controlado mientras se procesaba un update", exc_info=context.error)

# Arranque del bot
def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("Falta TELEGRAM_TOKEN en el entorno (.env).")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_error_handler(error_handler)
    print("Bot corriendo...")
    try:
        app.run_polling()
    except Conflict:
        logger.error("Conflicto de polling: ya hay otra instancia del bot ejecutándose.")
    except Exception:
        logger.exception("Fallo al iniciar el bot.")

if __name__ == "__main__":
    main()
