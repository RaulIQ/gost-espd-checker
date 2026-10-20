from docx.section import Section
from docx.shared import Mm


def conforming(section: Section) -> Section:
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(25)
    section.left_margin = Mm(20)
    section.right_margin = Mm(10)
    section.bottom_margin = Mm(15)
    return section
