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
from aiogram.exceptions import TelegramBadRequest

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@simplify_ai"

# --- Настройки текста ---
INTRO_TEXT = "✅ Спасибо за подписку!\n\nСмотри подборки по рубрикам ниже:\n"
OUTRO_TEXT = "\nСледи за новыми публикациями на канале!"

# Вставляем невидимый символ перед "http" чтобы Telegram не тянул превью
def no_preview(text: str) -> str:
    return text.replace("http", "\u200bhttp")

# --- Рубрики (заполняй своими пунктами) ---
LIFE_BEST = [
    "Gamma.app — Презентации с помощью ИИ",
    "scribbr.com — Проверка грамматики, плагиата и оформление текста",
    "aistudio.google.com — Личный AI-помощник на экране в реальном времени",
    "app.heygen.com — Перевод видео с озвучкой твоим голосом и синхронизацией губ",
    "quso.ai — Нарезка видео на короткие ролики с помощью ИИ",
    "krea.ai — Генерация изображений, 3D-объектов и видео по тексту",
    "runwayml.com — Удаление фона, генерация видео и визуальные эффекты",
    "remove.bg — Удаление фона с изображений за секунду",
    "geospy.ai — Поиск места по фотографии",
    "clipdrop.co — Улучшение изображений, удаление фона, света и объектов",
    "app.lupaupscaler.com — Увеличение чёткости и разрешения фото без потери качества",
    "looka.com — Генерация логотипов, цветовой схемы и бренд-дизайна по названию",
    "poe.com — Все популярные AI-боты в одном окне: ChatGPT, Claude, Gemini и др.",
    "dora.run — Визуальный AI-конструктор сайтов с анимацией и 3D без кода",
    "mokker.ai — Замена фона на фото с эффектом студийной съёмки",
    "pixverse.ai — Генерация видео по текстовому описанию в стиле Sora",
    "ideogram.ai — Генерация изображений с текстом и визуальными эффектами",
    "immersity.ai — Оживление фотографий за секунду",
    "app.submagic.co — Автоматическая генерация субтитров и монтаж под Shorts",
    "clipdrop.co/relight — Освещение картинки, как в студии",
    "cluely.com — Невидимый AI-помощник в видеозвонках и браузере",
    "higgsfield.ai — Создание анимации Earth Zoom Out и AI-видео по фото",
    "recraft.ai — Генерация иллюстраций и графики в любом стиле: от пиксель-арта до 3D",
    "flowith.io — Создание AI-интерфейсов и 3D-генераторов по текстовому описанию",
    "hailuoai.video — Анимация фото в видеоклипы по описанию: стиль как у Sora, но доступно уже сейчас",
    "x-minus.pro — Удаление вокала из песен онлайн, за секунды: создавай минусовки без программ",
    "animejs.com — Библиотека готовых веб-анимаций",
    "easyedit.io — Онлайн-редактор текстом фото с AI",
    "we-img-search.ordinall.me — Поиск любых обоев по скриншоту",
    "contentcore.xyz — Создаёт мокапы, 3D-логотипы, 3D-тексты и иконки",
    "paperanimator.com — Превращает статичную картинку в бумажную анимацию",
    "pentestgpt.ai — Этичный GPT хаккер",
    "tools.dverso.io — Самый милый способ удалить фон с фото",
    "huggingface.co — Создай сайт за пару минут без кодинга",
    "app.topoexport.com — Создавай карту местности в пару кликов",
    "chefgpt.xyz — Создай рецепт из того, что есть в холодильнике",
    "cleanup.pictures — Легко удали объект с фото",
    "@ToolProBot — ChatGPT5 и Gemini прямо в телеграм",
    "klingai.com — Один из лучших генераторов видео",
    "storytribeapp.com — Создавай сториборды в пару кликов",
    "reactbits.dev — Анимированные элементы для твоего проекта",
    "gentube.app — Генерация изображений за секунды",
    "printpal.io — Создание 3D моделей по фотографии",
    "productioncrate.com — Тысячи визуальных эффектов, 3D моделей и персонажей для проектов",
    "flux-context.org — Реставрация фото в пару кликов",
    "kittl.com — Шаблоны для твоего дизайна с возможностью редактирования",
    "myinstants.com — Звуки для твоих видео",
    "thiings.co — Эмодзи на любой вкус",
    "fakedetail.com — Создавай фейковые переписки",
    "liquid.paper.design — Анимируй лого, текст (эффект жидкого металла)",
    "pixie.haus — Создавай пиксель-арты",
    "buildcores.com — Собери свой ПК с 3D визуализацией",
    "planyourroom.com — Создай проект своей комнаты",
    "startmycar.com — Вся информация про машины",
    "speech2text.ru — Видео или аудио в текст",
    "yt1s.ltd — Скачать видео с YouTube",
    "seostudio.tools — Сотни SEO инструментов",
    "remove.photos — Редактируй изображение в браузере",
    "jitter.video — Настраиваемые анимации",
    "tools.flaex.ai — Список всех нейронок в одном месте",
    "systemrequirementslab.com — Проверь, потянет ли твой ПК игру",
    "ifixit.com — Почини всё что угодно",
    "unicorn.studio — Крутые анимации для твоих проектов",
    "smart.servier.com — Тысячи изображение по медицине и биологии",
    "opus.pro — Делай нарезки из подкастов, интервью или просто длинных видео",
    "app.paperanimator.com/text-match-cut — Бумажная анимация за секунды",
    "1aauto.com — Почини своё авто самостоятельно",
    "collov.ai — Преобрази свою комнату с этой нейронкой в пару кликов",
]

