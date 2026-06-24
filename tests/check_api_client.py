import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.hn_api import get_job_story_ids, get_item

ids = get_job_story_ids()
print(f"Fetched {len(ids)} job story ids.")
assert isinstance(ids, list), "Expected a list of ids"

if ids:
    sample_id = ids[0]
    item = get_item(sample_id)
    print(f"Sample item {sample_id}: {item}")
    assert item is not None, "Expected item details for a fresh id"
    assert item.get("type") == "job"
    print("SUCCESS: API client returned a well-formed job item.")
else:
    print("WARNING: jobstories.json returned no ids right now; cannot validate item shape.")
