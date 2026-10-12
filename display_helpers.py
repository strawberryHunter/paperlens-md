"""Minimal safe presentation helpers. No global document persistence."""
import html
import re

import fitz


def marked_excerpt(excerpt: str, phrase: str) -> str:
    """Highlight a case-insensitive plain-text match while escaping PDF markup."""
    parts = re.split(f"({re.escape(phrase)})", excerpt, flags=re.IGNORECASE) if phrase else [excerpt]
    rendered = "".join(
        f"<mark>{html.escape(part)}</mark>" if phrase and part.lower() == phrase.lower()
        else html.escape(part)
        for part in parts
    )
    return f'<div class="source-sheet">{rendered}</div>'


def pdf_page_png(pdf_bytes: bytes, page_number: int, phrase: str) -> bytes:
    """Render one in-memory page and annotate matching text when found."""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        if not (1 <= page_number <= len(doc)):
            raise ValueError("PDF page outside document")
        page = doc[page_number - 1]
        if phrase:
            try:
                for rect in page.search_for(phrase)[:20]:
                    page.add_highlight_annot(rect)
            except (ValueError, RuntimeError):
                pass
        return page.get_pixmap(matrix=fitz.Matrix(1.3, 1.3), alpha=False).tobytes("png")
