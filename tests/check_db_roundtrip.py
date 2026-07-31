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
    "title": "Test Co (YC W25) is hiring a Backend Engineer in Berlin",
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
job_id, title, link, by, role, location, posted_at, date_added = latest[0]
assert job_id == "999999"
assert role == "Backend Engineer", f"unexpected role: {role!r}"
assert location == "Berlin", f"unexpected location: {location!r}"

os.remove(settings.DB_PATH)

# A database created before role/location existed must migrate and backfill.
import sqlite3

conn = sqlite3.connect(settings.DB_PATH)
conn.execute("""
    CREATE TABLE jobs (
        id TEXT PRIMARY KEY, title TEXT, link TEXT, by TEXT, posted_at TEXT, date_added TEXT
    )
""")
conn.execute(
    "INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?)",
    ("1", "Old Co (YC S20) Is Hiring a Data Scientist (Remote)", "https://example.com",
     "tester", "2020-01-01 00:00:00 UTC", "2020-01-01"),
)
conn.commit()
conn.close()

init_db()
migrated = get_latest_jobs(limit=1)[0]
assert migrated[4] == "Data Scientist", f"backfilled role: {migrated[4]!r}"
assert migrated[5] == "Remote", f"backfilled location: {migrated[5]!r}"
print("Migrated legacy row:", migrated)

init_db()  # migration must be idempotent
assert get_latest_jobs(limit=1)[0] == migrated

print("SUCCESS: database round-trip works as expected.")
os.remove(settings.DB_PATH)
