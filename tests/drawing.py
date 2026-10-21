from docx.document import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.text.paragraph import Paragraph


def pictured(document: Document, kind: str = "picture") -> Paragraph:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.element.append(
        parse_xml(
            f"<w:r {nsdecls('w', 'wp', 'a', 'pic')}><w:drawing><wp:inline>"
            "<a:graphic><a:graphicData uri="
            f'"http://schemas.openxmlformats.org/drawingml/2006/{kind}">'
            "</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>"
        )
    )
    return paragraph
