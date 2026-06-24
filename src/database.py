import sqlite3
from datetime import datetime, timezone

from config.settings import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            link TEXT,
            by TEXT,
            posted_at TEXT,
            date_added TEXT
        )
    """)
    conn.commit()
    conn.close()


def has_any_jobs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM jobs")
    count = c.fetchone()[0]
    conn.close()
    return count > 0


def job_exists(job_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM jobs WHERE id=?", (str(job_id),))
    result = c.fetchone()
    conn.close()
    return result is not None


def save_job(job):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    posted_at = (
        datetime.fromtimestamp(job["time"], tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        if job.get("time") else None
    )
    c.execute("""
        INSERT OR IGNORE INTO jobs (id, title, link, by, posted_at, date_added)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(job["id"]),
        job.get("title"),
        job["link"],
        job.get("by"),
        posted_at,
        datetime.now().strftime("%Y-%m-%d"),
    ))
    conn.commit()
    conn.close()


def get_latest_jobs(limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, title, link, by, posted_at, date_added
        FROM jobs
        ORDER BY rowid DESC
        LIMIT ?
    """, (limit,))
    results = c.fetchall()
    conn.close()
    return results
