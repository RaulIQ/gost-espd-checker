from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Mm
from hamcrest import assert_that, equal_to, is_

from gost_espd_checker.effective import Effective
from gost_espd_checker.lineage import Lineage


def test_reads_alignment_of_paragraph() -> None:
    paragraph = Document().add_paragraph("Состав программы")
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
    assert_that(
        Effective(Lineage(paragraph)).alignment(),
        equal_to(WD_PARAGRAPH_ALIGNMENT.RIGHT),
        "alignment of the paragraph was not read",
    )


def test_inherits_alignment_through_base_style() -> None:
    document = Document()
    document.styles[
        "Normal"
    ].paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    assert_that(
        Effective(
            Lineage(document.add_paragraph("ОБЩИЕ СВЕДЕНИЯ", style="Heading 1"))
        ).alignment(),
        equal_to(WD_PARAGRAPH_ALIGNMENT.CENTER),
        "alignment was not inherited through the base style",
    )


def test_aligns_left_without_any_alignment() -> None:
    assert_that(
        Effective(
            Lineage(Document().add_paragraph("Связи программ"))
        ).alignment(),
        equal_to(WD_PARAGRAPH_ALIGNMENT.LEFT),
        "paragraph without alignment was not aligned left",
    )


def test_inherits_first_line_indent_from_style() -> None:
    document = Document()
    document.styles["Heading 2"].paragraph_format.first_line_indent = Mm(12.5)
    assert_that(
        Effective(
            Lineage(
                document.add_paragraph("Установка программы", style="Heading 2")
            )
        )
        .indent()
        .twips,
        equal_to(Mm(12.5).twips),
        "first line indent was not inherited from the style",
    )


def test_gives_zero_indent_without_any_indent() -> None:
    assert_that(
        Effective(
            Lineage(Document().add_paragraph("Условия проверки"))
        ).indent(),
        equal_to(0),
        "paragraph without indent did not get a zero indent",
    )


def test_allows_hyphenation_by_default() -> None:
    assert_that(
        Effective(
            Lineage(Document().add_paragraph("Контрольный пример"))
        ).hyphenation(),
        is_(True),
        "hyphenation was not allowed by default",
    )


def test_sees_hyphenation_suppressed_by_style() -> None:
    document = Document()
    document.styles["Heading 2"].element.get_or_add_pPr().append(
        parse_xml(f"<w:suppressAutoHyphens {nsdecls('w')}/>")
    )
    assert_that(
        Effective(
            Lineage(
                document.add_paragraph("Сообщения журнала", style="Heading 2")
            )
        ).hyphenation(),
        is_(False),
        "hyphenation suppressed by the style was not seen",
    )


def test_lets_paragraph_turn_hyphenation_back_on() -> None:
    document = Document()
    document.styles["Heading 2"].element.get_or_add_pPr().append(
        parse_xml(f"<w:suppressAutoHyphens {nsdecls('w')}/>")
    )
    paragraph = document.add_paragraph("Состав программы", style="Heading 2")
    paragraph.paragraph_format.element.get_or_add_pPr().append(
        parse_xml(f'<w:suppressAutoHyphens {nsdecls("w")} w:val="0"/>')
    )
    assert_that(
        Effective(Lineage(paragraph)).hyphenation(),
        is_(True),
        "paragraph did not turn hyphenation back on",
    )


def test_takes_page_break_before_from_style() -> None:
    document = Document()
    document.styles["Heading 1"].paragraph_format.page_break_before = True
    assert_that(
        Effective(
            Lineage(document.add_paragraph("ОБЩИЕ СВЕДЕНИЯ", style="Heading 1"))
        ).pagebreak(),
        is_(True),
        "page break before was not taken from the style",
    )


def test_lets_paragraph_cancel_page_break_of_style() -> None:
    document = Document()
    document.styles["Heading 1"].paragraph_format.page_break_before = True
    paragraph = document.add_paragraph("ОБЩИЕ СВЕДЕНИЯ", style="Heading 1")
    paragraph.paragraph_format.page_break_before = False
    assert_that(
        Effective(Lineage(paragraph)).pagebreak(),
        is_(False),
        "paragraph did not cancel the page break of its style",
    )


def test_reads_end_alignment_as_right() -> None:
    paragraph = Document().add_paragraph("Литера опытного образца")
    paragraph.paragraph_format.element.get_or_add_pPr().append(
        parse_xml(f'<w:jc {nsdecls("w")} w:val="end"/>')
    )
    assert_that(
        Effective(Lineage(paragraph)).alignment(),
        equal_to(WD_PARAGRAPH_ALIGNMENT.RIGHT),
        "end alignment was not read as right",
    )


def test_reads_start_alignment_of_style_as_left() -> None:
    document = Document()
    document.styles["Heading 1"].element.get_or_add_pPr().append(
        parse_xml(f'<w:jc {nsdecls("w")} w:val="start"/>')
    )
    assert_that(
        Effective(
            Lineage(document.add_paragraph("ОБЩИЕ СВЕДЕНИЯ", style="Heading 1"))
        ).alignment(),
        equal_to(WD_PARAGRAPH_ALIGNMENT.LEFT),
        "start alignment of the style was not read as left",
    )


def test_measures_left_indent_as_start_of_first_line() -> None:
    paragraph = Document().add_paragraph("1) настройка зарядного устройства")
    paragraph.paragraph_format.left_indent = Mm(12.5)
    assert_that(
        Effective(Lineage(paragraph)).indent().twips,
        equal_to(Mm(12.5).twips),
        "left indent was not measured as the start of the first line",
    )


def test_subtracts_hanging_indent_from_left_indent() -> None:
    paragraph = Document().add_paragraph("— передача телеметрии")
    paragraph.paragraph_format.left_indent = Mm(20)
    paragraph.paragraph_format.first_line_indent = Mm(-7.5)
    assert_that(
        Effective(Lineage(paragraph)).indent().twips,
        equal_to(Mm(12.5).twips),
        "hanging indent was not subtracted from the left indent",
    )


def test_combines_left_indent_of_style_with_hanging_of_paragraph() -> None:
    document = Document()
    document.styles["Normal"].paragraph_format.left_indent = Mm(20)
    paragraph = document.add_paragraph("2) прием команд управления")
    paragraph.paragraph_format.first_line_indent = Mm(-20)
    assert_that(
        Effective(Lineage(paragraph)).indent(),
        equal_to(0),
        "left indent of the style was not combined with the hanging indent",
    )
