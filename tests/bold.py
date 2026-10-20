from docx.document import Document
from docx.text.paragraph import Paragraph


def bold(document: Document, text: str) -> Paragraph:
    paragraph = document.add_paragraph()
    paragraph.add_run(text).bold = True
    return paragraph
