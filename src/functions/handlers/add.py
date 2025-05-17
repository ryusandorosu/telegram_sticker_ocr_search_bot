import re
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from .stickerpack import add_sticker_pack_by_name

WAITING_FOR_SET = 1

# --- Начало команды /add ---
async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь стикер или ссылку на стикерпак, который нужно добавить:")
    return WAITING_FOR_SET

# --- Обработка ввода после /add ---
async def receive_set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    match = re.match(r"^https://t\.me/addstickers/([a-zA-Z0-9_]+)$", text)

    if not match:
        await update.message.reply_text("❌ Это не похоже на ссылку на стикерпак.")
        return ConversationHandler.END

    set_name = match.group(1)
    progress = await update.message.reply_text("Началась обработка стикерпака...")

    try:
        success_count, fail_count, title = await add_sticker_pack_by_name(
            set_name,
            update.effective_user.id,
            context.bot,
            progress_message=progress
        )
        await update.message.reply_text(
            f"Обработка стикерпака завершена.",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при загрузке стикерпака. {str(e)}")

    return ConversationHandler.END

# --- Отмена ---
async def cancel_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- Обработка отправленного стикера ---
async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker = update.message.sticker
    set_name = sticker.set_name

    if not set_name:
        await update.message.reply_text("❌ У этого стикера нет набора (set_name отсутствует)")
        return

    progress = await update.message.reply_text("Началась обработка стикерпака...")

    try:
        success_count, fail_count, title = await add_sticker_pack_by_name(
            set_name,
            update.effective_user.id,
            context.bot,
            progress_message=progress
        )
        await update.message.reply_text(
            f"Обработка стикерпака завершена."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при загрузке стикерпака. {str(e)}")