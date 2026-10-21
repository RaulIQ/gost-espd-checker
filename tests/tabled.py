from docx.document import Document


def tabled(
    document: Document, caption: str, *rows: tuple[str, ...]
) -> Document:
    if caption:
        document.add_paragraph(caption)
    table = document.add_table(rows=len(rows), cols=len(rows[0]))
    for row, texts in zip(table.rows, rows, strict=True):
        for cell, text in zip(row.cells, texts, strict=True):
            cell.text = text
    return document
