from telegram.ext import ApplicationBuilder, ConversationHandler, CommandHandler, MessageHandler, filters
from telegram import BotCommand
from functions.config import BOT_TOKEN
from functions.database import init_db
from functions.handlers import start, start_add, receive_set_name, cancel_add, handle_sticker, WAITING_FOR_SET, start_search, receive_query, cancel_search, WAITING_FOR_QUERY

def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    add_conv = ConversationHandler(
        entry_points=[CommandHandler("add", start_add)],
        states={
            WAITING_FOR_SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_set_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel_add)],
    )

    search_conv = ConversationHandler(
        entry_points=[CommandHandler("search", start_search)],
        states={
            WAITING_FOR_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_query)],
        },
        fallbacks=[CommandHandler("cancel", cancel_search)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(add_conv)
    app.add_handler(search_conv)
    app.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))

    app.bot.set_my_commands([
        BotCommand("start", "Запуск бота"),
        BotCommand("add", "Добавить стикерпак"),
        BotCommand("search", "Поиск по распознанному тексту"),
        BotCommand("cancel", "Отменить команду")
    ])

    print("Бот запущен")
    try:
        app.run_polling()
    finally:
        print("Бот остановлен")

if __name__ == "__main__":
    main()