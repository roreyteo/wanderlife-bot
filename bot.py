import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📸 Subir foto y comenzar", callback_data="subir_foto")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 ¡Bienvenido a WanderLife Bot!\n\n"
        "Sube tu foto y te animamos en cualquier ciudad del mundo 🌍\n\n"
        "Presiona el botón para comenzar:",
        reply_markup=reply_markup
    )

# Maneja botones
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "subir_foto":
        await query.edit_message_text("📸 Perfecto, ahora sube tu foto:")

    elif query.data == "continente_europa":
        await mostrar_ciudades(query, "europa")
    elif query.data == "continente_asia":
        await mostrar_ciudades(query, "asia")
    elif query.data == "continente_america":
        await mostrar_ciudades(query, "america")

    elif query.data.startswith("ciudad_"):
        ciudad = query.data.replace("ciudad_", "")
        context.user_data["ciudad"] = ciudad
        await mostrar_efectos(query, ciudad)

    elif query.data.startswith("efecto_"):
        efecto = query.data.replace("efecto_", "")
        ciudad = context.user_data.get("ciudad", "París")
        await query.edit_message_text(
            f"⚙️ Generando tu video en *{ciudad}* con efecto *{efecto}*...\n\n"
            "⏳ Esto puede tardar unos segundos.",
            parse_mode="Markdown"
        )

# Muestra menú de continentes
async def mostrar_continentes(update, foto_id):
    keyboard = [
        [InlineKeyboardButton("🌍 Europa", callback_data="continente_europa")],
        [InlineKeyboardButton("🌏 Asia", callback_data="continente_asia")],
        [InlineKeyboardButton("🌎 América", callback_data="continente_america")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌍 Elige un continente:", reply_markup=reply_markup)

# Muestra ciudades por continente
async def mostrar_ciudades(query, continente):
    ciudades = {
        "europa": [("🗼 París", "París"), ("🏛️ Roma", "Roma"), ("💂 Londres", "Londres"), ("🌊 Santorini", "Santorini")],
        "asia": [("🗾 Tokio", "Tokio"), ("🏙️ Dubai", "Dubai"), ("🦁 Singapur", "Singapur"), ("🛺 Bangkok", "Bangkok")],
        "america": [("🗽 Nueva York", "Nueva York"), ("🌉 Buenos Aires", "Buenos Aires"), ("🌮 Ciudad de México", "Ciudad de México"), ("🏖️ Río de Janeiro", "Río de Janeiro")],
    }
    keyboard = [[InlineKeyboardButton(nombre, callback_data=f"ciudad_{ciudad}")] for nombre, ciudad in ciudades[continente]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🏙️ Elige una ciudad:", reply_markup=reply_markup)

# Muestra efectos
async def mostrar_efectos(query, ciudad):
    keyboard = [
        [InlineKeyboardButton("🚶 Caminar", callback_data="efecto_caminar")],
        [InlineKeyboardButton("👋 Saludar", callback_data="efecto_saludar")],
        [InlineKeyboardButton("💬 Frase motivacional", callback_data="efecto_frase")],
        [InlineKeyboardButton("🎤 Presentación", callback_data="efecto_presentacion")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"🎬 Ciudad: *{ciudad}*\n\nElige un efecto:", reply_markup=reply_markup, parse_mode="Markdown")

# Recibe foto
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    foto = update.message.photo[-1]
    context.user_data["foto_id"] = foto.file_id
    await mostrar_continentes(update, foto.file_id)

# Error handler
async def error_handler(update, context):
    logger.error("Error no controlado mientras se procesaba un update", exc_info=context.error)

def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("Falta TELEGRAM_TOKEN en el entorno (.env).")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_error_handler(error_handler)
    print("Bot corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()
