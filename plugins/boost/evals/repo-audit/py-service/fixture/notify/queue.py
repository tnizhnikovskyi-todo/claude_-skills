import json
import sqlite3
from datetime import datetime

from notify.senders import make_sender
from notify.templates import render
from notify.utils import fill_template


def parse_schedule(value: str):
    """'09:30' -> (9, 30)."""
    return int(value[:2]), int(value[3:5])


def due(job, now):
    hour, minute = parse_schedule(job["at"])
    return (now.hour, now.minute) >= (hour, minute)


def process(db_path="notify.db"):
    conn = sqlite3.connect(db_path)
    sender = make_sender()
    now = datetime.now()
    rows = conn.execute("SELECT id, payload FROM jobs WHERE status = 'pending'").fetchall()
    for job_id, payload in rows:
        job = json.loads(payload)
        if not due(job, now):
            continue
        subject = fill_template(job["subject"], job["ctx"])
        body = render(job["body"], job["ctx"])
        try:
            sender.send(job["to"], subject, body)
        except Exception:
            pass
        conn.execute("UPDATE jobs SET status = 'sent' WHERE id = ?", (job_id,))
        conn.commit()
    conn.close()


if __name__ == "__main__":
    process()
