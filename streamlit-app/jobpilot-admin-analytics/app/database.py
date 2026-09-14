# SECURITY: user-owned records must be filtered by authenticated user_id.
from pathlib import Path

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Text,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'jobpilot.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=True, index=True)

    version_name = Column(String(200), nullable=False)

    original_filename = Column(String(300), nullable=False)

    stored_file_path = Column(String(500), nullable=False)

    file_type = Column(String(50), nullable=False)

    notes = Column(Text, nullable=True)
    
    resume_text = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=True, index=True)

    company_name = Column(
        String(200),
        nullable=False,
    )

    job_title = Column(
        String(200),
        nullable=False,
    )

    job_url = Column(
        String(500),
        nullable=True,
    )

    location = Column(
        String(200),
        nullable=True,
    )

    employment_type = Column(
        String(100),
        nullable=True,
    )

    job_description = Column(
        Text,
        nullable=False,
    )

    source = Column(
        String(100),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )    
class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=True, index=True)

    company_name = Column(
        String(200),
        nullable=False,
    )

    job_title = Column(
        String(200),
        nullable=False,
    )

    job_id = Column(
        Integer,
        nullable=True,
    )

    resume_version_id = Column(
        Integer,
        nullable=False,
    )

    resume_version_name = Column(
        String(200),
        nullable=False,
    )

    resume_file_path = Column(
        String(500),
        nullable=False,
    )

    application_date = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    status = Column(
        String(100),
        default="Applied",
        nullable=False,
    )

    job_url = Column(
        String(500),
        nullable=True,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

class InterviewPreparation(Base):
    __tablename__ = "interview_preparations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=True, index=True)

    application_id = Column(Integer, nullable=False)

    company_name = Column(String, nullable=False)

    job_title = Column(String, nullable=False)

    resume_version_id = Column(Integer, nullable=False)

    resume_version_name = Column(String, nullable=False)

    resume_file_path = Column(String, nullable=False)

    job_description = Column(Text, nullable=False)

    interview_type = Column(String, nullable=False)

    question = Column(Text, nullable=False)

    answer = Column(Text, default="")

    preparation_status = Column(
        String,
        default="Not Started",
    )
Base.metadata.create_all(bind=engine)

try:
    from app.ownership_migration import ensure_user_id_columns
    ensure_user_id_columns()
except Exception:
    pass