from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram import BotCommand
from functions.config import BOT_TOKEN
from functions.database import init_db
from functions.handlers import start, add_set_command, handle_sticker, search_command

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