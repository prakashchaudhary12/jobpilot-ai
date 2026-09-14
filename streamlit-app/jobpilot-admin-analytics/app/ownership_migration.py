from sqlalchemy import text
from app.database import engine

TABLES = [
    "resume_versions",
    "jobs",
    "applications",
    "interview_preparations",
]

def ensure_user_id_columns():
    with engine.begin() as conn:
        for table in TABLES:
            columns = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
            names = {row[1] for row in columns}
            if "user_id" not in names:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER"))
                conn.execute(text(
                    f"CREATE INDEX IF NOT EXISTS ix_{table}_user_id ON {table}(user_id)"
                ))
