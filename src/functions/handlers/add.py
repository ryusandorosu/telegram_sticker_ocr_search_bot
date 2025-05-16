import re
import sqlite3
from telegram import Update, Sticker
from telegram.ext import ContextTypes
from ..ocr import recognize_sticker
from ..config import DB_PATH
from .. import logger

# --- Обработка команды /add ---
async def add_set_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи название стикерпака или ссылку на него сразу после /add одной строкой")
        return
    arg = context.args[0]
    set_name = re.sub(r"^https://t.me/addstickers/", "", arg)
    try:
        sticker_set = await context.bot.get_sticker_set(set_name)
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO sticker_sets VALUES (?, ?)", (sticker_set.name, sticker_set.title))
            c.execute("INSERT OR IGNORE INTO user_sets VALUES (?, ?)", (update.effective_user.id, sticker_set.name))
        await update.message.reply_text(f"Добавлен пак: {sticker_set.title}")
    except Exception as e:
        logger.warning(f"Ошибка при добавлении пака: {e}")
        await update.message.reply_text("Не удалось найти стикерпак.")

# --- Обработка отправленного стикера ---
async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker: Sticker = update.message.sticker
    set_name = sticker.set_name
    file_id = sticker.file_id
    emoji = sticker.emoji or ""
    try:
        file = await context.bot.get_file(file_id)
        image_data = await file.download_as_bytearray()
        text = await recognize_sticker(image_data)

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO sticker_sets VALUES (?, ?)", (set_name, set_name))
            c.execute("INSERT OR IGNORE INTO user_sets VALUES (?, ?)", (update.effective_user.id, set_name))
            c.execute("INSERT OR REPLACE INTO stickers VALUES (?, ?, ?, ?)", (file_id, set_name, emoji, text))

        await update.message.reply_text(f"Стикер добавлен. Распознанный текст: {text}")
    except Exception as e:
        logger.warning(f"Ошибка обработки стикера: {e}")
        await update.message.reply_text("Ошибка обработки стикера")