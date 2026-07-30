import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MYSQL_URL = os.getenv("MYSQL_URL")


missing_vars = []
if not BOT_TOKEN:
    missing_vars.append("BOT_TOKEN")
if not GROQ_API_KEY:
    missing_vars.append("GROQ_API_KEY")
if not MYSQL_URL:
    missing_vars.append("MYSQL_URL")

if missing_vars:
    logging.critical(f"Критичні змінні оточення відсутні: {', '.join(missing_vars)}")
    sys.exit(1)