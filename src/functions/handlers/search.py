import sqlite3
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from ..config import DB_PATH

WAITING_FOR_QUERY = 1

# --- Начало поиска ---
async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введи текст для поиска по стикерам:")
    return WAITING_FOR_QUERY

# --- Обработка поискового запроса ---
async def receive_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyword = update.message.text.lower().strip()
    user_id = update.effective_user.id
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT file_id FROM stickers
            WHERE text LIKE ? AND set_name IN (
                SELECT set_name FROM user_sets WHERE user_id = ?
            )
            LIMIT 5
        ''', (f"%{keyword}%", user_id))
        rows = c.fetchall()
    if not rows:
        await update.message.reply_text("Ничего не найдено", reply_markup=ReplyKeyboardRemove())
    else:
        for (file_id,) in rows:
            await update.message.reply_sticker(file_id)
    return ConversationHandler.END

# --- Отмена ---
async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Поиск отменён.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END