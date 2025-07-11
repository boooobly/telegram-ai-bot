import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router, F

import os
API_TOKEN = os.getenv("BOT_TOKEN") 
CHANNEL_USERNAME = "@simplify_ai"       

WELCOME_TEXT = """
✅ Спасибо за подписку!

Вот список полезных AI-сервисов:
1. Gamma.app — Презентации с помощью ИИ
2. scribbr.com — Проверка грамматики, плагиата и оформление текста
3. aistudio.google.com — Личный AI-помощник на экране в реальном времени
4. app.heygen.com — Перевод видео с озвучкой твоим голосом и синхронизацией губ
5. quso.ai — Нарезка видео на короткие ролики с помощью ИИ
6. krea.ai — Генерация изображений, 3D-объектов и видео по тексту
7. runwayml.com — Удаление фона, генерация видео и визуальные эффекты
8. remove.bg — Удаление фона с изображений за секунду
9. geospy.ai — Поиск места по фотографии

Следи за новыми публикациями на канале!
"""

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

@router.message(F.text == "/start")
async def cmd_start(message: types.Message):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            await message.answer(WELCOME_TEXT)
        else:
            await message.answer(
                "❗Чтобы получить доступ, подпишись на канал "
                f"<a href='https://t.me/simplify_ai'>{CHANNEL_USERNAME}</a>"
            )
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки: {e}")
        await message.answer(
            "⚠️ Произошла ошибка при проверке подписки. Убедись, что бот добавлен в канал и у него есть права."
        )

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
