from ownership import current_user_id
from app.database import (
    SessionLocal,
    Application,
)


def save_application(
    company_name: str,
    job_title: str,
    job_id: int,
    resume_version_id: int,
    resume_version_name: str,
    resume_file_path: str,
    status: str,
    job_url: str = "",
    notes: str = "",
):
    db = SessionLocal()

    try:
        application = Application(
            user_id=current_user_id(),
            company_name=company_name,
            job_title=job_title,
            job_id=job_id,
            resume_version_id=resume_version_id,
            resume_version_name=resume_version_name,
            resume_file_path=resume_file_path,
            status=status,
            job_url=job_url,
            notes=notes,
        )

        db.add(application)
        db.commit()
        db.refresh(application)

        return application

    finally:
        db.close()


def get_all_applications():
    db = SessionLocal()

    try:
        applications = (
            db.query(Application)
            .filter(Application.user_id == current_user_id())
            .order_by(
                Application.created_at.desc()
            )
            .all()
        )

        return applications

    finally:
        db.close()


def update_application_status(
    application_id: int,
    new_status: str,
):
    db = SessionLocal()

    try:
        application = (
            db.query(Application)
            .filter(
                Application.id == application_id,
                Application.user_id == current_user_id()
            )
            .first()
        )

        if application:
            application.status = new_status

            db.commit()
            db.refresh(application)

        return application

    finally:
        db.close()


def delete_application(
    application_id: int,
):
    db = SessionLocal()

    try:
        application = (
            db.query(Application)
            .filter(
                Application.id == application_id,
                Application.user_id == current_user_id()
            )
            .first()
        )

        if application:
            db.delete(application)
            db.commit()

        return application

    finally:
        db.close()