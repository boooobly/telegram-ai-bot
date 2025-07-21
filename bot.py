from aiohttp import web
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@simplify_ai"

WELCOME_TEXT = """ ✅ Спасибо за подписку!

Вот список полезных AI-сервисов из моих коротких видео:
1. Gamma.app — Презентации с помощью ИИ
2. scribbr.com — Проверка грамматики, плагиата и оформление текста
3. aistudio.google.com — Личный AI-помощник на экране в реальном времени
4. app.heygen.com — Перевод видео с озвучкой твоим голосом и синхронизацией губ
5. quso.ai — Нарезка видео на короткие ролики с помощью ИИ
6. krea.ai — Генерация изображений, 3D-объектов и видео по тексту
7. runwayml.com — Удаление фона, генерация видео и визуальные эффекты
8. remove.bg — Удаление фона с изображений за секунду
9. geospy.ai — Поиск места по фотографии
10. clipdrop.co — Улучшение изображений, удаление фона, света и объектов
11. app.lupaupscaler.com — Увеличение чёткости и разрешения фото без потери качества
12. looka.com — Генерация логотипов, цветовой схемы и бренд-дизайна по названию
13. poe.com — Все популярные AI-боты в одном окне: ChatGPT, Claude, Gemini и др.
14. dora.run — Визуальный AI-конструктор сайтов с анимацией и 3D без кода
15. mokker.ai — Замена фона на фото с эффектом студийной съёмки
16. pixverse.ai — Генерация видео по текстовому описанию в стиле Sora
17. ideogram.ai — Генерация изображений с текстом и визуальными эффектами
18. immersity.ai — Оживление фотографий за секунду
19. app.submagic.co — Автоматическая генерация субтитров и монтаж под Shorts
20. clipdrop.co/relight — Освещение картинки, как в студии
21. cluely.com — Невидимый AI-помощник в видеозвонках и браузере
22. higgsfield.ai — Создание анимации Earth Zoom Out и AI-видео по фото
23. recraft.ai — Генерация иллюстраций и графики в любом стиле: от пиксель-арта до 3D
24. flowith.io — Создание AI-интерфейсов и 3D-генераторов по текстовому описанию
25. hailuoai.video — Анимация фото в видеоклипы по описанию: стиль как у Sora, но доступно уже сейчас
26. x-minus.pro — Удаление вокала из песен онлайн, за секунды: создавай минусовки без программ

Следи за новыми публикациями на канале! """  # Твой текст с AI-сервисами

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

channel_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Перейти на канал", url="https://t.me/simplify_ai")]
    ]
)

start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/start")]],
    resize_keyboard=True
)

@router.message(F.text == "/start")
async def cmd_start(message: types.Message):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            await message.answer(WELCOME_TEXT, reply_markup=start_kb)
        else:
            await message.answer(
                "❗Чтобы получить доступ, подпишись на канал:",
                reply_markup=channel_button
            )
            await message.answer(
                "🔁 После подписки нажми «Проверить подписку» ниже ⬇️",
                reply_markup=start_kb
            )
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки: {e}")
        await message.answer(
            "⚠️ Произошла ошибка при проверке подписки. Убедись, что бот добавлен в канал и у него есть права.",
            reply_markup=start_kb
        )

async def handle_ping(request):
    return web.Response(text="OK")

async def run_web():
    app = web.Application()
    app.add_routes([web.get('/', handle_ping)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

async def main():
    logging.basicConfig(level=logging.INFO)
    # Запускаем одновременно веб-сервер и polling бота
    await asyncio.gather(
        dp.start_polling(bot),
        run_web()
    )

if __name__ == "__main__":
    asyncio.run(main())
