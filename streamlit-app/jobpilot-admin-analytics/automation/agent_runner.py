from automation.adzuna_job_search import search_adzuna_jobs
"""JobPilot background orchestration.

This module supports the safe part of the workflow:
discover -> deduplicate -> match -> rank -> save.
Portal submission must use an authorized API or a user-approved browser
session and must stop for OTP/CAPTCHA/final confirmation.
"""
import csv
import json
import os
from datetime import datetime
from pathlib import Path

from automation.job_discovery import match_job_to_resume
from automation.google_job_search import google_search_many
from automation.job_discovery import search_remote_jobs

BASE_DIR = Path(__file__).resolve().parents[1]
JOB_STORE = BASE_DIR / "data" / "jobs" / "jobs.json"


def load_jobs():
    if not JOB_STORE.exists():
        return []
    try:
        return json.loads(JOB_STORE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def save_jobs(jobs):
    JOB_STORE.parent.mkdir(parents=True, exist_ok=True)
    JOB_STORE.write_text(json.dumps(jobs, indent=2), encoding="utf-8")


def discover_and_match(resume_text, queries, location="", limit=50):
    existing = load_jobs()
    fingerprints = {row.get("fingerprint") for row in existing}
    results = []

    per_query = max(1, int(limit / max(len(queries), 1)))
    for query in queries:
        provider_jobs = search_adzuna_jobs(role, location, limit) or google_search_many([query], location, per_query) if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_CSE_ID') else search_remote_jobs(query, location, per_query)
        for job in provider_jobs:
            score, matching, missing = match_job_to_resume(
                resume_text, job.description
            )
            job.match_score = score
            job.matching_skills = ", ".join(matching)
            job.missing_skills = ", ".join(missing)
            row = job.to_dict()
            row["fingerprint"] = job.fingerprint
            row["status"] = "Found"
            if job.fingerprint not in fingerprints:
                existing.append(row)
                fingerprints.add(job.fingerprint)
            results.append(row)

    existing.sort(key=lambda item: item.get("match_score", 0), reverse=True)
    save_jobs(existing)
    return sorted(results, key=lambda item: item.get("match_score", 0), reverse=True)


def export_jobs_csv(path=None):
    rows = load_jobs()
    path = Path(path or BASE_DIR / "data" / "jobs" / "job_matches.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "title", "company", "location", "source", "url", "match_score",
        "matching_skills", "missing_skills", "status", "discovered_at"
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)
    return path