FUN_BEST = [
    "slowroads.io — Бесконечный симулятор вождения",
    "3dtuning.com — Тюнингуй любые машины",
    "eaglecraft.com — Майнкрафт прямо в браузере",
]

WIN_TIPS = [
    "github.com/Maplespe/ExplorerBlurMica/releases — Прозрачный проводник (Mica/Blur)",
]

# --- Кнопки ---
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

channel_button = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Перейти на канал", url="https://t.me/simplify_ai")]]
)
update_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Обновить", callback_data="refresh")]]
)
start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/start")]], resize_keyboard=True)

# --- Вспомогательная отправка: рубрику кусками по 50 ---
async def send_category(chat_id: int, title: str, items: list[str], prefix: str = "", suffix: str = ""):
    if not items:
        return
    chunk_size = 50
    total = len(items)
    for i in range(0, total, chunk_size):
        chunk = items[i : i + chunk_size]
        body = "\n".join([f"{i + j + 1}. {v}" for j, v in enumerate(chunk)])
        text = f"{title}\n{body}"
        if prefix and i == 0:
            text = prefix + text
        if suffix and (i + chunk_size >= total):
            text = text + suffix

        await bot.send_message(
            chat_id=chat_id,
            text=no_preview(text),
            disable_web_page_preview=True
        )

# --- Отправка всех рубрик в нужном порядке ---
async def send_all_categories(chat_id: int):
    # 1) Упростят жизнь   2) Спасут от скуки   3) Фишки Windows
    await send_category(chat_id, "💡 Лучшие сайты, которые упростят жизнь:", LIFE_BEST, prefix=INTRO_TEXT)
    await send_category(chat_id, "🎯 Лучшие сайты, которые спасут от скуки:", FUN_BEST)
    await send_category(chat_id, "🪟 Фишки для Windows, о которых ты должен знать:", WIN_TIPS, suffix=OUTRO_TEXT)

# --- Команда /start с проверкой подписки ---
@router.message(F.text == "/start")
async def cmd_start(message: types.Message):
    try:
        # Аккуратно проверяем подписку
        is_subscribed = False
        try:
            member = await bot.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
            status = getattr(member, "status", None)
            is_subscribed = status in (
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR,
            )
        except TelegramBadRequest:
            is_subscribed = False

        if is_subscribed:
            await send_all_categories(message.chat.id)
            await message.answer(
                "Нажми «Обновить», чтобы снова получить списки по рубрикам",
                reply_markup=update_kb,
                disable_web_page_preview=True
            )
        else:
            await message.answer(
                "❗Чтобы получить доступ, подпишись на канал:",
                reply_markup=channel_button,
                disable_web_page_preview=True
            )
            await message.answer(
                "🔁 После подписки нажми «Проверить подписку» ниже ⬇️",
                reply_markup=start_kb,
                disable_web_page_preview=True
            )
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки: {e}")
        await message.answer(
            "⚠️ Произошла ошибка при проверке подписки. Убедись, что бот добавлен в канал и у него есть права.",
            reply_markup=start_kb,
            disable_web_page_preview=True
        )

# --- Обработчик inline-кнопки «Обновить» ---
@router.callback_query(F.data == "refresh")
async def refresh_list(callback: types.CallbackQuery):
    await send_all_categories(callback.message.chat.id)
    await callback.message.answer(
        "Нажми «Обновить», чтобы снова получить списки по рубрикам",
        reply_markup=update_kb,
        disable_web_page_preview=True
    )
    await callback.answer()

# --- Ping endpoint для Render (чтобы UptimeRobot будил сервис) ---
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
    await asyncio.gather(
        dp.start_polling(bot),
        run_web()
    )

if __name__ == "__main__":
    asyncio.run(main())

