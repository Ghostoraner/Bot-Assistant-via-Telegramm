from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.database.engine import AsyncSessionLocal
from app.database.models import User
from app.locales import MESSAGES, get_msg, USER_LANG

menu_router = Router()

async def get_user_lang(user_id: int) -> str:
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, language="ru")
            session.add(user)
            await session.commit()
            return "ru"
        return user.language or "ru"

def get_main_kb(lang: str) -> ReplyKeyboardMarkup:
    msg = MESSAGES.get(lang, MESSAGES["ru"])
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=msg["btn_jobs"]), KeyboardButton(text=msg["btn_tasks"])],
            [KeyboardButton(text=msg["btn_planner"]), KeyboardButton(text=msg["btn_ai"])],
            [KeyboardButton(text=msg["btn_settings"]), KeyboardButton(text=msg["btn_info"])]
        ],
        resize_keyboard=True
    )

def get_settings_kb(lang: str) -> ReplyKeyboardMarkup:
    msg = MESSAGES.get(lang, MESSAGES["ru"])
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=msg["btn_change_lang"])],
            [KeyboardButton(text=msg["btn_back"])]
        ],
        resize_keyboard=True
    )

@menu_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_user_lang(message.from_user.id)
    USER_LANG[message.from_user.id] = lang
    await message.answer(
        get_msg(message.from_user.id, "menu_welcome"),
        reply_markup=get_main_kb(lang)
    )

@menu_router.message(F.text.in_([MESSAGES["ru"]["btn_settings"], MESSAGES["en"]["btn_settings"]]))
async def btn_settings(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_user_lang(message.from_user.id)
    await message.answer(
        get_msg(message.from_user.id, "settings_title"),
        reply_markup=get_settings_kb(lang),
        parse_mode="Markdown"
    )

@menu_router.message(F.text.in_([MESSAGES["ru"]["btn_change_lang"], MESSAGES["en"]["btn_change_lang"]]))
async def change_language(message: Message):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(id=message.from_user.id, language="ru")
            session.add(user)

        new_lang = "en" if user.language == "ru" else "ru"
        user.language = new_lang
        await session.commit()
        USER_LANG[message.from_user.id] = new_lang

        await message.answer(
            get_msg(message.from_user.id, "lang_changed"),
            reply_markup=get_settings_kb(new_lang)
        )


@menu_router.message(F.text.in_([MESSAGES["ru"]["btn_back"], MESSAGES["en"]["btn_back"]]))
async def btn_back(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_user_lang(message.from_user.id)
    await message.answer(
        get_msg(message.from_user.id, "menu_welcome"),
        reply_markup=get_main_kb(lang)
    )