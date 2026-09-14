from ai.llm_service import generate_ai_response


def improve_resume_for_job(
    resume_text,
    job_description,
):

    prompt = f"""
You are an expert resume writer and ATS optimization specialist.

Analyze the candidate resume against the job description.

Candidate Resume:
{resume_text}

Job Description:
{job_description}

Provide the following sections:

1. Overall Resume Analysis
2. Missing Skills
3. Important ATS Keywords
4. Weak Resume Points
5. Suggested Improvements
6. Improved Resume Bullet Points
7. Final Recommendations

Rules:
- Use only the candidate's actual experience.
- Do not invent companies, projects, achievements, or skills.
- Do not add false information.
- Make suggestions specific to the job description.
- Keep the response clear and practical.
"""

    return generate_ai_response(prompt)