from aiohttp import web
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, Update,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.exceptions import TelegramBadRequest

# === Env ===
API_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # напр.: https://telegram-ai-bot-tptq.onrender.com
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change_me")
PORT = int(os.getenv("PORT", 8000))

if not API_TOKEN or not APP_URL:
    raise RuntimeError("BOT_TOKEN и APP_URL должны быть заданы в переменных окружения.")

CHANNEL_USERNAME = "@simplify_ai"

# === Texts ===
WELCOME = "✅ Добро пожаловать!\n\nВыбери нужную рубрику ниже 👇"
OUTRO = "\nСледи за новыми публикациями на канале!"
HOME_BTN_TEXT = "🏠 Главное меню"

def no_preview(text: str) -> str:
    """Отключаем предпросмотр ссылок (вставляем zero-width space перед http)."""
    return text.replace("http", "\u200bhttp")

# === Data (можно вынести в JSON позже) ===
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
    "insmind.com — Сотни AI инструментов. От генерации изображений, до генерации видео",
    "vidu.com — Генерация видео, как в топовых нейронках",
    "vsthemes.org — Курсоры, обои, игры и многое другое",
    "yarn.co — Сотни тысяч вырезок из фильмов по ключевому слову",
    "tripo3d.ai — Создавай 3D модели по текстовому запросу или по изображению",
    "posemy.art — Создавай позы персонажей или бери готовые позы",
    "home.by.me — Создай планировку для своей квартиры",
    "whitescreen.online — Проверь битые пиксели, поставь windows обновляться или разыграй друга",
    "uiball.com — Элементы загрузки для твоих проектов",
    "motormatchup.com — Сравни машины",
    "animagraffs.com — Десятки примеров, как устроенны сложные вещи в 3D визуализации",
    "dungeonscrawl.com — Рисуй карты в разных стиляй под свой вкус",
    "myretrotvs.com — Погрузись в детсво с этим ретро телевизором",
    "chemequations.com — Реши любые химические уравнения",
    "cymath.com — Реши любое математическое уравнение",
    "freesewing.eu — Создавай свои раскройки для одежды в пару кликов",
    "24ai.tech — Десятки AI инструментов для изображений",
    "builditapp.com — Сотни инструкций по постройкам в майнкрафт",
    "musicgpt.com — Создавай музыку под свой вкус с помощью ИИ",
    "app.endlesstools.io — Создавай 3D модели, кастомизируй изображения, создавай 3D текст",
    "womp.com — Сайт на котором можно делать 3D модели",
    "kimi.com — Создавай презентации в пару кликов",
    "thetoymaker.com — Создавай собственные бумажные игрушки",
    "sketchfab.com — Тысячи 3D моделей на любой вкус",
    "kiddoworksheets.com — Создавай задачки для детей или бери уже готовые",
    "autodraw.com — Сделай из наброска, готовый рисунок",
    "foldbook.art — Создавай арт-объекты из книг",
    "textstudio.com — Крутые дизайны для текста, баннеры, постеры и др.",
    "bitmap.designfamilymarket.com — Обрабокта фотографии в bit стиле",
    "science.nasa.gov/specials/your-name-in-landsat — Напиши своё имя из ландшафтов на Земле",
]

FUN_BEST = [
    "slowroads.io — Бесконечный симулятор вождения",
    "3dtuning.com — Тюнингуй любые машины",
    "eaglecraft.com — Майнкрафт прямо в браузере",
    "zty.pe — Прокачай свой скилл набора текста в игровом формате",
    "oskarstalberg.com/Townscaper — Построй свой остров",
]

WIN_TIPS = [
    "github.com/Maplespe/ExplorerBlurMica/releases — Прозрачный Проводник (Mica/Blur)",
]

CATEGORIES = {
    "life": {"title": "💡 Лучшие сайты, которые упростят жизнь:", "items": LIFE_BEST},
    "fun":  {"title": "🎯 Лучшие сайты, которые спасут от скуки:", "items": FUN_BEST},
    "win":  {"title": "🪟 Фишки Windows, о которых ты должен знать:", "items": WIN_TIPS},
}

# === aiogram ===
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# === Keyboards ===
# Reply-клавиатура (всегда снизу)
home_reply_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=HOME_BTN_TEXT)]],
    resize_keyboard=True
)

# Главное меню (inline)
def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💡 Лучшие сайты", callback_data="show:life")],
            [InlineKeyboardButton(text="🎯 Сайты от скуки", callback_data="show:fun")],
            [InlineKeyboardButton(text="🪟 Фишки Windows", callback_data="show:win")],
        ]
    )

