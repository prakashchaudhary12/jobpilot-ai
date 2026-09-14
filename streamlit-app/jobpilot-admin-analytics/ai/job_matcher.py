from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_match_score(
    resume_text: str,
    job_description: str,
) -> float:
    """
    Calculate similarity between resume and job description.
    """

    if not resume_text.strip():
        return 0.0

    if not job_description.strip():
        return 0.0

    documents = [
        resume_text,
        job_description,
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(
        documents
    )

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2],
    )[0][0]

    score = round(
        similarity * 100,
        2,
    )

    return score