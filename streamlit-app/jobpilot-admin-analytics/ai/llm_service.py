import ollama


MODEL_NAME = "llama3.2"


def generate_ai_response(prompt):

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]


def generate_ai_interview_questions(
    resume_text,
    job_description,
    interview_type,
):

    prompt = f"""
You are an expert interviewer and career coach.

Generate 10 interview questions for the candidate.

Interview Type:
{interview_type}

Candidate Resume:
{resume_text}

Job Description:
{job_description}

Instructions:
1. Generate exactly 10 interview questions.
2. Use the candidate's actual resume.
3. Use the job description.
4. Do not invent candidate experience.
5. Make questions realistic and relevant.
6. Return only numbered questions.
7. Do not provide answers.
"""

    return generate_ai_response(prompt)


def generate_model_answer(
    question,
    resume_text,
    job_description,
):

    prompt = f"""
You are an expert interview coach.

Generate a strong and realistic interview answer
for the following question.

Interview Question:
{question}

Candidate Resume:
{resume_text}

Job Description:
{job_description}

Instructions:
1. Answer naturally, like a real candidate.
2. Use only information from the candidate's resume.
3. Do not invent companies, projects, skills, or experience.
4. Keep the answer clear and interview-ready.
5. Use the STAR method where appropriate.
6. Do not mention that you are an AI.
"""

    return generate_ai_response(prompt)