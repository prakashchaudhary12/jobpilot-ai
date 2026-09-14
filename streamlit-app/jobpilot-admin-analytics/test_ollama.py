from ai.llm_service import generate_ai_response


prompt = """
Explain what a Data Analyst does in simple language.
Give 5 important responsibilities.
"""


answer = generate_ai_response(prompt)

print(answer)