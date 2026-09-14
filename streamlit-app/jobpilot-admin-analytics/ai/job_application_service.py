from ai.llm_service import generate_ai_response


def generate_resume_recommendations(resume_text, job_description):
    prompt = f"""
You are an expert recruiter, ATS specialist, and resume consultant.

Compare the candidate resume with the job description.

CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide:

1. Overall match analysis
2. Match percentage estimate
3. Matching skills
4. Missing or weak skills
5. Important ATS keywords
6. Experience gaps
7. Projects that should be highlighted
8. Resume formatting recommendations
9. Specific bullet-point improvements
10. Final recommendation

Rules:
- Do not invent experience.
- Do not add fake skills.
- Do not create false achievements.
- Clearly separate existing skills from suggested skills.
- Give practical recommendations.
"""

    return generate_ai_response(prompt)


def generate_tailored_resume(resume_text, job_description):
    prompt = f"""
You are an expert professional resume writer.

Rewrite the candidate resume according to the job description.

CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Create a professional ATS-friendly resume with these sections:

1. Professional Summary
2. Technical Skills
3. Work Experience
4. Projects
5. Education
6. Certifications
7. Additional Information

Rules:
- Use only information present in the candidate resume.
- Do not invent companies, job titles, projects, achievements, or technologies.
- Do not add a skill unless it is already present in the resume.
- Improve wording and keyword alignment.
- Use strong action verbs.
- Keep the resume concise and professional.
- Do not include explanations outside the resume.
"""

    return generate_ai_response(prompt)


def generate_cover_letter(resume_text, job_description):
    prompt = f"""
Write a professional and customized job application cover letter.

CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Rules:
- Use only facts from the resume.
- Do not invent experience or achievements.
- Mention relevant skills and projects.
- Keep it professional and concise.
- Do not use fake company information.
"""

    return generate_ai_response(prompt)