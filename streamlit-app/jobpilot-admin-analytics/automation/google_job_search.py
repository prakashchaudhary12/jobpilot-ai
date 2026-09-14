"""Google-based job discovery using Google Custom Search JSON API."""
import os, requests
from datetime import datetime
from automation.job_discovery import DiscoveredJob

def google_job_search(query, location="", limit=50):
    api_key=os.getenv("GOOGLE_API_KEY","").strip()
    cse_id=os.getenv("GOOGLE_CSE_ID","").strip()
    if not api_key or not cse_id:
        return []
    search_query=f"{query} jobs {location}".strip()
    params={"key":api_key,"cx":cse_id,"q":search_query,
            "num":min(max(int(limit),1),10)}
    response=requests.get(
        "https://www.googleapis.com/customsearch/v1",
        params=params, timeout=30
    )
    response.raise_for_status()
    data=response.json()
    jobs=[]
    for item in data.get("items",[])[:limit]:
        jobs.append(DiscoveredJob(
            title=item.get("title",""),
            company="",
            location=location,
            source="Google",
            url=item.get("link",""),
            description=item.get("snippet",""),
            discovered_at=datetime.utcnow().isoformat()
        ))
    return jobs

def google_search_many(queries, location="", limit=50):
    results=[]
    each=max(1, min(10, int(limit/max(len(queries),1))))
    seen=set()
    for query in queries:
        for job in google_job_search(query,location,each):
            if job.url and job.url not in seen:
                seen.add(job.url); results.append(job)
    return results[:limit]
