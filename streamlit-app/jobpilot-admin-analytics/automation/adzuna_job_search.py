"""
Adzuna job-search integration.
Uses ADZUNA_APP_ID and ADZUNA_APP_KEY from environment variables.
"""
import os
import requests
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AdzunaJob:
    title: str
    company: str
    location: str
    source: str
    url: str
    description: str = ""
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None


def search_adzuna_jobs(
    role: str,
    location: str = "India",
    results_per_page: int = 20,
    country: str = "in",
) -> List[AdzunaJob]:
    app_id = os.getenv("ADZUNA_APP_ID", "").strip()
    app_key = os.getenv("ADZUNA_APP_KEY", "").strip()

    if not app_id or not app_key:
        return []

    results_per_page = max(1, min(int(results_per_page), 50))
    page = 1
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": role,
        "where": location,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    jobs = []
    for item in payload.get("results", []):
        company = (item.get("company") or {}).get("display_name", "")
        area = item.get("location") or {}
        location_text = ", ".join(area.get("display_name", "").split(", ")[:3])

        jobs.append(
            AdzunaJob(
                title=item.get("title", ""),
                company=company,
                location=location_text or location,
                source="Adzuna",
                url=item.get("redirect_url", ""),
                description=item.get("description", ""),
                salary_min=item.get("salary_min"),
                salary_max=item.get("salary_max"),
            )
        )

    return jobs
