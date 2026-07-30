import hashlib
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.services.parser_service import FreelanceService
from app.database.engine import AsyncSessionLocal
from app.database.models import Planer
from app.locales import get_msg

job_router = Router()
freelance_service = FreelanceService()

JOBS_CACHE = {}
USER_CATEGORIES = {}

CATEGORIES = {
    "python": "🐍 Python / Backend",
    "frontend": "💻 Web Frontend",
    "fullstack": "🌐 Fullstack Web",
    "mobile": "📱 Mobile (Flutter/Android/iOS)",
    "cpp": "⚙️ C++ / Embedded",
    "all": "❇️ Все направления"
}


@job_router.message(F.text.in_(["🔍 Поиск работы", "🔍 Job Search"]))
async def search_jobs_menu(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    cat_code = USER_CATEGORIES.get(uid, "all")
    cat_name = CATEGORIES.get(cat_code, "❇️ Все направления")

    text = get_msg(uid, "job_menu_title", cat=cat_name)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_msg(uid, "btn_run_search"), callback_data="run_job_search")],
        [InlineKeyboardButton(text=get_msg(uid, "btn_select_cat"), callback_data="open_cat_select")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")


@job_router.callback_query(F.data == "open_cat_select")
async def select_category_menu(call: CallbackQuery):
    uid = call.from_user.id
    buttons = []
    for code, name in CATEGORIES.items():
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"set_cat:{code}")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.edit_text(get_msg(uid, "select_cat_title"), reply_markup=kb)


@job_router.callback_query(F.data.startswith("set_cat:"))
async def set_category(call: CallbackQuery):
    uid = call.from_user.id
    cat_tag = call.data.split("set_cat:")[1]
    USER_CATEGORIES[uid] = cat_tag

    cat_name = CATEGORIES.get(cat_tag, "All")
    await call.answer(get_msg(uid, "cat_changed", cat=cat_name), show_alert=True)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_msg(uid, "btn_run_search"), callback_data="run_job_search")],
        [InlineKeyboardButton(text=get_msg(uid, "btn_select_cat"), callback_data="open_cat_select")]
    ])
    await call.message.edit_text(get_msg(uid, "job_menu_title", cat=cat_name), reply_markup=kb, parse_mode="Markdown")


@job_router.callback_query(F.data == "run_job_search")
async def run_search(call: CallbackQuery):
    uid = call.from_user.id
    category = USER_CATEGORIES.get(uid, "all")
    await call.answer()
    await call.message.answer(get_msg(uid, "searching"))

    jobs = await freelance_service.get_jobs(category=category)

    if not jobs:
        await call.message.answer(get_msg(uid, "no_jobs"))
        return

    for job in jobs:
        job_id = hashlib.md5(job['link'].encode()).hexdigest()[:10]
        JOBS_CACHE[job_id] = job['title']

        text = (
            f"📌 **{job['title']}**\n"
            f"💰 **Бюджет:** {job['price']}\n"
            f"🏛 **Биржа:** {job['source']}"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_msg(uid, "btn_open_job"), url=job['link'])],
            [InlineKeyboardButton(text=get_msg(uid, "btn_to_planner"), callback_data=f"save_p:{job_id}")]
        ])
        await call.message.answer(text, reply_markup=kb, parse_mode="Markdown")


@job_router.callback_query(F.data.startswith("save_p:"))
async def save_job_to_planner(call: CallbackQuery):
    uid = call.from_user.id
    job_id = call.data.split("save_p:")[1]
    title = JOBS_CACHE.get(job_id, "Freelance Job")

    async with AsyncSessionLocal() as session:
        new_plan = Planer(
            user_id=uid,
            title=f"Заказ: {title[:50]}",
            due_date=datetime.now()
        )
        session.add(new_plan)
        await session.commit()

    await call.answer(get_msg(uid, "job_saved"), show_alert=True)