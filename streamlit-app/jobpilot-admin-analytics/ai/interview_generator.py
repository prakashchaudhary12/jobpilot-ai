import re


def generate_interview_questions(
    resume_text: str,
    job_description: str,
    interview_type: str,
):
    resume_text = resume_text or ""
    job_description = job_description or ""

    combined_text = (
        resume_text + " " + job_description
    ).lower()

    questions = []

    if interview_type == "HR Interview":

        questions = [
            "Tell me about yourself.",
            "Why do you want to join our company?",
            "Why are you interested in this role?",
            "What are your strengths and weaknesses?",
            "Why should we hire you?",
            "Where do you see yourself in five years?",
            "Tell me about a difficult situation you handled.",
            "How do you handle pressure and deadlines?",
        ]

    elif interview_type == "Resume-Based Interview":

        questions = [
            "Walk me through your resume.",
            "Explain your most important project.",
            "What was your exact contribution to the project?",
            "Which technical skills have you used practically?",
            "Explain one challenge you faced in your experience.",
            "Which achievement are you most proud of?",
            "Why did you choose your technology stack?",
            "Explain your current or previous role.",
        ]

    elif interview_type == "Technical Interview":

        questions = [
            "Explain the main technical skills mentioned in your resume.",
            "Explain one machine learning or data science project.",
            "How do you handle missing values in a dataset?",
            "What is the difference between classification and regression?",
            "Explain overfitting and how to prevent it.",
            "What is the difference between SQL JOIN types?",
            "How do you evaluate a machine learning model?",
            "Explain precision, recall, and F1-score.",
        ]

        if "python" in combined_text:

            questions.append(
                "Explain Python data structures and their use cases."
            )

        if "sql" in combined_text:

            questions.append(
                "Write a SQL query to find the second-highest salary."
            )

        if "machine learning" in combined_text:

            questions.append(
                "Explain the complete machine learning project lifecycle."
            )

        if "pandas" in combined_text:

            questions.append(
                "How do you use Pandas for data cleaning and analysis?"
            )

        if "power bi" in combined_text:

            questions.append(
                "Explain how you would create a Power BI dashboard."
            )

        if "salesforce" in combined_text:

            questions.append(
                "Explain Salesforce governor limits and bulkification."
            )

    elif interview_type == "Project-Based Interview":

        questions = [
            "Explain your project architecture.",
            "What problem does your project solve?",
            "Why did you select this technology?",
            "Explain the complete project workflow.",
            "What was the biggest challenge in the project?",
            "How did you test your project?",
            "How can your project be improved?",
            "What would you do differently if you rebuilt it?",
        ]

    elif interview_type == "Job Description-Based Interview":

        questions = [
            "Why are you suitable for this job?",
            "Which skills from your resume match this job?",
            "Explain your experience with the technologies in the job description.",
            "Which required skill do you need to improve?",
            "How would you contribute during your first 90 days?",
            "Explain a project relevant to this job.",
            "How would you solve a problem related to this role?",
            "Why should the company select you?",
        ]

    else:

        questions = [
            "Explain your background and relevant experience.",
            "Why are you interested in this position?",
            "Explain one relevant project.",
            "What are your strongest technical skills?",
            "What skill are you currently improving?",
        ]

    return questions