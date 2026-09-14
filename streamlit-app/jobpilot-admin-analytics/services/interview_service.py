from ownership import current_user_id
from app.database import (
    SessionLocal,
    InterviewPreparation,
)


def save_interview_question(
    application_id,
    company_name,
    job_title,
    resume_version_id,
    resume_version_name,
    resume_file_path,
    job_description,
    interview_type,
    question,
):
    db = SessionLocal()

    try:

        interview_question = InterviewPreparation(
            user_id=current_user_id(),
            application_id=application_id,
            company_name=company_name,
            job_title=job_title,
            resume_version_id=resume_version_id,
            resume_version_name=resume_version_name,
            resume_file_path=resume_file_path,
            job_description=job_description,
            interview_type=interview_type,
            question=question,
            answer="",
            preparation_status="Not Started",
        )

        db.add(interview_question)
        db.commit()
        db.refresh(interview_question)

        return interview_question

    finally:

        db.close()


def get_interview_questions(application_id=None):

    db = SessionLocal()

    try:

        query = db.query(InterviewPreparation).filter(
            InterviewPreparation.user_id == current_user_id()
        )

        if application_id is not None:

            query = query.filter(
                InterviewPreparation.application_id
                == application_id,
                InterviewPreparation.user_id == current_user_id()
            )

        return query.order_by(
            InterviewPreparation.id.desc()
        ).all()

    finally:

        db.close()


def update_interview_answer(
    question_id,
    answer,
    preparation_status,
):
    db = SessionLocal()

    try:

        question = db.query(
            InterviewPreparation
        ).filter(
            InterviewPreparation.id == question_id,
            InterviewPreparation.user_id == current_user_id()
        ).first()

        if question:

            question.answer = answer

            question.preparation_status = (
                preparation_status
            )

            db.commit()

        return question

    finally:

        db.close()


def delete_interview_question(question_id):

    db = SessionLocal()

    try:

        question = db.query(
            InterviewPreparation
        ).filter(
            InterviewPreparation.id == question_id,
            InterviewPreparation.user_id == current_user_id()
        ).first()

        if question:

            db.delete(question)
            db.commit()

            return True

        return False

    finally:

        db.close()