"""Safe job-discovery service.

This module provides a provider-neutral interface. Portal-specific connectors
must use official APIs or user-approved browser sessions and must respect each
portal's terms, rate limits, CAPTCHA and OTP requirements.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List
import hashlib
import re
import os
import requests


@dataclass
class DiscoveredJob:
    title: str
    company: str
    location: str = ""
    source: str = ""
    url: str = ""
    description: str = ""
    employment_type: str = ""
    match_score: float = 0.0
    matching_skills: str = ""
    missing_skills: str = ""
    discovered_at: str = ""

    def to_dict(self):
        return asdict(self)

    @property
    def fingerprint(self):
        raw = f"{self.title}|{self.company}|{self.url}".lower()
        return hashlib.sha256(raw.encode()).hexdigest()


def extract_skills(text: str):
    vocabulary = [
        "python", "sql", "excel", "power bi", "tableau", "statistics",
        "pandas", "numpy", "scikit-learn", "salesforce", "apex",
        "soql", "javascript", "java", "aws", "azure", "machine learning",
        "data analysis", "data visualization", "etl", "git", "jira"
    ]
    text = (text or "").lower()
    return sorted({skill for skill in vocabulary if skill in text})


def match_job_to_resume(resume_text: str, job_description: str):
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description))
    if not job_skills:
        return 0.0, [], []
    matching = sorted(resume_skills & job_skills)
    missing = sorted(job_skills - resume_skills)
    score = round((len(matching) / len(job_skills)) * 100, 2)
    return score, matching, missing


def search_remote_jobs(query: str, location: str = "", limit: int = 50) -> List[DiscoveredJob]:
    """Search a configurable public job-search endpoint.

    Set JOB_SEARCH_API_URL and JOB_SEARCH_API_KEY in .env only when using a
    provider that authorizes this use. Without configuration, returns [].
    """
    api_url = os.getenv("JOB_SEARCH_API_URL")
    api_key = os.getenv("JOB_SEARCH_API_KEY")
    if not api_url:
        return []

    params = {"query": query, "location": location, "limit": min(int(limit), 100)}
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    response = requests.get(api_url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("jobs", payload if isinstance(payload, list) else [])

    jobs = []
    for row in rows[:limit]:
        jobs.append(DiscoveredJob(
            title=row.get("title", ""),
            company=row.get("company", row.get("company_name", "")),
            location=row.get("location", location),
            source=row.get("source", "API"),
            url=row.get("url", row.get("job_url", "")),
            description=row.get("description", row.get("job_description", "")),
            employment_type=row.get("employment_type", ""),
            discovered_at=datetime.utcnow().isoformat(),
        ))
    return jobs
