import os
import sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config.settings as settings

settings.DB_PATH = os.path.join(tempfile.gettempdir(), "ycombinator_scrapper_test.db")
if os.path.exists(settings.DB_PATH):
    os.remove(settings.DB_PATH)

from src.database import init_db, has_any_jobs, job_exists, save_job, get_latest_jobs

init_db()
assert has_any_jobs() is False, "Fresh DB should report no jobs"

fake_job = {
    "id": 999999,
    "title": "Test Co is hiring",
    "link": "https://example.com",
    "by": "tester",
    "time": 1700000000,
}
save_job(fake_job)

assert has_any_jobs() is True
assert job_exists(999999) is True
assert job_exists(123) is False

latest = get_latest_jobs(limit=5)
print("Latest jobs:", latest)
assert latest[0][0] == "999999"

print("SUCCESS: database round-trip works as expected.")
os.remove(settings.DB_PATH)
