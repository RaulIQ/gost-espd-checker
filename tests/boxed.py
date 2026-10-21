from docx.document import Document
from docx.oxml import parse_xml
from docx.text.paragraph import Paragraph


def boxed(document: Document, *lines: str) -> Paragraph:
    content = "".join(
        f"<w:p><w:r><w:t>{line}</w:t></w:r></w:p>" for line in lines
    )
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.element.append(
        parse_xml(
            "<w:r"
            ' xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
            ' xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"'
            ' xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"'
            ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
            ' xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"'
            ' xmlns:v="urn:schemas-microsoft-com:vml">'
            '<mc:AlternateContent><mc:Choice Requires="wps"><w:drawing>'
            "<wp:anchor><a:graphic><a:graphicData uri="
            '"http://schemas.microsoft.com/office/word/2010/wordprocessingShape">'
            f"<wps:wsp><wps:txbx><w:txbxContent>{content}</w:txbxContent>"
            "</wps:txbx></wps:wsp></a:graphicData></a:graphic></wp:anchor>"
            "</w:drawing></mc:Choice><mc:Fallback><w:pict><v:rect><v:textbox>"
            f"<w:txbxContent>{content}</w:txbxContent></v:textbox></v:rect>"
            "</w:pict></mc:Fallback></mc:AlternateContent></w:r>"
        )
    )
    return paragraph
