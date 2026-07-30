MESSAGES = {
    "ru": {
        "menu_welcome": "Главное меню. Выберите действие:",
        "settings_title": "⚙️ **Настройки**\nТекущий язык: **Русский**",
        "menu_prompt": "Возврат в главное меню.",
        "lang_changed": "🌐 Язык успешно изменен на Русский!",
        "info_text": "🤖 **Бот-помощник v1.0**\n\nПредназначен для парсинга заказов с 10+ фриланс-бирж, управления задачами и планирования проектов.",

        # Кнопки Главного Меню
        "btn_jobs": "🔍 Поиск работы",
        "btn_tasks": "📋 Задачи",
        "btn_planner": "📅 Планировщик",
        "btn_ai": "🤖 Ассистент ИИ",
        "btn_settings": "⚙️ Настройки",
        "btn_info": "ℹ️ Инфо",

        # Настройки
        "btn_change_lang": "🌐 Сменить язык (EN)",
        "btn_back": "🔙 Назад",

        # Задачи
        "tasks_title": "📋 **Ваши задачи:**",
        "tasks_empty": "Список задач пуст.",
        "btn_add_task": "➕ Добавить задачу",
        "btn_del_task": "🗑 Удалить задачу",
        "enter_task_title": "Введите название задачи:",
        "enter_task_deadline": "Укажите дедлайн (например: 31.12.2026 18:00) или напишите 'нет':",
        "task_added": "✅ Задача **'{title}'** успешно добавлена!",
        "enter_task_id_del": "Введите ID задачи для удаления:",
        "invalid_id": "Пожалуйста, введите корректный числовой ID.",
        "task_deleted": "🗑 Задача ID {task_id} удалена.",

        # Планировщик
        "planner_title": "📅 **Сохраненные проекты:**",
        "planner_empty": "📅 **Планировщик пуст.**\n\nСохраняйте проекты из раздела 'Поиск работы' сюда!",

        # Поиск работы
        "job_menu_title": "🔍 **Поиск работы**\nТекущее направление: **{cat}**",
        "btn_run_search": "🚀 Найти новые заказы",
        "btn_select_cat": "🎯 Выбрать направление",
        "searching": "🔎 Ищу свежие заказы на биржах (Freelancehunt, Habr, Kwork, FL, Upwork, Weblancer)...",
        "no_jobs": "К сожалению, свежих заказов по данному направлению не найдено.",
        "btn_open_job": "🔗 Открыть заказ на бирже",
        "btn_to_planner": "📌 В планировщик",
        "job_saved": "✅ Проект добавлен в Планировщик!",
        "select_cat_title": "Выберите специализацию для поиска заказов:",
        "cat_changed": "Направление изменено на: {cat}"
    },
    "en": {
        "menu_welcome": "Main menu. Select an action:",
        "settings_title": "⚙️ **Settings**\nCurrent language: **English**",
        "menu_prompt": "Returned to main menu.",
        "lang_changed": "🌐 Language successfully changed to English!",
        "info_text": "🤖 **Assistant Bot v1.0**\n\nDesigned for parsing orders from 10+ freelance exchanges, task management, and project planning.",

        # Main Menu Buttons
        "btn_jobs": "🔍 Job Search",
        "btn_tasks": "📋 Tasks",
        "btn_planner": "📅 Planner",
        "btn_ai": "🤖 AI Assistant",
        "btn_settings": "⚙️ Settings",
        "btn_info": "ℹ️ Info",

        # Settings
        "btn_change_lang": "🌐 Change language (RU)",
        "btn_back": "🔙 Back",

        # Tasks
        "tasks_title": "📋 **Your Tasks:**",
        "tasks_empty": "Task list is empty.",
        "btn_add_task": "➕ Add Task",
        "btn_del_task": "🗑 Delete Task",
        "enter_task_title": "Enter task title:",
        "enter_task_deadline": "Enter deadline (e.g., 31.12.2026 18:00) or write 'no':",
        "task_added": "✅ Task **'{title}'** successfully added!",
        "enter_task_id_del": "Enter Task ID to delete:",
        "invalid_id": "Please enter a valid numeric ID.",
        "task_deleted": "🗑 Task ID {task_id} deleted.",

        # Planner
        "planner_title": "📅 **Saved Projects:**",
        "planner_empty": "📅 **Planner is empty.**\n\nSave projects from 'Job Search' here!",

        # Job Search
        "job_menu_title": "🔍 **Job Search**\nCurrent direction: **{cat}**",
        "btn_run_search": "🚀 Search New Orders",
        "btn_select_cat": "🎯 Select Specialization",
        "searching": "🔎 Searching for new orders on exchanges (Freelancehunt, Habr, Kwork, FL, Upwork, Weblancer)...",
        "no_jobs": "No new orders found for this direction.",
        "btn_open_job": "🔗 Open order link",
        "btn_to_planner": "📌 Save to Planner",
        "job_saved": "✅ Project added to Planner!",
        "select_cat_title": "Select specialization for job parsing:",
        "cat_changed": "Category changed to: {cat}"
    }
}

TEXTS = MESSAGES
USER_LANG = {}

def get_msg(user_id: int, key: str, **kwargs) -> str:
    lang = USER_LANG.get(user_id, "ru")
    text = MESSAGES.get(lang, MESSAGES["ru"]).get(key, "")
    return text.format(**kwargs) if kwargs else text