import sqlite3
from datetime import datetime, timezone

from config.settings import DB_PATH
from src.job_parser import parse_job_details


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            link TEXT,
            by TEXT,
            role TEXT,
            location TEXT,
            posted_at TEXT,
            date_added TEXT
        )
    """)
    _migrate_role_location(conn)
    conn.commit()
    conn.close()


def _migrate_role_location(conn):
    """Add the role/location columns to pre-existing databases and backfill them."""
    c = conn.cursor()
    columns = {row[1] for row in c.execute("PRAGMA table_info(jobs)")}
    added = [name for name in ("role", "location") if name not in columns]
    for name in added:
        c.execute(f"ALTER TABLE jobs ADD COLUMN {name} TEXT")

    if not added:
        return
    for job_id, title in c.execute("SELECT id, title FROM jobs").fetchall():
        role, location = parse_job_details(title)
        c.execute("UPDATE jobs SET role=?, location=? WHERE id=?", (role, location, job_id))


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
    role, location = parse_job_details(job.get("title"))
    c.execute("""
        INSERT OR IGNORE INTO jobs (id, title, link, by, role, location, posted_at, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(job["id"]),
        job.get("title"),
        job["link"],
        job.get("by"),
        job.get("role") or role,
        job.get("location") or location,
        posted_at,
        datetime.now().strftime("%Y-%m-%d"),
    ))
    conn.commit()
    conn.close()


def get_latest_jobs(limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, title, link, by, role, location, posted_at, date_added
        FROM jobs
        ORDER BY posted_at DESC
        LIMIT ?
    """, (limit,))
    results = c.fetchall()
    conn.close()
    return results
