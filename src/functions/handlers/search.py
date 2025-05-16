import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from ..config import DB_PATH

# --- Поиск по тексту ---
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи ключевое слово для поиска после /search одной строкой")
        return
    keyword = " ".join(context.args).lower()
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
        await update.message.reply_text("Ничего не найдено")
    else:
        for (file_id,) in rows:
            await update.message.reply_sticker(file_id)