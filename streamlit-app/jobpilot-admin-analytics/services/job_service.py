from ownership import current_user_id
from app.database import SessionLocal, Job


def save_job(
    company_name: str,
    job_title: str,
    job_url: str,
    location: str,
    employment_type: str,
    job_description: str,
    source: str,
):
    db = SessionLocal()

    try:

        job = Job(
            user_id=current_user_id(),
            company_name=company_name,
            job_title=job_title,
            job_url=job_url,
            location=location,
            employment_type=employment_type,
            job_description=job_description,
            source=source,
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return job

    finally:

        db.close()


def get_all_jobs():
    db = SessionLocal()

    try:

        jobs = (
            db.query(Job)
            .filter(Job.user_id == current_user_id())
            .order_by(
                Job.created_at.desc()
            )
            .all()
        )

        return jobs

    finally:

        db.close()