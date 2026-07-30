import os
import logging
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from groq import AsyncGroq

from app.locales import MESSAGES, get_msg
from app.handlers.menu import get_main_kb, get_user_lang

logger = logging.getLogger(__name__)

ai_router = Router()

# Ініціалізація асинхронного клієнта Groq без жорстко прописаного ключа
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))


class AIState(StatesGroup):
    waiting_for_prompt = State()


def get_ai_kb(lang: str) -> ReplyKeyboardMarkup:
    exit_text = "❌ Выйти из AI" if lang == "ru" else "❌ Exit AI Mode"
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=exit_text)]],
        resize_keyboard=True
    )


# Вхід у режим AI
@ai_router.message(F.text.in_([MESSAGES["ru"]["btn_ai"], MESSAGES["en"]["btn_ai"]]))
async def enter_ai_mode(message: Message, state: FSMContext):
    lang = await get_user_lang(message.from_user.id)
    await state.set_state(AIState.waiting_for_prompt)

    msg_text = (
        "🤖 **Режим ИИ включен.** Задайте любой вопрос:"
        if lang == "ru"
        else "🤖 **AI Mode enabled.** Ask me anything:"
    )
    await message.answer(msg_text, reply_markup=get_ai_kb(lang), parse_mode="Markdown")


# Вихід з режиму AI
@ai_router.message(AIState.waiting_for_prompt, F.text.in_(["❌ Выйти из AI", "❌ Exit AI Mode"]))
async def exit_ai_mode(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_user_lang(message.from_user.id)
    await message.answer(
        get_msg(message.from_user.id, "menu_welcome"),
        reply_markup=get_main_kb(lang)
    )


# Обробка запиту до Groq
@ai_router.message(AIState.waiting_for_prompt)
async def handle_ai_prompt(message: Message, state: FSMContext):
    # Якщо натиснули головну кнопку меню замість тексту
    if message.text in [
        MESSAGES["ru"]["btn_jobs"], MESSAGES["en"]["btn_jobs"],
        MESSAGES["ru"]["btn_settings"], MESSAGES["en"]["btn_settings"],
        MESSAGES["ru"]["btn_tasks"], MESSAGES["en"]["btn_tasks"]
    ]:
        await state.clear()
        lang = await get_user_lang(message.from_user.id)
        await message.answer("Вы вышли из режима AI.", reply_markup=get_main_kb(lang))
        return

    # Перевірка наявності ключа перед запитом
    if not os.getenv("GROQ_API_KEY"):
        logger.error("GROQ_API_KEY is missing in environment variables.")
        await message.answer("❌ Ошибка конфигурации: API ключ Groq не найден.")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        response = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Ты — вежливый и лаконичный ИИ-ассистент внутри Telegram-бота. Отвечай четко, по делу и на том языке, на котором пишет пользователь."
                },
                {"role": "user", "content": message.text}
            ],
            temperature=0.7,
            max_tokens=1024
        )

        answer = response.choices[0].message.content
        if answer:
            await message.answer(answer)
        else:
            await message.answer("⚠️ Не удалось получить ответ от ИИ.")

    except Exception as e:
        logger.error(f"Groq API Error: {e}")
        await message.answer("❌ Произошла ошибка при обращении к ИИ. Проверьте настройки или повторите позже.")