# ycombinator_scrapper

Monitors Hacker News' Jobs feed (which is how YC company job postings surface) and sends a
Telegram notification whenever a new job posting appears. Designed to be triggered periodically
by cron — it is a one-shot script, not a long-running daemon.

## How it works

1. Fetches the current list of job story IDs from
   `https://hacker-news.firebaseio.com/v0/jobstories.json`.
2. For any ID not already stored locally, fetches full details from
   `https://hacker-news.firebaseio.com/v0/item/{id}.json` and saves them to a local SQLite
   database.
3. Sends a Telegram message for each newly discovered job.

### First-run behavior

**The very first run is a silent baseline.** On an empty database, all currently listed job IDs
are stored, but no Telegram notifications are sent (otherwise you'd get ~30-200 messages at once).
From the second run onward, only genuinely new job IDs trigger a notification.

## Installation

A dedicated conda environment (matching job_tracker's per-project setup) is used:

```bash
cd ycombinator_scrapper
conda create -n ycombinator_scrapper python=3.12 -y
conda activate ycombinator_scrapper
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in your own values:

```bash
cp .env.example .env
```

```
TELEGRAM_TOKEN=<your bot token, from @BotFather>
TELEGRAM_CHAT_ID=<your chat id>
DB_PATH=data/jobs.db
TELEGRAM_MESSAGE_DELAY=3   # seconds between consecutive Telegram messages, to avoid rate limits
```

`.env` is gitignored and never committed.

## Usage

```bash
python main.py            # check for new jobs, notify on Telegram if any are found
python main.py -v         # same, with verbose/debug logging
python main.py --list     # print the last 10 stored jobs and exit (no network calls)
```

## Automating with cron

Run once a day, e.g. at 9am, and log output for troubleshooting:

```cron
0 9 * * * /home/kevinvanliebergen/miniconda3/envs/ycombinator_scrapper/bin/python3 /home/kevinvanliebergen/git/ycombinator_scrapper/main.py >> /home/kevinvanliebergen/git/ycombinator_scrapper/cron.log 2>&1
```

Edit with `crontab -e`. Use absolute paths — cron's `PATH` and environment are minimal, so test
the exact command manually before relying on it.

## Testing

Lightweight manual scripts (no pytest, matching job_tracker's style):

```bash
python tests/check_api_client.py     # hits the live HN API
python tests/check_db_roundtrip.py   # exercises SQLite logic against a throwaway DB
```

## Database schema

```sql
CREATE TABLE jobs (
    id         TEXT PRIMARY KEY,
    title      TEXT,
    link       TEXT,
    by         TEXT,
    posted_at  TEXT,
    date_added TEXT
)
```
