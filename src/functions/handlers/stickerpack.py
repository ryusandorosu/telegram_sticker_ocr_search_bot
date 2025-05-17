import sqlite3
from telegram import Bot, Message
from ..ocr import recognize_sticker
from ..config import DB_PATH
from .. import logger

async def add_sticker_pack_by_name(set_name: str, user_id: int, bot: Bot, progress_message: Message | None = None):
    try:
        sticker_set = await bot.get_sticker_set(set_name)
    except Exception as e:
        logger.warning(f"Ошибка при получении пака {set_name}: {e}")
        raise

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM sticker_sets WHERE set_name = ?", (set_name,))
        if c.fetchone():
            raise Exception("Этот стикерпак уже добавлен.")

        c.execute("INSERT OR IGNORE INTO sticker_sets VALUES (?, ?)", (set_name, sticker_set.title))
        c.execute("INSERT OR IGNORE INTO user_sets VALUES (?, ?)", (user_id, set_name))

    success_count = 0
    fail_count = 0
    total_count = len(sticker_set.stickers)

    for sticker in sticker_set.stickers:
        try:
            file = await bot.get_file(sticker.file_id)
            image_data = await file.download_as_bytearray()
            text = await recognize_sticker(image_data)
            logger.info(f"Распознан текст для {sticker.file_id} в паке {set_name}:\n'{text}'")

            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT OR REPLACE INTO stickers VALUES (?, ?, ?, ?)",
                    (sticker.file_id, set_name, sticker.emoji or "", text)
                )
            success_count += 1

            if progress_message:
                progress_text = (
                    f"📦 Обработка пака: {sticker_set.title}\n"
                    f"📊 Всего стикеров: {total_count}\n"
                    f"✅ Успешно: {success_count}\n"
                    f"❌ Ошибок: {fail_count}\n"
                    f"♿️ Обрабатывается: {sticker.file_id}"
                    f"🔤 Текст: {text or '---'}"
                )
                try:
                    await progress_message.edit_text(progress_text)
                except Exception as e:
                    logger.warning(f"Не удалось обновить сообщение: {e}")

        except Exception as e:
            logger.warning(f"Ошибка при обработке стикера {sticker.file_id}: {e}")
            fail_count += 1

    return success_count, fail_count, sticker_set.title