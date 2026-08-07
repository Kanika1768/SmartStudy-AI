import pymupdf
import os

def load_pdf(pdf_path):
    """
    Reads a PDF page by page.

    Returns:
    [
        {
            "text": "...",
            "page": 1,
            "document": "OS.pdf"
        }
    ]
    """

    document = pymupdf.open(pdf_path)

    pages = []

    filename = os.path.basename(pdf_path)

    for page_num, page in enumerate(document, start=1):

        text = page.get_text("text").strip()

        if text:

            pages.append({

                "text": text,

                "page": page_num,

                "document": filename

            })

    return pages