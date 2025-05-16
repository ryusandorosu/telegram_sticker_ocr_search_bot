import re
import sqlite3
import logging
import pytesseract
from PIL import Image
from io import BytesIO
from telegram import Update, Sticker, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Конфигурация ---
BOT_TOKEN = "8126189458:AAHpWe3HrGcnlld9KpQtx645WjnPWs4twds"
DB_PATH = "stickers.db"

# --- Инициализация базы данных ---
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS sticker_sets (
                set_name TEXT PRIMARY KEY,
                title TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_sets (
                user_id INTEGER,
                set_name TEXT,
                PRIMARY KEY(user_id, set_name)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS stickers (
                file_id TEXT PRIMARY KEY,
                set_name TEXT,
                emoji TEXT,
                text TEXT
            )
        ''')

# --- OCR распознавание ---
async def recognize_sticker(image_data: bytes) -> str:
    img = Image.open(BytesIO(image_data))
    text = pytesseract.image_to_string(img, lang='eng+rus')
    return text.strip()

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли стикер или напиши /add <название или ссылка> в одну строку.")

# --- Обработка команды /добавить ---
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

# --- Запуск бота ---
def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_set_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))

    app.bot.set_my_commands([
        BotCommand("start", "Запуск бота"),
        BotCommand("add", "Добавить стикерпак"),
        BotCommand("search", "Поиск по распознанному тексту"),
    ])

    print("Бот запущен")
    try:
        app.run_polling()
    finally:
        print("Бот остановлен")

if __name__ == "__main__":
    main()