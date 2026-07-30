from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select, delete

from app.database.engine import AsyncSessionLocal
from app.database.models import Task, Planer, User
from app.locales import get_msg, USER_LANG, MESSAGES

tasks_planner_router = Router()

class TaskStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_deadline = State()

class DeleteTaskState(StatesGroup):
    waiting_for_id = State()

async def sync_user_lang(user_id: int):
    if user_id not in USER_LANG:
        async with AsyncSessionLocal() as session:
            user = await session.get(User, user_id)
            USER_LANG[user_id] = user.language if user else "ru"

@tasks_planner_router.message(F.text.in_([MESSAGES["ru"]["btn_tasks"], MESSAGES["en"]["btn_tasks"]]))
async def show_tasks(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    await sync_user_lang(uid)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Task).where(Task.user_id == uid))
        tasks = result.scalars().all()

    text = get_msg(uid, "tasks_title") + "\n\n"
    if not tasks:
        text += get_msg(uid, "tasks_empty")
    else:
        for t in tasks:
            status = "✅" if t.is_completed else "📌"
            text += f"**ID: {t.id}** | {status} {t.title}\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_msg(uid, "btn_add_task"), callback_data="add_task")],
        [InlineKeyboardButton(text=get_msg(uid, "btn_del_task"), callback_data="del_task")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@tasks_planner_router.callback_query(F.data == "add_task")
async def start_add_task(call: CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    await sync_user_lang(uid)
    await state.set_state(TaskStates.waiting_for_title)
    await call.message.answer(get_msg(uid, "enter_task_title"))
    await call.answer()

@tasks_planner_router.message(TaskStates.waiting_for_title)
async def process_task_title(message: Message, state: FSMContext):
    uid = message.from_user.id
    await state.update_data(title=message.text)
    await state.set_state(TaskStates.waiting_for_deadline)
    await message.answer(get_msg(uid, "enter_task_deadline"))

@tasks_planner_router.message(TaskStates.waiting_for_deadline)
async def process_task_deadline(message: Message, state: FSMContext):
    uid = message.from_user.id
    data = await state.get_data()
    title = data['title']

    if message.text.lower() not in ["нет", "no"]:
        title += f" (DL: {message.text})"

    async with AsyncSessionLocal() as session:
        new_task = Task(user_id=uid, title=title, is_completed=False)
        session.add(new_task)
        await session.commit()

    await state.clear()
    await message.answer(get_msg(uid, "task_added", title=title), parse_mode="Markdown")

@tasks_planner_router.callback_query(F.data == "del_task")
async def start_del_task(call: CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    await sync_user_lang(uid)
    await state.set_state(DeleteTaskState.waiting_for_id)
    await call.message.answer(get_msg(uid, "enter_task_id_del"))
    await call.answer()

@tasks_planner_router.message(DeleteTaskState.waiting_for_id)
async def process_del_task(message: Message, state: FSMContext):
    uid = message.from_user.id
    if not message.text.isdigit():
        await message.answer(get_msg(uid, "invalid_id"))
        return

    task_id = int(message.text)
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Task).where(Task.id == task_id, Task.user_id == uid))
        await session.commit()

    await state.clear()
    await message.answer(get_msg(uid, "task_deleted", task_id=task_id))

@tasks_planner_router.message(F.text.in_([MESSAGES["ru"]["btn_planner"], MESSAGES["en"]["btn_planner"]]))
async def show_planner(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    await sync_user_lang(uid)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Planer).where(Planer.user_id == uid))
        plans = result.scalars().all()

    if not plans:
        await message.answer(get_msg(uid, "planner_empty"))
        return

    text = get_msg(uid, "planner_title") + "\n\n"
    for p in plans:
        date_str = p.due_date.strftime("%d.%m.%Y")
        text += f"📌 **{p.title}** ({date_str})\n"

    await message.answer(text, parse_mode="Markdown")