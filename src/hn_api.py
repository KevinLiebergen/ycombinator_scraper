import logging
import time

import requests

from config.settings import (
    HN_JOB_STORIES_URL,
    HN_ITEM_URL_TEMPLATE,
    REQUEST_TIMEOUT,
    REQUEST_RETRIES,
    REQUEST_BACKOFF,
)

logger = logging.getLogger(__name__)


def _get_with_retries(url):
    """GET a URL with simple retry/backoff. Returns parsed JSON or None on failure."""
    last_exc = None
    for attempt in range(1, REQUEST_RETRIES + 1):
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as ex:
            last_exc = ex
            logger.warning(
                "Request failed (attempt %d/%d) for %s: %s",
                attempt, REQUEST_RETRIES, url, ex,
            )
            if attempt < REQUEST_RETRIES:
                time.sleep(REQUEST_BACKOFF * attempt)
    logger.error("Giving up on %s after %d attempts: %s", url, REQUEST_RETRIES, last_exc)
    return None


def get_job_story_ids():
    """Fetch the current list of HN job story IDs (newest first). Returns [] on failure."""
    data = _get_with_retries(HN_JOB_STORIES_URL)
    if data is None:
        return []
    if not isinstance(data, list):
        logger.error("Unexpected jobstories response shape: %r", type(data))
        return []
    return data


def get_item(item_id):
    """Fetch full item details for a single HN id. Returns None on failure or if absent."""
    url = HN_ITEM_URL_TEMPLATE.format(id=item_id)
    data = _get_with_retries(url)
    if data is None:
        logger.warning("Item %s could not be fetched, skipping.", item_id)
        return None
    if data.get("deleted") or data.get("dead"):
        logger.info("Item %s is deleted/dead, skipping.", item_id)
        return None
    return data
