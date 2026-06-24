import logging

from config.settings import HN_DISCUSSION_URL_TEMPLATE
from src.hn_api import get_job_story_ids, get_item
from src.database import has_any_jobs, job_exists, save_job

logger = logging.getLogger(__name__)


def resolve_link(item):
    url = item.get("url")
    if url:
        return url
    return HN_DISCUSSION_URL_TEMPLATE.format(id=item["id"])


def build_job_record(item):
    return {
        "id": item["id"],
        "title": item.get("title") or "(untitled)",
        "link": resolve_link(item),
        "by": item.get("by"),
        "time": item.get("time"),
    }


def crawl():
    """
    Fetch current HN job story IDs, persist any not already seen.
    Returns (new_jobs, is_first_run):
      - new_jobs: list of job dicts that were newly inserted this run
      - is_first_run: True if the DB was empty before this run (caller should
        suppress notifications for new_jobs in that case)
    """
    is_first_run = not has_any_jobs()
    if is_first_run:
        logger.info("Database is empty - this is the first run, baseline will be silent.")

    story_ids = get_job_story_ids()
    if not story_ids:
        logger.warning("No job story IDs fetched (empty list or API failure). Nothing to do.")
        return [], is_first_run

    logger.info("Fetched %d job story IDs from HN.", len(story_ids))

    new_jobs = []
    for job_id in story_ids:
        if job_exists(job_id):
            continue

        item = get_item(job_id)
        if item is None:
            continue
        if item.get("type") != "job":
            logger.debug("Item %s is type=%s, not 'job', skipping.", job_id, item.get("type"))
            continue

        job = build_job_record(item)
        save_job(job)
        new_jobs.append(job)
        logger.info("New job saved: [%s] %s", job["id"], job["title"])

    return new_jobs, is_first_run
