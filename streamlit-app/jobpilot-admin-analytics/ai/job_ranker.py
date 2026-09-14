from ai.job_matcher import calculate_match_score
from ai.skill_analyzer import analyze_skill_gap


def calculate_job_priority(
    resume_text: str,
    job_description: str,
) -> dict:
    """
    Calculate job priority using text similarity
    and skill coverage.
    """

    text_match_score = calculate_match_score(
        resume_text=resume_text,
        job_description=job_description,
    )

    skill_result = analyze_skill_gap(
        resume_text=resume_text,
        job_description=job_description,
    )

    skill_coverage = skill_result[
        "coverage_score"
    ]

    priority_score = round(
        (
            text_match_score * 0.40
        )
        +
        (
            skill_coverage * 0.60
        ),
        2,
    )

    return {
        "text_match_score": text_match_score,
        "skill_coverage": skill_coverage,
        "priority_score": priority_score,
        "matched_skills": skill_result[
            "matched_skills"
        ],
        "missing_skills": skill_result[
            "missing_skills"
        ],
    }