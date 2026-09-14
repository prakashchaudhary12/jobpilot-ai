import re


SKILL_LIBRARY = [
    "python",
    "sql",
    "excel",
    "power bi",
    "tableau",
    "pandas",
    "numpy",
    "scikit-learn",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "statistics",
    "data analysis",
    "data visualization",
    "etl",
    "data cleaning",
    "data transformation",
    "tensorflow",
    "pytorch",
    "keras",
    "nlp",
    "natural language processing",
    "rag",
    "llm",
    "generative ai",
    "aws",
    "azure",
    "google cloud",
    "git",
    "salesforce",
    "apex",
    "power query",
    "dax",
]


def normalize_text(text: str) -> str:
    """
    Convert text to lowercase and normalize spaces.
    """

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def extract_skills(text: str) -> list[str]:
    """
    Extract known skills from text.
    """

    normalized_text = normalize_text(text)

    found_skills = []

    for skill in SKILL_LIBRARY:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(
            pattern,
            normalized_text,
        ):

            found_skills.append(skill)

    return sorted(found_skills)


def analyze_skill_gap(
    resume_text: str,
    job_description: str,
) -> dict:
    """
    Compare resume skills with job-required skills.
    """

    resume_skills = set(
        extract_skills(resume_text)
    )

    job_skills = set(
        extract_skills(job_description)
    )

    matched_skills = sorted(
        resume_skills.intersection(
            job_skills
        )
    )

    missing_skills = sorted(
        job_skills.difference(
            resume_skills
        )
    )

    if job_skills:

        coverage_score = round(
            (
                len(matched_skills)
                / len(job_skills)
            ) * 100,
            2,
        )

    else:

        coverage_score = 0.0

    return {
        "resume_skills": sorted(
            resume_skills
        ),
        "job_skills": sorted(
            job_skills
        ),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "coverage_score": coverage_score,
    }