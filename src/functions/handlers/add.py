import re
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from .stickerpack import add_sticker_pack_by_name

WAITING_FOR_SET = 1

# --- Начало команды /add ---
async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь ссылку на стикерпак, который нужно добавить:")
    return WAITING_FOR_SET

# --- Обработка ввода после /add ---
async def receive_set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    match = re.match(r"^https://t\.me/addstickers/([a-zA-Z0-9_]+)$", text)

    if not match:
        await update.message.reply_text("❌ Это не похоже на ссылку на стикерпак.")
        return ConversationHandler.END

    set_name = match.group(1)

    try:
        success_count, fail_count, title = await add_sticker_pack_by_name(set_name, update.effective_user.id, context.bot)
        await update.message.reply_text(
            f"✅ Добавлено стикеров: {success_count}\n❌ Ошибок: {fail_count}\n📦 Пак: {title}",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception:
        await update.message.reply_text("❌ Не удалось загрузить стикерпак.")

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

    try:
        success_count, fail_count, title = await add_sticker_pack_by_name(set_name, update.effective_user.id, context.bot)
        await update.message.reply_text(
            f"✅ Обработано стикеров: {success_count}\n❌ Ошибок: {fail_count}\n📦 Пак: {title}"
        )
    except Exception:
        await update.message.reply_text("❌ Не удалось загрузить стикерпак.")