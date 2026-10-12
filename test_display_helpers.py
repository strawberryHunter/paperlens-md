"""UI utility security and PDF rendering regression tests."""
import fitz
import pytest
from display_helpers import marked_excerpt, pdf_page_png


def test_excerpt_highlights_case_insensitively():
    result = marked_excerpt("We used GROMACS 2024.1.", "gromacs 2024.1")
    assert "<mark>GROMACS 2024.1</mark>" in result


def test_pdf_markup_is_html_escaped():
    result = marked_excerpt('<img src=x onerror=alert(1)> TIP3P', 'TIP3P')
    assert '<img' not in result
    assert '&lt;img' in result
    assert '<mark>TIP3P</mark>' in result


def test_pdf_page_renderer_png_and_bounds():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), 'CHARMM36m TIP3P GROMACS 2024.1')
    document_bytes = doc.tobytes()
    doc.close()
    output = pdf_page_png(document_bytes, 1, 'CHARMM36m')
    assert output.startswith(b'\x89PNG\r\n\x1a\n')
    with pytest.raises(ValueError):
        pdf_page_png(document_bytes, 2, 'CHARMM36m')
