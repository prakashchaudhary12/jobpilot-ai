from ownership import current_user_id
from pathlib import Path
from datetime import datetime
from uuid import uuid4

from app.database import SessionLocal, ResumeVersion
from ai.resume_parser import extract_resume_text


BASE_DIR = Path(__file__).resolve().parent.parent
RESUME_DIR = BASE_DIR / "data" / "resumes"

RESUME_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def save_resume_version(
    uploaded_file,
    version_name: str,
    notes: str = "",
):
    original_filename = uploaded_file.name

    file_extension = Path(
        original_filename
    ).suffix.lower()

    unique_filename = (
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
        f"{uuid4().hex[:8]}"
        f"{file_extension}"
    )

    stored_file_path = RESUME_DIR / unique_filename

    with open(stored_file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    db = SessionLocal()

    try:
        resume_text = extract_resume_text(
            str(stored_file_path)
        )

        resume = ResumeVersion(
            user_id=current_user_id(),
            version_name=version_name,
            original_filename=original_filename,
            stored_file_path=str(stored_file_path),
            file_type=file_extension,
            notes=notes,
            resume_text=resume_text,
        )
        
        

        db.add(resume)
        db.commit()
        db.refresh(resume)

        return resume

    finally:
        db.close()


def get_all_resume_versions():
    db = SessionLocal()

    try:
        resumes = (
            db.query(ResumeVersion)
            .filter(ResumeVersion.user_id == current_user_id())
            .order_by(
                ResumeVersion.created_at.desc()
            )
            .all()
        )

        return resumes

    finally:
        db.close()