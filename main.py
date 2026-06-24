import argparse
import logging

from src.crawler import crawl
from src.notifier import send_new_jobs
from src.database import init_db, get_latest_jobs


def main(verbose=False, list_jobs=False):
    init_db()

    if list_jobs:
        jobs = get_latest_jobs()
        print(f"Last {len(jobs)} jobs found:\n")
        for job_id, title, link, by, posted_at, date_added in jobs:
            print(f"[{job_id}] {title}")
            print(f"   by {by} | posted {posted_at} | added {date_added}")
            print(f"   {link}\n")
        return

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    logger.info("Checking Hacker News job stories...")
    try:
        new_jobs, is_first_run = crawl()
    except Exception as ex:
        logger.error("Unhandled error during crawl: %s", ex, exc_info=verbose)
        return

    if not new_jobs:
        logger.info("No new jobs found.")
        return

    if is_first_run:
        logger.info(
            "First run: stored %d job(s) as baseline, no notifications sent.",
            len(new_jobs),
        )
        return

    logger.info("Found %d new job(s), sending Telegram notifications...", len(new_jobs))
    send_new_jobs(new_jobs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hacker News / YC job stories monitor")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose (DEBUG) logging")
    parser.add_argument("--list", "-l", action="store_true", help="List last 10 jobs found and exit")
    args = parser.parse_args()
    main(verbose=args.verbose, list_jobs=args.list)
