import sqlite3
from telegram import Bot
from ..ocr import recognize_sticker
from ..config import DB_PATH
from .. import logger

async def add_sticker_pack_by_name(set_name: str, user_id: int, bot: Bot) -> tuple[int, int, str]:
    try:
        sticker_set = await bot.get_sticker_set(set_name)
    except Exception as e:
        logger.warning(f"Ошибка при получении пака {set_name}: {e}")
        raise

    success_count = 0
    fail_count = 0

    for sticker in sticker_set.stickers:
        try:
            file = await bot.get_file(sticker.file_id)
            image_data = await file.download_as_bytearray()
            text = await recognize_sticker(image_data)

            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("INSERT OR IGNORE INTO sticker_sets VALUES (?, ?)", (set_name, sticker_set.title))
                c.execute("INSERT OR IGNORE INTO user_sets VALUES (?, ?)", (user_id, set_name))
                c.execute(
                    "INSERT OR REPLACE INTO stickers VALUES (?, ?, ?, ?)",
                    (sticker.file_id, set_name, sticker.emoji or "", text)
                )
            success_count += 1
        except Exception as e:
            logger.warning(f"Ошибка при обработке стикера {sticker.file_id}: {e}")
            fail_count += 1

    return success_count, fail_count, sticker_set.title