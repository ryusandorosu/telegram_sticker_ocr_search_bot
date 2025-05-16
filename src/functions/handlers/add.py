import re
import sqlite3
from telegram import Update, Sticker, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from ..ocr import recognize_sticker
from ..config import DB_PATH
from .. import logger

WAITING_FOR_SET = 1

# --- Начало команды /add ---
async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь название или ссылку на стикерпак, который нужно добавить:")
    return WAITING_FOR_SET

# --- Обработка ввода после /add ---
async def receive_set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = update.message.text.strip()
    set_name = re.sub(r"^https://t.me/addstickers/", "", arg)
    try:
        sticker_set = await context.bot.get_sticker_set(set_name)
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO sticker_sets VALUES (?, ?)", (sticker_set.name, sticker_set.title))
            c.execute("INSERT OR IGNORE INTO user_sets VALUES (?, ?)", (update.effective_user.id, sticker_set.name))
        await update.message.reply_text(f"Добавлен пак: {sticker_set.title}", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        logger.warning(f"Ошибка при добавлении пака: {e}")
        await update.message.reply_text("Не удалось найти стикерпак.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- Отмена ---
async def cancel_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

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