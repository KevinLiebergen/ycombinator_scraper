import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "../.env"))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DB_PATH = os.getenv("DB_PATH") or os.path.join(BASE_DIR, "../data", "jobs.db")

HN_JOB_STORIES_URL = "https://hacker-news.firebaseio.com/v0/jobstories.json"
HN_ITEM_URL_TEMPLATE = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
HN_DISCUSSION_URL_TEMPLATE = "https://news.ycombinator.com/item?id={id}"

REQUEST_TIMEOUT = 10
REQUEST_RETRIES = 3
REQUEST_BACKOFF = 2

TELEGRAM_MESSAGE_DELAY = int(os.getenv("TELEGRAM_MESSAGE_DELAY", "3"))