# Кнопки раздела (inline): Обновить + две другие рубрики
def section_menu_kb(current: str) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="🔁 Обновить раздел", callback_data=f"refresh:{current}")]]
    for key, label in (("life", "💡 Лучшие сайты"), ("fun", "🎯 Сайты от скуки"), ("win", "🪟 Фишки Windows")):
        if key != current:
            buttons.append([InlineKeyboardButton(text=label, callback_data=f"show:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# === Helpers ===
async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        status = getattr(member, "status", None)
        return status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)
    except TelegramBadRequest:
        return False

async def send_category(chat_id: int, key: str):
    data = CATEGORIES[key]
    title = data["title"]
    items = data["items"]
    if not items:
        await bot.send_message(chat_id, no_preview(f"{title}\n(пока пусто)"), disable_web_page_preview=True)
        return

    chunk_size = 50
    total = len(items)
    for i in range(0, total, chunk_size):
        chunk = items[i:i+chunk_size]
        body = "\n".join([f"{i + j + 1}. {v}" for j, v in enumerate(chunk)])
        text = f"{title}\n{body}"
        if i + chunk_size >= total:
            text += OUTRO
        await bot.send_message(
            chat_id,
            no_preview(text),
            disable_web_page_preview=True
        )

async def send_main_menu(chat_id: int):
    """Сначала включаем reply-клавиатуру, затем показываем inline-меню разделов."""
    # 1) Включаем нижнюю reply-клавиатуру
    await bot.send_message(
        chat_id,
        "Кнопка «🏠 Главное меню» всегда внизу 👇",
        reply_markup=home_reply_kb,
        disable_web_page_preview=True
    )
    # 2) Показываем inline-главное меню разделов
    await bot.send_message(
        chat_id,
        no_preview(WELCOME),
        reply_markup=main_menu_kb(),
        disable_web_page_preview=True
    )

# === Handlers ===
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    try:
        if await is_user_subscribed(message.from_user.id):
            await send_main_menu(message.chat.id)
        else:
            # Показываем reply-клавиатуру тоже (пусть всегда будет)
            await message.answer(
                "❗Чтобы получить доступ к рубрикам, подпишись на канал:\nhttps://t.me/simplify_ai",
                reply_markup=home_reply_kb,
                disable_web_page_preview=True
            )
            await message.answer(
                "После подписки снова нажми /start или «🏠 Главное меню» ⬇️",
                reply_markup=home_reply_kb,
                disable_web_page_preview=True
            )
    except Exception as e:
        logging.exception(f"Ошибка в /start: {e}")
        await message.answer(
            "⚠️ Произошла ошибка. Проверь, что бот добавлен в канал и у него есть права.",
            reply_markup=home_reply_kb,
            disable_web_page_preview=True
        )

# Нажатие на нижнюю reply-кнопку «Главное меню»
@dp.message(F.text == HOME_BTN_TEXT)
async def on_home_button(message: types.Message):
    if await is_user_subscribed(message.from_user.id):
        await send_main_menu(message.chat.id)
    else:
        await message.answer(
            "❗Чтобы открыть разделы, подпишись на канал:\nhttps://t.me/simplify_ai",
            reply_markup=home_reply_kb,
            disable_web_page_preview=True
        )

@dp.callback_query(F.data.startswith("show:"))
async def on_show(callback: types.CallbackQuery):
    key = callback.data.split(":", 1)[1]
    if key not in CATEGORIES:
        await callback.answer("Неизвестная рубрика", show_alert=True)
        return
    if not await is_user_subscribed(callback.from_user.id):
        await callback.message.answer(
            "❗Чтобы открыть разделы, подпишись на канал:\nhttps://t.me/simplify_ai",
            reply_markup=home_reply_kb,
            disable_web_page_preview=True
        )
        await callback.answer()
        return

    await send_category(callback.message.chat.id, key)
    await callback.message.answer(
        "Выбери следующий раздел или обнови текущий:",
        reply_markup=section_menu_kb(key),
        disable_web_page_preview=True
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("refresh:"))
async def on_refresh(callback: types.CallbackQuery):
    key = callback.data.split(":", 1)[1]
    if key not in CATEGORIES:
        await callback.answer("Неизвестная рубрика", show_alert=True)
        return
    if not await is_user_subscribed(callback.from_user.id):
        await callback.message.answer(
            "❗Чтобы открыть разделы, подпишись на канал:\nhttps://t.me/simplify_ai",
            reply_markup=home_reply_kb,
            disable_web_page_preview=True
        )
        await callback.answer()
        return

    await send_category(callback.message.chat.id, key)
    await callback.message.answer(
        "Выбери следующий раздел или обнови текущий:",
        reply_markup=section_menu_kb(key),
        disable_web_page_preview=True
    )
    await callback.answer("Обновлено")

# --- Fallback-хэндлер для любых непонятных сообщений ---
@dp.message()
async def fallback_message(message: types.Message):
    # Сюда попадает всё, что не совпало с другими хэндлерами:
    # произвольный текст, медиа, стикеры, голосовые, команды и т.п.
    await message.answer(
        "Я понимаю только команду /start и нажатия на кнопки.\n"
        "Нажми «🏠 Главное меню» ниже, чтобы вернуться к выбору разделов.",
        reply_markup=home_reply_kb,
        disable_web_page_preview=True
    )

# --- Fallback-хэндлер для любых непонятных callback-кнопок ---
@dp.callback_query()
async def fallback_callback(callback: types.CallbackQuery):
    # Например, если кнопка устарела или колбэк неизвестен
    await callback.answer("Кнопка больше неактивна. Используй «🏠 Главное меню».", show_alert=False)


# === Webhook server ===
async def handle_ping(request):  # healthcheck
    return web.Response(text="OK")

async def webhook_handler(request: web.Request):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != WEBHOOK_SECRET:
        return web.Response(status=403, text="Forbidden")

    try:
        data = await request.json()
        update = Update.model_validate(data)
    except Exception as e:
        logging.exception(f"Bad update payload: {e}")
        return web.Response(status=400, text="Bad Request")

    await dp.feed_update(bot, update)
    return web.Response(text="OK")

async def setup_webhook():
    url = f"{APP_URL}/webhook/{WEBHOOK_SECRET}"
    logging.info(f"Setting webhook to: {url}")
    await bot.set_webhook(url=url, secret_token=WEBHOOK_SECRET, drop_pending_updates=True)

async def run_web():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_post(f"/webhook/{WEBHOOK_SECRET}", webhook_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logging.info(f"Web server started on port {PORT}")

    while True:
        await asyncio.sleep(3600)

async def main():
    logging.basicConfig(level=logging.INFO)
    await setup_webhook()
    await run_web()

if __name__ == "__main__":
    asyncio.run(main())


























