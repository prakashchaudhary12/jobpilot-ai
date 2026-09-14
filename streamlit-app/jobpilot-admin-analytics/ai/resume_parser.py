from pathlib import Path



import fitz
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF resume.
    """

    document = fitz.open(file_path)

    extracted_text = []

    for page in document:
        page_text = page.get_text()

        if page_text:
            extracted_text.append(page_text)

    document.close()

    return "\n".join(extracted_text).strip()


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX resume.
    """

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():
            paragraphs.append(
                paragraph.text.strip()
            )

    return "\n".join(paragraphs).strip()


def extract_resume_text(file_path: str) -> str:
    """
    Detect file type and extract resume text.
    """

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":

        return extract_text_from_pdf(file_path)

    elif extension == ".docx":

        return extract_text_from_docx(file_path)

    else:

        raise ValueError(
            "Only PDF and DOCX files are supported."
        )