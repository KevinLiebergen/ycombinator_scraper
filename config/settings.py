import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, "../.env"))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

_db_path = os.getenv("DB_PATH") or os.path.join("data", "jobs.db")
DB_PATH = _db_path if os.path.isabs(_db_path) else os.path.join(PROJECT_ROOT, _db_path)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

HN_JOB_STORIES_URL = "https://hacker-news.firebaseio.com/v0/jobstories.json"
HN_ITEM_URL_TEMPLATE = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
HN_DISCUSSION_URL_TEMPLATE = "https://news.ycombinator.com/item?id={id}"

REQUEST_TIMEOUT = 10
REQUEST_RETRIES = 3
REQUEST_BACKOFF = 2

TELEGRAM_MESSAGE_DELAY = int(os.getenv("TELEGRAM_MESSAGE_DELAY", "3"))
